from enum import Enum


class StateType(Enum):
    ACTIVE = 'active'
    DONE = 'done'


class RoleType(Enum):
    DRIVER = 'driver'
    CUSTOMER = 'customer'
