# OttoScript

## What is OttoScript?
`OttoScript` is a toolkit for parsing OttoScript files (*.otto) into python objects which can then be used to run home automations. 

## Installing ottoscript
Installation is simply a matter of checking out the code from github. (For instructions on how to install this on HomeAssistant, see [ottopyscript](https://github.com/qui3xote/ottopyscript))

# The Language
Ottoscript is inspired by SQL - it aims to provide an intuitive and human-readable language for creating automations with minimal syntax. Whitespace, line breaks, indentations and capitalization are all ignored (but are recommended for readability). At the same time, OttoScript supports programming concepts (like variables) that make the language flexible and more capable than YAML. Here's an example, in a file called workroutine.otto:

```
@working = input_boolean.working

AUTO work_start
  WHEN 08:00 on WEEKDAY
    SET @working TO 'on'
;

AUTO work_end
  WHEN 17:00 on WEEKDAY
    SET @working TO 'off'
;

AUTO start_end_work
  WHEN @working CHANGES
    CASE
      IF @working == 'on'
          DIM AREA office to 70%
          TURN ON SWITCH switch.noise_machine_on_off
      END
      IF  @working == 'off'
          TURN OFF LIGHT AREA office
          TURN OFF SWITCH switch.noise_machine_on_off
      END
    END
;
```

In this example, there are three automations; Each automation begins with `AUTO _name_` and  a WHEN statement, and ends with a semi-colon. So in the example above, the first two turn an input_boolean on and off at the beginning and end of the work day. The last automation watches for changes in the input_boolean and reacts by turning on/off lights and a white noise machine in my home office. It uses a switch statment to check which state the input_boolean is in (on/off) before deciding which commands to run.

Every Automation has three sections: Controls, Triggers and Actions. 
 - **Controls** give the automation a name, and have other options for deciding 'how' the automation runs. 
 - **Triggers** determine 'when' the automation runs - whether it's based on time of day or another event.
 - **Actions** determine 'what' an automation will do by running Commands (such as DIM, LOCK, or TURN OFF) and under what conditions, using IF or Switch statements. 

## Controls
AUTO _name_ (_trigger_variable_ **@trigger**) (**SINGLE** | RESTART)

The only requirement for controls is to start with the AUTO keyword, and give your automation a _name_. There are two optional controls (enclosed in parentheses) - the trigger variable and the mode. By default, OttoScript captures information about what triggered your automation and makes it accessible in the @trigger variable. If you want, you can rename this to something else by providing a different variable here. The mode tells OttoScript what to do if your automation triggers again while the actions from the last trigger are still running. SINGLE (which is the default) will ignore the new trigger and complete what it was doing. RESTART will cause the automation to start again from the top. 

## Triggers

WHEN statements specify triggers - such as time of day, or a change in the state of an entity. You can have multiple triggers (WHEN statements) in an automation  - if any one of them fires, the actions will run. 

### State Change Triggers
WHEN \[_entity_] CHANGES (FROM _old-state_) (TO _new-state_) (FOR _number_ HOURS | MINUTES | SECONDS)

An state change trigger watches one or more entities and fires if the entity changes, if it meets the optional FROM, TO & FOR criteria. FROM and TO control what the old and new values must be, and FOR says that the entity must stay in it's new state for a period of time before the actions run; If the entity changes again during that time, the actions won't run and the timer will restart if the new state still meets the FROM/TO criteria. Note that _entity_ is enclosed in brackets in the definition above, because you can pass a comma seperated list of entities and the trigger will fire if anyone one of them is true.

Examples

```WHEN person.john, person.jane CHANGES FROM 'home'``` will run when either john or jane leave home. 

```WHEN binary_sensor.bathroom_motion CHANGES TO 'off' FOR 5 MINUTES``` will run when the bathroom motion sensor has stayed 'off' for 5 minutes.


### Time Triggers
WHEN \[_time_] (ON \[_dayofweek_])

Time trigger let you schedule automations for certains times on certain days of the week. Times and days can both be lists, and if days are ommitted, it will run every day. Times use a 24 hour clock, and seconds are optional, so `08:30` and `08:30:00` both mean 8:30 AM. Days can be full or shortened name (TUESDAY or TUE) or WEEKDAY/WEEKEND 

Examples

```WHEN 06:30``` 6:30AM every day.

```WHEN 12:00, 13:00 on Mon, Wed, Fri``` Noon and 1PM on Monday, Wedensday and Friday.

```WHEN 08:30 ON WEEKEND``` 8:30AM on Satuday and Sunday. 


Time can also be SUNRISE or SUNSET, and can be modified with a BEFORE/AFTER statement:

```WHEN 30 MINUTES BEFORE SUNRISE``` 30 Minutes before sunrise everyday.

```WHEN 1 HOUR AFTER SUNSET on WEEKDAY``` 1 Hour after sunset on weekdays. 

**NB** Sunrise/Sunset times currently can't be included in lists. So if you want a sun trigger and time-of-day trigger, or two sun triggers on the same automation, you'll need to use two WHEN statements. 

## Actions
Actions break down into two components: **Commands** to be run, and **Conditions** that can control under what circumnstances they will run. 

### Commands
Most commmands call Home Assistant services and follow a basic pattern:

KEYWORDS [_targets_] (WITH [_optional\_data_])

Targets can be entities or areas, though areas needed to be preceded by the AREA keyword (I am hoping to remove this requirement in a future release). 

```LOCK AREA downstairs, first_floor WITH (code=1234)``` Will lock all the doors in the downstairs and first_floor areas, using the code 1234. Multiple options can be passed inside the parentheses as a comma seperated list: `(code=1234, other_stuff='stuff')` OttoScript doesn't actually look at what is in those options - it just passes them along to Home Assistant, so it's up to you to know which options are supported. 

There are some exceptions to this pattern:

1. A few commands can apply to many types of entities. For those commands, it's necessary to specify which domain you want to apply it to. In those cases, the domain is always the first thing to specify after the keywords (`TURN OFF LIGHT`, `TOGGLE SWITCH`), followed by targets and optional_data.
2. Some commands are shortcuts for common tasks, and have their own ways of specifying options. So, `DIM light.office_light to 50%` will work the same as `TURN ON LIGHT light.office_light WITH (brightness_pct=50)` - it's just easier to type and read.
3. Then there are few special commands that just work differently, like PASS, WAIT and SET, because, well they *are* different. 

There are two special commands that are worth calling out:
- Variable assignments are commands, but don't have a keyword. They take the form @varname = _value_. Variable names must start with an @ and can only include letters, numbers and underscores in the rest of the name. They can contain entities, areas, numbers, strings (anything enclosed in quotes), lists, and dictionaries (`(code=1234)`). Because they are commands in their own right, you can't assign a variable inside another command (you can read it however).
- CALL lets you run *any* home assistant service, and it's format is somewhat different to allow it be flexible. So even if a service isn't directly supported with a keyword command, you can still use CALL to get the job done. 

### Conditions
IF and CASE let you selectively run parts of the automation depending what else is true, using comparisons, like so:

```IF light.office_lights == 'on'``` 

The comparison has 3 parts - a left term (`light.office_light`), an operator (`==`) and a right term (`'on'`).  The terms can be numbers, strings, entities or variables, and the operators include the usual mathematical comparisons (>, >=, <, <=, ==, !=, ==). (For non-progammers, '==' just means equals. It's used here to instead of a single '=' so that it's clear we're not trying to assign a variable). 

Comparisons can also be chained together using AND, OR and NOT. So `IF light.office_light =='on' AND input_boolean.sleep == 'off'` is only true if BOTH comparisons are true. 

IF and CASE conditions are closed off by the END keyword. This allows for things like only placing conditions around a few commands and then having the rest always run, and also for nesting conditions. They both also support an optional ELSE section which will run if the comparison(s) are false. 

**NB** Unlike HA YAML, the whole automation doesn't stop when a condition isn't met. The commands inside the condition aren't run, but OttoScript keeps going and tries to run the rest of the script.


## Appendix: Command Reference


### Services

**TURN** (ON | OFF) _domain_ \[_targets_] (WITH _optional\_data_)

**TOGGLE** \[_entities_]

**LOCK** \[_targets_] (WITH _optional\_data_)

**UNLOCK** \[_targets_] (WITH _optional\_data_)

**ARM** _arm\_type_ \[_targets_] (WITH _optional\_data_)

**DISARM** _arm\_type_ \[_targets_] (WITH _optional\_data_)

**CALL** _domain.service_ ON \[_targets_] (WITH _optional\_data_)


### Shorcuts

**OPEN** \[_cover_targets_] (TO _percent\_open_)

**CLOSE** \[_cover_targets_] (TO _percent\_closed_)

**DIM** \[_light\_targets_] TO | BY _number_ (%)



### Script Controls

**WAIT** _number_ (SECONDS | MINUTES | HOURS) - Wait for the specified time before running the next command.

**PASS** - Do nothing. 


### Other

**SET** _entity_ TO _state_ - this updates HA's internal representation of the entity state. It will *not* turn your lights on/off or control your devices. It can be used to change an input helper, or to test whether a trigger works. 



