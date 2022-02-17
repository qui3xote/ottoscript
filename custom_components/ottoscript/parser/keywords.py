import operator as op
from pyparsing import CaselessKeyword, MatchFirst

# control keywords
AUTOMATION = MatchFirst(map(CaselessKeyword, ["AUTOMATION", "AUTO"]))
RESTART = CaselessKeyword("RESTART")

# Keywords
WHEN = CaselessKeyword('WHEN')
IF = CaselessKeyword('IF')
THEN = CaselessKeyword('THEN')
ELSE = CaselessKeyword('ELSE')
FROM = CaselessKeyword('FROM')
WITH = CaselessKeyword('WITH')
IS = CaselessKeyword('IS')
FOR = CaselessKeyword('FOR')
TRUE = CaselessKeyword('TRUE')
CHANGES = CaselessKeyword('CHANGES')
AND = CaselessKeyword('AND')
OR = CaselessKeyword('OR')
NOT = CaselessKeyword('NOT')
END = CaselessKeyword('END')
CASE = CaselessKeyword('CASE')
SWITCH = CaselessKeyword('SWITCH')
TO = CaselessKeyword('TO')
ON = CaselessKeyword('ON')
OFF = CaselessKeyword('OFF')
DEFAULT = CaselessKeyword('DEFAULT')

# Time
HOUR = MatchFirst(map(CaselessKeyword, ["HOUR", "HOURS"]))
MINUTE = MatchFirst(map(CaselessKeyword, ["MINUTE", "MINUTES", "MIN"]))
SECOND = MatchFirst(map(CaselessKeyword, ["SECOND", "SECONDS", "SEC"]))
SUNRISE = CaselessKeyword('SUNRISE')
SUNSET = CaselessKeyword('SUNSET')
BEFORE = CaselessKeyword('BEFORE')
AFTER = CaselessKeyword('AFTER')

# Other
AREA = MatchFirst(map(CaselessKeyword, ["AREAS", "AREA"]))

reserved_words = (WHEN | IF | THEN | ELSE | CASE | END
                  | FROM | IS | FOR | TRUE | CHANGES | TO | FROM | ON | OFF
                  | HOUR | MINUTE | SECOND | SUNRISE | SUNSET | BEFORE | AFTER
                  | AREA)

OPERATORS = {
    '==': op.eq,
    '<=': op.le,
    '>=': op.ge,
    '!=': op.ne,
    '<': op.lt,
    '>': op.gt
}
