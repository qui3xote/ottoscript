test_automation = """
CONDITIONS
	IF input.vacation = 'on'
WHEN person.tom changes to home
	IF person.catherina is not home
WHEN person.catherina changes to home
	IF person.tom is not home
THEN
	SET home.temperature to 70
		if weather.tempurature < 70
	SET home.temperature to 68
		if weather.temperature
"""

test_automation2 = """
CONDITIONS
	IF input.vacation == 'on'
WHEN person.tom changes to home
	IF catherina is not home
WHEN catherina changes to home
	IF tom is not home
THEN
	SET home.temperature = 70
		if weather.tempurature < 70
	SET home.temperature = 68
		if weather.temperature
"""

light_bonding = """
WHEN light1 changes
When light2 changes
THEN
     Set light1 brightness to light2 brightness
       If light2 changed
     Set light2 brightness to light1 brightness
       If light1 changed
"""

sunset_routine = """
PRECONDITIONS
    IF input.vacation == 'off'
WHEN 15 minutes before sunrise
    IF house.occupied == 'on'
THEN
    SET downstairs.lights:brightness = 20
        IF downstairs.light:brightness < 20
    WAIT 45 minutes
    SET upstairs.lights, main_room.lights to 20
    SET master_bedroom.cover.window to closed
    SET den.lights brightness to 20
        if den.lumens < input.cozylights
"""

sunset_routine_tabbed = """
WHEN sunrise.time == 'now'
    IF input.vacation == 'off'
        AND house.occupied == 'on'
    OR input.testing == 'on'
THEN
    IF downstairs.light:brightness < 20
        SET downstairs.lights:brightness = 20
    WAIT 45 minutes
    SET upstairs.lights, main_room.lights to 20
    SET master_bedroom.cover.window to closed
    SET den.lights brightness to 20
        if den.lumens < input.cozylights
"""
