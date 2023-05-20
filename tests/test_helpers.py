# ======================================================================================================================
#        File:  test_helpers.py
#     Project:  B Bug Tracker
# Description:  Distributed Bug Tracker Extension for Mercurial
#      Author:  Jared Julien <jaredjulien@exsystems.net>
#   Copyright:  (c) 2010-2011 Michael Diamond <michael@digitalgemstones.com>
#               (c) 2022-2023 Jared Julien <jaredjulien@exsystems.net>
# ---------------------------------------------------------------------------------------------------------------------
"""Tests specifically for the various helper functions in helpers.py.

To execute:

    poetry run pytest tests
"""


# ======================================================================================================================
# Import Statements
# ----------------------------------------------------------------------------------------------------------------------
import os, re, tempfile
import shutil

import pytest

# Configures simple hashing in b
os.environ['HG_B_SIMPLE_HASHING'] = 'true'
import b
import helpers
import exceptions
from extension import version
from bugs_dict import BugsDict




# ======================================================================================================================
# Tests
# ----------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize('value', [None, 1310458238.24])
def test_datetime(value):
    """Tests format datatime method, specifically some edge cases."""
    helpers.formatted_datetime(value)


# ----------------------------------------------------------------------------------------------------------------------
def test_hash():
    """Verify that the hash method does something."""
    helpers.hash("test")


# ----------------------------------------------------------------------------------------------------------------------
def test_mkdirp():
    """Verify that the mkdirp works."""
    path = os.path.join('dir', 'to', 'test', '_mkdir_p')
    helpers.mkdir_p(path)
    assert os.path.exists(path)
    shutil.rmtree(path)


# ----------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize('value, expected', [
    ('True', True),
    ('Flase', False)
])
def test_truth(value, expected):
    """Verify that a truth input produces a truthy output."""
    assert helpers.truth(value) == expected


# ----------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize('line', [
    "",
    "task",
    "    task    | a:1, b:2, c:3, d:4, e:5",
    "task|    id:13443, owner:, open: True, time: 1234",
    "task|    id:13443, owner:somebody, open: True, time: 1234",
    "task | taskpart | id:1234"
])
def test_task_from_taskline_good(line):
    """Test tasklines that should succeed."""
    task = helpers.task_from_taskline(line)
    assert task['text'] == line.rsplit('|',1)[0].strip()


# ----------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize('line', [
    "task|taskpart", # can't handle direct edit inserts with |
    "task | id:12|34, owner=you?" # can't handle | in metadata
])
def test_task_from_taskline_bad(line):
    """Test tasklines that should fail."""
    with pytest.raises(IOError):
        helpers.task_from_taskline(line)


# ----------------------------------------------------------------------------------------------------------------------
def test_taskline_from_tasks():
    """Verify correct parsing of tasklines from tasks."""
    helpers.tasklines_from_tasks([{
        'text': "task",
        'id':"4567"
    }])


# ----------------------------------------------------------------------------------------------------------------------
def test_prefixes():
    """Verify prefix generation produces the expected outputs."""
    prefix_gen = ['a','abb','bbb','bbbb','cdef','cghi','defg','defh','e123456789']
    assert helpers.prefixes(prefix_gen) == {
        'a': 'a',
        'abb': 'ab',
        'defh': 'defh',
        'cdef': 'cd',
        'e123456789': 'e',
        'cghi': 'cg',
        'bbbb': 'bbbb',
        'bbb': 'bbb',
        'defg': 'defg'
    }


# ----------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize('count, open, owner, grep, result', [
    (1,  True,  '*',    '',     'Found 1 open bug'                                            ),
    (10, True,  '*',    '',     'Found 10 open bugs'                                          ),
    (11, False, '*',    '',     'Found 11 resolved bugs'                                      ),
    (12, True,  '',     '',     'Found 12 open bugs owned by Nobody'                          ),
    (13, True,  'Jack', '',     'Found 13 open bugs owned by Jack'                            ),
    (14, True,  '',     'Word', 'Found 14 open bugs owned by Nobody whose title contains Word'),
    (15, True,  'Jack', 'Word', 'Found 15 open bugs owned by Jack whose title contains Word'  ),

])
def test_describe_print(count, open, owner, grep, result):
    """Verify that the output formatter produces pretty stings with various inputs."""
    assert helpers.describe_print(count, open, owner, grep) == result




# End of File
