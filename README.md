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

This automation specifies a trigger (`WHEN`) and a control structure (`IF` `THEN`) for deciding what conditions (`person.tom IS 'home'`) must be met before a sequence of commands are executed ```TURN OFF lights.porch_sconce_lights
     LOCK lock.entry```

## WHEN
All ottoscripts automation begin with a WHEN clause, which specifies an event (aka 'trigger') that must occur before the rest of the script occurs:

WHEN _entity_ CHANGES (FROM _state_) (TO _state_) 
`FROM` and `TO` are optional, but must be in the order above if both are used, multiple triggers may be strung together with `OR`. 

Example ```WHEN person.tom CHANGES TO 'home' or person.mywife CHANGES TO 'home'```

## IF
IF _entity_ [operand] [value]

Supported operands include standard mathematical notations ('=','<','>', etc) and `IS`.  Multiple conditions can be strung together using `AND`, `OR` and `NOT`, and parentheses can be used to control the order of evaluation. 

Example ```IF light.office_lights:brightness_pct < 50 AND binary_sensor.office_occupied OR input_boolean.keep_the_lights_on IS 'on```





### requirements
Python 3.7+
Pyparsing 3.0+

## What does this repository contain?

### vocab.py

### commands.py

### conditions.py

### teststrings.py

### triggers.py
