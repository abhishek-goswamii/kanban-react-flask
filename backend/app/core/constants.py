class AppConstants:
    """app wide constants"""
    API_V1_PREFIX = "/api/v1"
    SUCCESS = "success"
    ERROR = "error"
    REQUEST_ID_HEADER = "X-Request-Id"


class RouteConstants:
    """api route resource paths"""
    AUTH = "/auth"
    USERS = "/users"
    PROJECTS = "/projects"
    TASKS = "/tasks"
    STAGES = "/stages"
    COMMENTS = "/comments"
    MEMBERS = "/members"
    INVITATIONS = "/invitations"


class TaskStatus:
    """task status values"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"


class ProjectRole:
    """project member roles"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"

    ALL = ["owner", "admin", "member"]


class InvitationStatus:
    """member invitation statuses"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class Messages:
    """standard response messages"""
    # auth
    REGISTER_SUCCESS = "registered successfully"
    LOGIN_SUCCESS = "logged in successfully"
    LOGOUT_SUCCESS = "logged out successfully"
    INVALID_CREDENTIALS = "invalid email or password"
    EMAIL_ALREADY_EXISTS = "email already exists"
    UNAUTHORIZED = "authentication required"
    TOKEN_EXPIRED = "token has expired"
    TOKEN_INVALID = "invalid token"

    # project
    PROJECT_CREATED = "project created successfully"
    PROJECT_UPDATED = "project updated successfully"
    PROJECT_DELETED = "project deleted successfully"
    PROJECT_NOT_FOUND = "project not found"

    # task
    TASK_CREATED = "task created successfully"
    TASK_UPDATED = "task updated successfully"
    TASK_DELETED = "task deleted successfully"
    TASK_NOT_FOUND = "task not found"
    TASK_MOVED = "task moved successfully"

    # stage
    STAGE_CREATED = "stage created successfully"
    STAGE_NOT_FOUND = "stage not found"

    # comment
    COMMENT_CREATED = "comment added successfully"
    COMMENT_DELETED = "comment deleted successfully"
    COMMENT_NOT_FOUND = "comment not found"

    # member
    MEMBER_INVITED = "member invited successfully"
    MEMBER_REMOVED = "member removed successfully"
    MEMBER_NOT_FOUND = "member not found"
    ALREADY_A_MEMBER = "user is already a member"
    INVITATION_ACCEPTED = "invitation accepted"
    INVITATION_REJECTED = "invitation rejected"
    INVITATION_NOT_FOUND = "invitation not found"
    USER_NOT_FOUND = "user not found"
    CANNOT_REMOVE_OWNER = "cannot remove the project owner"

    # generic
    SERVER_ERROR = "internal server error"
    VALIDATION_ERROR = "validation error"
    FORBIDDEN = "you do not have permission to perform this action"
