# ======================================================================================================================
#        File:  helpers.py
#     Project:  B Bug Tracker
# Description:  Simple bug tracker
#      Author:  Jared Julien <jaredjulien@exsystems.net>
#   Copyright:  (c) 2010-2011 Michael Diamond <michael@digitalgemstones.com>
#               (c) 2022-2023 Jared Julien <jaredjulien@exsystems.net>
# ---------------------------------------------------------------------------------------------------------------------
"""A variety of helper methods used internally by b."""

# ======================================================================================================================
# Import Statements
# ----------------------------------------------------------------------------------------------------------------------
import time
import hashlib
from datetime import datetime
from typing import List




# ======================================================================================================================
# Helpers
# ----------------------------------------------------------------------------------------------------------------------
def make_id(existing: List[str] = None):
    """Return a hash of the given text for use as an id.

    Currently SHA1 hashing is used.  It should be plenty for our purposes.
    """
    while True:
        hash = hashlib.sha1(str(time.time()).encode('utf-8')).hexdigest()
        if not existing or hash not in existing:
            return hash



# ----------------------------------------------------------------------------------------------------------------------
def describe_print(num, is_open, owner, filter_by):
    """Helper function used by list to describe the data just displayed."""
    type_name = 'open' if is_open else 'resolved'
    out = "Found %s %s bug%s" % (num, type_name, '' if num == 1 else 's')
    if owner != '*':
        out = out + (" owned by %s" % ('Nobody' if owner == '' else owner))
    if filter_by:
        out = out + " whose title contains %s" % filter_by
    return out




# End of File
