class DriverHasControlException(Exception):
    def __init__(self, message="Driver took control while we were operating the sorting algorithm"):
        super().__init__(message)
