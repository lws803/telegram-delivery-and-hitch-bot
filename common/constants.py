from enum import Enum


class StateType(Enum):
    ACTIVE = 'active'
    DONE = 'done'


class RoleType(Enum):
    DRIVER = 'driver'
    CUSTOMER = 'customer'


class RegExpressions:
    NO_COMMAND_SLASH = r'^[^\/]'
    PRICE = r'^[0-9]+(\.[0-9][0-9])?$'
    NUMBER = r'^[0-9]*$'
