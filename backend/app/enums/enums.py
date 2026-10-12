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

class DOCUMENT_STATUS(Enum):
    REGISTERED = "REGISTERED"
    FORWARDED = "FORWARDED"
    UNDER_REVIEW = "UNDER_REVIEW"
    ACTION_TAKEN = "ACTION_TAKEN"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"

class PERMISSIONS(Enum):
    USER_CREATE = "users:create"
    USER_DISABLE = "users:disable"
    USER_SEARCH = "users:search"
    USER_SELF_UPDATE = "users:self_update"
    USER_OTHER_UPDATE = "users:other_update"

    LOG_VIEW = "logs:view"

    OFFICE_CREATE = "offices:create"
    OFFICE_UPDATE = "offices:update"
    OFFICE_SEARCH = "offices:search"

    DEPARTMENT_CREATE = "departments:create"
    DEPARTMENT_UPDATE = "departments:update"
    DEPARTMENT_SEARCH = "departments:search"

    FINANCIAL_YEAR_CREATE = "financial_year:create"
    FINANCIAL_YEAR_UPDATE = "financial_year:update"
    FINANCIAL_YEAR_SEARCH = "financial_year:search"

    OFFICER_CREATE = "officers:create"
    OFFICER_UPDATE = "officers:update"
    OFFICER_SEARCH = "officers:search"

    DARTA_CREATE = "darta:create"
    DARTA_UPDATE = "darta:update"
    DARTA_SEARCH = "darta:search"
    DARTA_FORWARD = "darta:forward"

    CHALAN_CREATE = "chalan:create"
    CHALAN_UPDATE = "chalan:update"
    CHALAN_SEARCH = "chalan:search"
    CHALAN_FORWARD = "chalan:forward"

    DOCUMENT_OCR = "document:ocr"
    DOCUMENT_DOWNLOAD = "document:download"