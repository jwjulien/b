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
import errno
import hashlib
import os
import time
from datetime import datetime




# ======================================================================================================================
# Helpers
# ----------------------------------------------------------------------------------------------------------------------
def bugs_dir(ui):
    """Returns the path to the bugs dir, relative to the repo root."""
    return ui.config(b"bugs", b"dir", b".bugs").decode('utf-8')


# ----------------------------------------------------------------------------------------------------------------------
def formatted_datetime(timestamp=None):
    """Returns a formatted string of the time from a timestamp, or now if called with no arguments."""
    if timestamp:
        t = datetime.fromtimestamp(float(timestamp))
    else:
        t = datetime.now()
    return t.strftime("%A, %B %d, %Y at %I:%M %p")


# ----------------------------------------------------------------------------------------------------------------------
def hash(*args):
    """Return a hash of the given text for use as an id.

    Currently SHA1 hashing is used.  It should be plenty for our purposes.
    """
    return hashlib.sha1(''.join(args).encode('utf-8')).hexdigest()


# ----------------------------------------------------------------------------------------------------------------------
def mkdir_p(path):
    """Race condition handling recursive mkdir -p call:
    http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
    """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise


# ----------------------------------------------------------------------------------------------------------------------
def truth(s):
    """Indicates the truth of a string."""
    return s == 'True' or s == 'true'


# ----------------------------------------------------------------------------------------------------------------------
def task_from_taskline(taskline):
    """Parse a taskline (from a task file) and return a task.

    A taskline should be in the format:

        summary text ... | meta1:meta1_value,meta2:meta2_value,...

    The task returned will be a dictionary such as:

        { 'id': <hash id>,
          'text': <summary text>,
           ... other metadata ... }

    A taskline can also consist of only summary text, in which case the id
    and other metadata will be generated when the line is read.  This is
    supported to enable editing of the taskfile with a simple text editor.
    """
    try:
        if '|' in taskline:
            text, meta = taskline.rsplit('|', 1)
            task = {'text': text.strip()}
            for piece in meta.strip().split(','):
                label, data = piece.split(':', 1)
                task[label.strip()] = data.strip()
        else:
            text = taskline.strip()
            task = {'id': hash(text, str(time.time())),
                    'text': text,
                    'owner': '',
                    'open': 'True',
                    'time': time.time()
                    }
        return task
    except Exception:
        raise IOError(errno.EIO,
                      "Failed to parse task; perhaps a missplaced '|'?\n"
                      "Line is: %s" % taskline)


# ----------------------------------------------------------------------------------------------------------------------
def tasklines_from_tasks(tasks):
    """Parse a list of tasks into tasklines suitable for writing to a file."""

    tasklines = []

    for task in tasks:
        meta = [m for m in task.items() if m[0] != 'text']
        meta_str = ', '.join('%s:%s' % m for m in meta)
        tasklines.append('%s | %s\n' % (task['text'].ljust(60), meta_str))

    return tasklines


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
    """ Helper function used by list to describe the data just displayed """
    type_name = 'open' if is_open else 'resolved'
    out = "Found %s %s bug%s" % (num, type_name, '' if num == 1 else 's')
    if owner != '*':
        out = out + (" owned by %s" % ('Nobody' if owner == '' else owner))
    if filter_by:
        out = out + " whose title contains %s" % filter_by
    return out




# End of File
