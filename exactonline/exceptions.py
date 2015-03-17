# vim: set ts=8 sw=4 sts=4 et ai tw=79:


class ExactOnlineError(Exception):
    pass


class MultipleObjectsReturned(ExactOnlineError):
    """
    Exception named Django style.
    """
    pass


class ObjectDoesNotExist(ExactOnlineError):
    """
    Exception named Django style.
    """
    pass
