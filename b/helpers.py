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
def formatted_datetime(timestamp=None):
    """Returns a formatted string of the time from a timestamp, or now if called with no arguments."""
    if timestamp:
        t = datetime.fromtimestamp(float(timestamp))
    else:
        t = datetime.now()
    return t.strftime("%A, %B %d, %Y at %I:%M %p")


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
def prefixes(elements):
    """Return a mapping of elements to their unique prefix in O(n) time.

    This is much faster than the native t function, which takes O(n^2) time.

    Each prefix will be the shortest possible substring of the element that
    can uniquely identify it among the given group of elements.

    If an element is entirely a substring of another, the whole string will be
    the prefix.
    """
    pre = {}
    for e in elements:
        e_len = len(e)
        i, prefix = None, None  # should always be overwritten
        for i in range(1, e_len + 1):
            # Identifies an empty prefix slot, or a singular collision
            prefix = e[:i]
            if prefix not in pre or (
                    pre[prefix] != ':' and prefix != pre[prefix]):
                break
        if prefix in pre:
            # Handle collisions
            collide = pre[prefix]
            for j in range(i, e_len + 1):
                if collide[:j] == e[:j]:
                    pre[e[:j]] = ':'
                else:
                    pre[collide[:j]] = collide
                    pre[e[:j]] = e
                    break
            else:
                pre[collide[:e_len + 1]] = collide
                pre[e] = e
        else:
            # No collision, can safely add
            pre[prefix] = e

    # Invert mapping and clear placeholder key
    pre = dict(zip(pre.values(), pre.keys()))
    if ':' in pre:
        del pre[':']
    return pre


# ----------------------------------------------------------------------------------------------------------------------
def describe_print(num, is_open, owner, filter_by):
    """Helper function used by list to describe the data just displayed """
    type_name = 'open' if is_open else 'resolved'
    out = "Found %s %s bug%s" % (num, type_name, '' if num == 1 else 's')
    if owner != '*':
        out = out + (" owned by %s" % ('Nobody' if owner == '' else owner))
    if filter_by:
        out = out + " whose title contains %s" % filter_by
    return out




# End of File
