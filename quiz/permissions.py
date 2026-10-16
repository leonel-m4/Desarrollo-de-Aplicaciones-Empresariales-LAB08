from rest_framework.permissions import SAFE_METHODS, BasePermission

AGENT_GROUP = "agente"


class AgentPermission(BasePermission):
    """Enforce roles on the server, regardless of the client.

    The rule the lab asks for:
      - a person (user with is_staff) can do anything;
      - the group «agente» may read, create and modify, but never delete;
      - anybody else who is logged in can only read;
      - an unknown method is denied (deny by default).
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if request.method not in (
            *SAFE_METHODS, "POST", "PUT", "PATCH", "DELETE"
        ):
            return False
        if request.method in SAFE_METHODS or user.is_staff:
            return True
        return (
            request.method in ("POST", "PUT", "PATCH")
            and user.groups.filter(name=AGENT_GROUP).exists()
        )
