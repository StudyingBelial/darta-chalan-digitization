from backend.app.enums import PERMISSIONS, USER_TYPE

ROLE_PREMISSIONS = {
    USER_TYPE.STAFF: [
        PERMISSIONS.USER_SELF_UPDATE,

        PERMISSIONS.DARTA_CREATE,
        PERMISSIONS.DARTA_SEARCH,
        PERMISSIONS.DARTA_FORWARD,

        PERMISSIONS.CHALAN_CREATE,
        PERMISSIONS.CHALAN_SEARCH,
        PERMISSIONS.CHALAN_FORWARD,

        PERMISSIONS.DOCUMENT_OCR,
        PERMISSIONS.DOCUMENT_DOWNLOAD,
    ],

    USER_TYPE.OFFICE_ADMIN: [
        PERMISSIONS.USER_CREATE,
        PERMISSIONS.USER_DISABLE,
        PERMISSIONS.USER_SEARCH,
        PERMISSIONS.USER_SELF_UPDATE,
        PERMISSIONS.USER_OTHER_UPDATE,

        PERMISSIONS.OFFICER_CREATE,
        PERMISSIONS.OFFICER_UPDATE,
        PERMISSIONS.OFFICER_SEARCH,

        PERMISSIONS.DARTA_CREATE,
        PERMISSIONS.DARTA_UPDATE,
        PERMISSIONS.DARTA_SEARCH,
        PERMISSIONS.DARTA_FORWARD,

        PERMISSIONS.CHALAN_CREATE,
        PERMISSIONS.CHALAN_UPDATE,
        PERMISSIONS.CHALAN_SEARCH,
        PERMISSIONS.CHALAN_FORWARD,

        PERMISSIONS.DOCUMENT_OCR,
        PERMISSIONS.DOCUMENT_DOWNLOAD,
    ],

    USER_TYPE.SYSTEM_ADMIN: list(PERMISSIONS)
}

def has_permission(user, permission: PERMISSIONS) -> bool:
    """
    Check if a user has a specific permission.
    Returns True if the user is active and has the permission, False otherwise.
    """
    if not user or getattr(user, "is_disabled", False):
        return False
    allowed = ROLE_PREMISSIONS.get(user.user_type, [])
    return permission in allowed