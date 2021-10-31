from rest_framework import permissions


class IsPrivateAllowed(permissions.BasePermission):
    """
    Allow access to request owner
    """
    def has_permission(self, request, view):
        # return True if allowed else False
        # 'username' is the request url kwarg eg. bobby, jonhdoe
        return view.kwargs.get('username', '') == request.user.username