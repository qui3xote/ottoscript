# OttoScript

## What is OttoScript?
`OttoScript` is a toolkit for parsing OttoScript files (*.otto) into python objects which can then be used to run home automations. 

## Installing ottoscript
Installation is simply a matter of checking out the code from github. (For instructions on how to run this on HomeAssistant, see [ottopyscript](https://github.com/qui3xote/ottopyscript)

# The Language
Ottoscript is inspired by SQL - it aims to provide an intuitive and human-readable language for creating automations with minimal syntax. Whitespace, line breaks, indentations and capitalization are all ignored (but are recommended for readability). Here is a simple example:

```
WHEN input_boolean.sleep CHANGES TO 'on'
  IF person.tom IS 'home'
   THEN
     TURN OFF lights.porch_sconce_lights
     LOCK lock.entry
  END
```

An automation specifies a trigger (`WHEN`) and a control structure (`IF` `THEN`) for deciding what conditions (`person.tom IS 'home'`) must be met before a sequence of commands are executed ```TURN OFF lights.porch_sconce_lights
     LOCK lock.entry```

### WHEN
All automations begin with a WHEN clause, which specifies an event (aka 'trigger') that must occur before the rest of the script is run:

WHEN _entity_ CHANGES (FROM _state_) (TO _state_) 
`FROM` and `TO` are optional, but must be in the order above if both are used, multiple triggers may be strung together with `OR`. 

Example ```WHEN person.tom CHANGES TO 'home' or person.mywife CHANGES TO 'home'```

A WHEN clause must be followed by one or more control structures (CASE and IF/THEN/ELSE are currently supported). All control structures are evaluated regardless of whether the prior succeeded or failed. (NB: This is unlike HA, where any failed condition will stop the remaining actions).

### IF
IF _entity_ [operand] _value_ (AND | OR | NOT) (_condition_) ... END

Supported operands include standard mathematical notations ('=','<','>', etc) and `IS`.  Multiple conditions can be strung together using `AND`, `OR` and `NOT`, and parentheses can be used to control the order of evaluation. 

**EXAMPLE** 
```
IF light.office_lights:brightness_pct < 50 
  AND (binary_sensor.office_occupied = 'on' OR input_boolean.keep_the_lights_on IS 'on')
    THEN DIM light.office_lights to 100%
    ELSE TURN OFF light.office_lights 
  END
```

### THEN
(THEN) _command_ | _condition_

THEN must be followed by one or more commands or conditions, meaning that you can have nested logic (see example below). All commands are run in sequence, and all are executed regardless of whether or not the prior commands succeed. As of v0.2, the actual keyword THEN is optional. 

**EXAMPLE**
```
THEN
  TURN ON lights.main_lights
  IF input_boolean.vacation_mode == 'off'
    UNLOCK lock.front_door_lock
 ```

### CASE
CASE IF _condition_ THEN _command_ END (ELSE _condition_ | _command_) END

CASE operates similarly to HA 'choose' - IF/THEN statements are evaluated in order, and only the first true condition is executed. In the event that none of them are true, there is an optional 'ELSE' statement which is run. Note that `ELSE` statements are not allowed inside the CASE IF/THENS - only at the end.

**EXAMPLE**
```
CASE
  IF input_boolean.guest_mode == 'on'
    CALL automation.trigger ON automation.welcome_guests
  END
  IF input_boolean.guest_mode == 'off'
    CALL automation.trigger ON automation.welcome_family
  END
  ELSE
    LOCK lock.front_door_lock
    CALL automation.trigger ON automation.intruder_alert
  END
```

### Commands

Supported commands currently include:

TURN ON/OFF _entity_
TOGGLE _entity_
DIM _light.entity_ (TO | BY)  (_number_ | _percent_)
LOCK/UNLOCK _lock.entity_ (WITH (code=_code_))
CALL _domain.servicename_ ON _entity_ (WITH (param1=_value_, param2=_value2_...))
SET _entity_ (TO | =) _value_ 
WAIT _number_ (SECONDS | MINUTES | HOURS)
PASS 

The CALL command allows you to call any service currently supported by HA, so in theory you never need the other commands, but they are 
useful shortcuts - future versions will add more.

### Variables
As of v0.2, OttoScript supports variables! Variables can be assigned as part of any THEN block, and read in any subsequent command or conditions. Variables are denoted with the `@` symbol.

**EXAMPLE**
```
WHEN input_select.home_mode CHANGES
  CASE
    IF imput_select.home_mode == 'evening'
      @brightness = 50%
    END
    IF imput_select.home_mode == 'sleep'
      @brightness = 30%
    END
    DIM lights.porch_lights to @brightness
```


# Extending the Language
OttoScript relies on PyParsing and heavy use of subclassing to handle the dirty work of parsing scripts into usable objects. `vocab.py` establishes a few key primitives as simple pyparsing object (digits, identifiers, etc) and establishes the BaseVocab class from which everything else inherits. 
A standard OttoScript class includes a `_parser` class attribute which defines the grammar, and a class method `parser()`, which returns a pyparsing object, which will in turn return an instance of the class. In this way, you can build more complex structures by relying on existing grammar. 

### Interpreter
`interpreter.py` contains an ExampleInterpreter which can be used for testing and debugging. (A 'live' interpreter can by found in the `ottopyscript` repository). The interpreter is responsible for translating OttoScript commands into live instructions to HASS (or, if someone wants to write one, a different home automation controller).

### vocab.py
In addition to the base class and primitives, the `vocab` module defines smaller, reusable OttoScript snippets, such as the `RelativeTime` class:

```
class RelativeTime(BaseVocab):
    _parser = Numeric.parser()("_count") + (Hour.parser() | Minute.parser() | Second.parser())("_unit")

    @property
    def seconds(self):
        return self._count.value * self._unit.seconds
```

### Adding a Command
Commands require only a parser and a async `eval` function which issues commands to the interpreter:
```
class Toggle(BaseCommand):
    _kwd = CaselessKeyword("TOGGLE")
    _parser = _kwd + Entity.parser()("_entity")

    async def eval(self, interpreter):
        servicename = 'toggle'
        kwargs = {'entity_id': self._entity.name}
        result = await interpreter.call_service(self._entity.domain, servicename, kwargs)
        return result
```

### Conditionals
Control structures (such as `IF`) are housed in conditionals. The `eval` function is responsible for evaluating the contained conditions and returning True or False. 

