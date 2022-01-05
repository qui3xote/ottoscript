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
```

An automation specifies a trigger (`WHEN`) and a control structure (`IF` `THEN`) for deciding what conditions (`person.tom IS 'home'`) must be met before a sequence of commands are executed ```TURN OFF lights.porch_sconce_lights
     LOCK lock.entry```

### WHEN
All automations begin with a WHEN clause, which specifies an event (aka 'trigger') that must occur before the rest of the script is run:

WHEN _entity_ CHANGES (FROM _state_) (TO _state_) 
`FROM` and `TO` are optional, but must be in the order above if both are used, multiple triggers may be strung together with `OR`. 

Example ```WHEN person.tom CHANGES TO 'home' or person.mywife CHANGES TO 'home'```

A WHEN clause must be followed by one or more control structures (currently only if/then is supported). All control structures are evaluated regardless of whether the prior succeeded or failed. 
### IF
IF _entity_ [operand] [value] (AND | OR | NOT) (_condition_)

Supported operands include standard mathematical notations ('=','<','>', etc) and `IS`.  Multiple conditions can be strung together using `AND`, `OR` and `NOT`, and parentheses can be used to control the order of evaluation. 

Example ```IF light.office_lights:brightness_pct < 50 AND (binary_sensor.office_occupied = 'on' OR input_boolean.keep_the_lights_on IS 'on')```

### THEN
THEN _command_

THEN must be followed by one or more commands. All commands are run in sequence, and all are executed regardless of whether or not the prior commands succeed. 


# Extending the Language
OttoScript relies on PyParsing and heavy use of subclassing to handle the dirty work of parsing scripts into usable objects. `vocab.py` establishes a few key primitives as simple pyparsing object (digits, identifiers, etc) and establishes the BaseVocab class from which everything else inherits. 
A standard OttoScript class includes a `_parser` class attribute which defines the grammar, and a class method `parser()`, which returns a pyparsing object, which will in turn return an instance of the class. In this way, you can build more complex structures by relying on existing grammar. 

### Interpreter
`interpreter.py` contains an TestInterpreter which can be used for testing and debugging. (A 'live' interpreter can by found in the `ottopyscript` repository). The interpreter is responsible for translating OttoScript commands into live instructions to HASS (or, if someone wants to write one, a different home automation controller).

### vocab.py
In addition to the base class and primitives, the `vocab` module defines smaller, reusable OttoScript snippets, such as the `RelativeTime` class:

```
class RelativeTime(BaseVocab):
    _parser = Numeric.parser()("_count") + (Hour.parser() | Minute.parser() | Second.parser())("_unit")

    @property
    def as_seconds(self):
        return self._count.value * self._unit.as_seconds
```

### Adding a Command
Commands require only a parser and a async `eval` function which issues commands to the interpreter:
```
class Toggle(BaseCommand):
    _kwd = CaselessKeyword("TOGGLE")
    _parser = _kwd + Entity.parser()("_entity")

    async def eval(self):
        servicename = 'toggle'
        kwargs = {'entity_id': self._entity.name}
        result = await self.interpreter.call_service(self._entity.domain, servicename, kwargs)
        return result
```

### Conditions
Control structures (such as `IF`) are housed in conditions. The `eval` function is responsible for evaluating the contained conditions and returning True or False. 

