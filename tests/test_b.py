# ======================================================================================================================
#        File:  test_b.py
#     Project:  B Bug Tracker
# Description:  Distributed Bug Tracker Extention for Mercurial
#      Author:  Jared Julien <jaredjulien@exsystems.net>
#   Copyright:  (c) 2010-2011 Michael Diamond <michael@digitalgemstones.com>
#               (c) 2022 Jared Julien, Nexteer Automotive
# ---------------------------------------------------------------------------------------------------------------------
"""Unit tests for b.

To execute:

    poetry run pytest tests
"""


# ======================================================================================================================
# Import Statements
# ----------------------------------------------------------------------------------------------------------------------
import os, re, tempfile

import pytest

# Configures simple hashing in b
os.environ['HG_B_SIMPLE_HASHING'] = 'true'
import b
import helpers
import exceptions
from extension import version
from bugs_dict import BugsDict




# ======================================================================================================================
# Fixtures
# ----------------------------------------------------------------------------------------------------------------------
@pytest.fixture
def bd():
    dir = tempfile.TemporaryDirectory()
    cwd = os.getcwd()
    os.chdir(dir.name)
    bd = BugsDict()
    yield bd

    # At the end of tests, ensure data is being written to bugs dict successfully.
    # Flush the cache to disk.
    bd.write()

    # Create a new dict which will load from disk.
    disk = BugsDict()
    assert bd.list(alpha=True) == disk.list(alpha=True)

    os.chdir(cwd)
    dir.cleanup()




# ======================================================================================================================
# Tests
# ----------------------------------------------------------------------------------------------------------------------
def test_private_methods(bd):
    """Tests the private methods of BD"""
    # Like test_helpers, some methods may just be called to test that they don't raise an exception

    bd.add("test") #a94a8fe5cc
    bd.add("another test") #afc8edc74a

    #__getitem__
    with pytest.raises(exceptions.UnknownPrefix):
        bd['b']
    with pytest.raises(exceptions.AmbiguousPrefix):
        bd['a']
    assert bd['a9']['text'] == 'test'
    assert bd['a94a']['text'] == 'test'
    assert bd['afc8edc74a']['text'] == 'another test'

    #_get_details_path
    id = bd.id('a9')
    _, path = bd._get_details_path(id)

    #_make_details_file
    bd._make_details_file(id)
    assert os.path.exists(path)

    #_user_list
    bd.assign('a9', 'User', True)
    assert len(bd._users_list()) == 2

    #_get_user
    # tested more completely by test_users
    assert bd._get_user('us') == 'User'



# ----------------------------------------------------------------------------------------------------------------------
def test_api():
    """Tests api functions that don't rely on Mercurial"""
    # Version
    assert version() > version("0.6.1")



# ----------------------------------------------------------------------------------------------------------------------
def test_id(bd):
    """Straightforward test, ensures ID function works"""
    bd.add("test")
    assert bd.id('a') == 'a94a8fe5ccb19ba61c4c0873d391e987982fbbd3'



# ----------------------------------------------------------------------------------------------------------------------
def test_add(bd):
    """Basic add functionality tested everywhere, edge cases here"""
    bd.add('test|with"bars,and\'other\tpotentially#bad{characters}')
    assert bd.list() == 'd - test|with"bars,and\'other\tpotentially#bad{characters}\nFound 1 open bug'
    assert bd.last_added_id == 'deea8c528cd4fe5ff34b3a15bb97de097d99c4f2'



# ----------------------------------------------------------------------------------------------------------------------
def test_rename(bd):
    """Tests total rename and sed-style rename"""
    bd.add('test')
    bd.rename('a','give the knife')
    assert bd.list() == 'a - give the knife\nFound 1 open bug'
    bd.rename('a', '/g|kn/l/')
    assert bd.list() == 'a - live the life\nFound 1 open bug'



# ----------------------------------------------------------------------------------------------------------------------
def test_users(bd):
    """Tests output of users command"""
    bd.add('unassigned')
    bd.user = 'User'
    bd.add('test')
    bd.add('another test')
    bd.add('resolved test')
    bd.resolve('8')
    bd.user = 'A User'
    bd.add('different test')
    assert bd.users() == 'Username: Open Bugs\nUser:   2\nA User: 1\nNobody: 1\n'



# ----------------------------------------------------------------------------------------------------------------------
def test_assign(bd):
    """Tests user assignment and forcing of user creation"""
    bd.user = 'User'
    bd.add('test')
    bd.user = 'A User'
    bd.add('a test')
    bd.add('a new test')
    assert bd.users() == 'Username: Open Bugs\nUser:   1\nA User: 2\n'
    bd.assign('9','u')
    assert bd.users() == 'Username: Open Bugs\nUser:   2\nA User: 1\n'
    with pytest.raises(exceptions.UnknownUser):
        bd.assign('9','Newbie')
    bd.assign('9', 'Uther', True)
    assert bd.users() == 'Username: Open Bugs\nUser:   1\nUther:  1\nA User: 1\n'
    with pytest.raises(exceptions.AmbiguousUser):
        bd.assign('9', 'u')



# ----------------------------------------------------------------------------------------------------------------------
def test_details(bd):
    """Tests outputting of issue details with and without a details file"""
    bd.add('new test')
    assert re.match(r'Title: new test\nID: ce91fd20f393d261ea86e97fa26c273d02d43b4b\n'
                    r'Filed On: \w+, \w+ \d\d \d\d\d\d \d\d:\d\d[A|P]M'
                    r'\n\nNo Details File Found.',
                    bd.details('c'))
    bd.assign('c', 'User', True)
    bd.resolve('c')
    bd.user = 'Another User'
    bd.comment('c','Resolved an issue.\nHow nice!')
    assert re.match(r'Title: new test\nID: ce91fd20f393d261ea86e97fa26c273d02d43b4b\n'
                    r'\*Resolved\* Owned By: User\n'
                    r'Filed On: \w+, \w+ \d\d \d\d\d\d \d\d:\d\d[A|P]M\n\n'
                    r'\[comments\]\n\nBy: Another User\n'
                    r'On: \w+, \w+ \d\d \d\d\d\d \d\d:\d\d[A|P]M\nResolved an issue.\n'
                    r'How nice!',
                    bd.details('c'))



# ----------------------------------------------------------------------------------------------------------------------
def test_edit():
    """Edit does little more than launch an external editor.  Nothing to easily test for now."""
    pass



# ----------------------------------------------------------------------------------------------------------------------
def test_comment(bd):
    """Confirms comment functionality works"""
    bd.add('test')
    bd.comment('a', 'This is a comment')
    assert re.match(r'Title: test\nID: a94a8fe5ccb19ba61c4c0873d391e987982fbbd3'
                    r'\nFiled On: \w+, \w+ \d\d \d\d\d\d \d\d:\d\d[A|P]M\n\n\[comments\]\n\n'
                    r'On: \w+, \w+ \d\d \d\d\d\d \d\d:\d\d[A|P]M\nThis is a comment',
                    bd.details('a'))



# ----------------------------------------------------------------------------------------------------------------------
def test_resolve(bd):
    """Tests both resolve and reopen"""
    bd.add('test')
    bd.add('another test')
    assert bd.list() == 'a9 - test\naf - another test\nFound 2 open bugs'
    bd.resolve('af')
    assert bd.list() == 'a9 - test\nFound 1 open bug'
    assert bd.list(False) == 'af - another test\nFound 1 resolved bug'
    bd.reopen('af')
    bd.resolve('a9')
    assert bd.list() == 'af - another test\nFound 1 open bug'
    assert bd.list(False) == 'a9 - test\nFound 1 resolved bug'



# ----------------------------------------------------------------------------------------------------------------------
def test_list(bd):
    """Tests that the BD doesn't fail when calling list before the BD has done any work"""
    # empty list
    assert bd.list() == "Found 0 open bugs"
    bd.add("EFGH")
    # one item
    assert bd.list() == "a - EFGH\nFound 1 open bug"
    bd.add("ABCD")
    bd.add("IJKL")
    # additional items, ordered by ID
    assert bd.list() == "a - EFGH\nf - ABCD\n6 - IJKL\nFound 3 open bugs"
    # ordered by title
    assert bd.list(alpha=True) == "f - ABCD\na - EFGH\n6 - IJKL\nFound 3 open bugs"
    # ordered by creation time
    assert bd.list(chrono=True) == "a - EFGH\nf - ABCD\n6 - IJKL\nFound 3 open bugs"

    # TODO truncate
    # how should we test truncate in a platform independent fashion?



# ----------------------------------------------------------------------------------------------------------------------
def test_list_filters(bd):
    """Tests list's filter functionality.
        Filter by owner and by grep - resolution is tested in test_resolve
    """
    bd.add('ABCD')
    bd.assign('fb','Someone',True)
    bd.add('DEFG')
    bd.user = 'User'
    bd.add('GHIJ')
    bd.add('JKLM')
    assert bd.list(owner='me') == 'f1 - GHIJ\n4  - JKLM\nFound 2 open bugs owned by User'
    assert bd.list(owner='no') == 'b - DEFG\nFound 1 open bug owned by Nobody'
    assert bd.list(owner='some') == 'fb - ABCD\nFound 1 open bug owned by Someone'
    assert bd.list(grep='D') == 'fb - ABCD\nb  - DEFG\nFound 2 open bugs whose title contains D'
    assert bd.list(grep='h') == 'f1 - GHIJ\nFound 1 open bug whose title contains h'
    assert bd.list(owner='u', grep='j') == 'f1 - GHIJ\n4  - JKLM\nFound 2 open bugs owned by User whose title contains j'




# End of File
