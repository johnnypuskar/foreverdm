from server.backend.errors.error import Error

class Errors:
    class UnspecifiedError(Error):
        def __init__(self):
            super().__init__(1000, "UNSPECIFIED_ERROR", "An unspecified error occurred.")
    
    class DataAccessError(Error):
        def __init__(self):
            super().__init__(1001, "DATA_ACCESS_ERROR", "An error occurred while accessing the database.")

    class SessionNotFound(Error):
        def __init__(self):
            super().__init__(1002, "SESSION_NOT_FOUND", "Session not found.")

    class UserNotInCampaign(Error):
        def __init__(self):
            super().__init__(1100, "USER_NOT_IN_CAMPAIGN", "User is not in the specified campaign.")

    class StatblockNotFound(Error):
        def __init__(self):
            super().__init__(1101, "STATBLOCK_NOT_FOUND", "The specified statblock was not found in the database.")

    class StatblockNotInCampaign(Error):
        def __init__(self):
            super().__init__(1102, "STATBLOCK_NOT_IN_CAMPAIGN", "Statblock is not in the specified campaign.")

    class UserNotOwnStatblock(Error):
        def __init__(self):
            super().__init__(1103, "USER_NOT_OWN_STATBLOCK", "User does not own the specified statblock.")
    
    class InstanceNotFound(Error):
        def __init__(self):
            super().__init__(1104, "INSTANCE_NOT_FOUND", "The specified instance was not found.")

    class InstanceTypeError(Error):
        def __init__(self):
            super().__init__(1105, "INSTANCE_TYPE_ERROR", "The instance type is invalid.")

    class InvalidLocation(Error):
        def __init__(self):
            super().__init__(1106, "INVALID_LOCATION", "The specified location is invalid or does not exist in the campaign.")

    class InvalidInstanceType(Error):
        def __init__(self):
            super().__init__(1107, "INVALID_INSTANCE_TYPE", "The specified instance type is invalid or not supported.")
    
    class PausedInstanceNotFound(Error):
        def __init__(self):
            super().__init__(1108, "PAUSED_INSTANCE_NOT_FOUND", "The specified paused instance was not found.")

    class NoInstanceFound(Error):
        def __init__(self):
            super().__init__(1109, "NO_INSTANCE_FOUND", "No instance found for the campaign and location.")

    class StatblockNotInInstance(Error):
        def __init__(self):
            super().__init__(1110, "STATBLOCK_NOT_IN_INSTANCE", "The specified statblock is not part of the instance.")

    class InvalidCommand(Error):
        def __init__(self, command):
            super().__init__(1200, "INVALID_COMMAND", f"The command '{command}' is invalid or not recognized.")
    
    class InvalidArguments(Error):
        def __init__(self):
            super().__init__(1201, "INVALID_ARGUMENTS", "The provided arguments are invalid or missing.")

    class NotImplementedError(Error):
        def __init__(self, feature):
            super().__init__(1200, "NOT_IMPLEMENTED_ERROR", f"Uses unimplemented feature: {feature}")