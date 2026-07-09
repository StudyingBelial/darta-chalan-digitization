from enum import Enum

class USER_TYPE(Enum):
    OFFICE_ADMIN = "OFFICE_ADMIN"
    STAFF = "STAFF"
    SYSTEM_ADMIN = "SYSTEM_ADMIN"

class LOG_TYPE(Enum):
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LOG_SOURCE(Enum):
    SYSTEM = "SYSTEM"
    USER = "USER"