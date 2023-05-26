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
from bugs import Bugs




# ======================================================================================================================
# Tests
# ----------------------------------------------------------------------------------------------------------------------
def test_make_id():
    """Verify that the hash generation method does something."""
    helpers.make_id("test")


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
