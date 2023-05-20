# ======================================================================================================================
#        File:  exceptions.py
#     Project:  B Bug Tracker
# Description:  Distributed Bug Tracker Extension for Mercurial
#      Author:  Jared Julien <jaredjulien@exsystems.net>
#   Copyright:  (c) 2010-2011 Michael Diamond <michael@digitalgemstones.com>
#               (c) 2022-2023 Jared Julien <jaredjulien@exsystems.net>
# ---------------------------------------------------------------------------------------------------------------------
"""Exceptions used by b."""

# ======================================================================================================================
# Exceptions
# ----------------------------------------------------------------------------------------------------------------------
class Error(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, msg):
        super(Error, self).__init__(msg)
        self.msg = msg


# ----------------------------------------------------------------------------------------------------------------------
class RequiresPrefix(Error):
    """Raised by CLI when a prefix is required."""

    def __init__(self):
        super().__init__("You need to provide an issue prefix.  Run list to get a unique prefix for the bug you are "
            "looking for.")


# ----------------------------------------------------------------------------------------------------------------------
class UnknownPrefix(Error):
    """Raised when trying to use a prefix that does not match any tasks."""

    def __init__(self, prefix):
        super().__init__("The provided prefix (%s) could not be found in the bugs database." % prefix)
        self.prefix = prefix


# ----------------------------------------------------------------------------------------------------------------------
class AmbiguousPrefix(Error):
    """Raised when trying to use a prefix that could identify multiple tasks."""

    def __init__(self, prefix):
        super().__init__(
            "The provided prefix - %s - is ambiguous, and could point to multiple bugs. Run list to get a unique "
            "prefix for the bug you are looking for." % prefix)
        self.prefix = prefix


# ----------------------------------------------------------------------------------------------------------------------
class AmbiguousUser(Error):
    """Raised when trying to use a prefix that could identify multiple users."""

    def __init__(self, user, matched):
        super().__init__("The provided user - %s - matched more than one user: %s" % (user, ', '.join(matched)))
        self.user = user
        self.matched = matched


# ----------------------------------------------------------------------------------------------------------------------
class UnknownUser(Error):
    """Raised when trying to use a user prefix that does not match any users."""

    def __init__(self, user):
        super().__init__("The provided user - %s - did not match any users in the system. "
            "Use -f to force the creation of a new user." % user)
        self.user = user


# ----------------------------------------------------------------------------------------------------------------------
class AmbiguousCommand(Error):
    """Indicates the given command prefix matches more than one command."""

    def __init__(self, cmds):
        super().__init__("Command ambiguous between: %s" % ', '.join(cmds))
        self.cmds = cmds


# ----------------------------------------------------------------------------------------------------------------------
class UnknownCommand(Error):
    """Raised when trying to run an unknown command."""

    def __init__(self, cmd):
        super(UnknownCommand, self).__init__("No such command '%s'" % cmd)
        self.cmd = cmd


# ----------------------------------------------------------------------------------------------------------------------
class InvalidCommand(Error):
    """Raised when command invocation is invalid, e.g. incorrect options."""

    def __init__(self, reason):
        super(InvalidCommand, self).__init__("Invalid command: %s" % reason)
        self.reason = reason


# ----------------------------------------------------------------------------------------------------------------------
class InvalidInput(Error):
    """Raised when the input to a command is somehow invalid - for example, a username with a | character will cause
    problems parsing the bugs file.
    """

    def __init__(self, reason):
        super(InvalidInput, self).__init__("Invalid input: %s" % reason)
        self.reason = reason


# ----------------------------------------------------------------------------------------------------------------------
class TemplateError(Error):
    """Raised when the specified template does not exist."""




# End of File
