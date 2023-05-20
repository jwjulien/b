# ======================================================================================================================
#        File:  bugs_dict.py
#     Project:  B Bug Tracker
# Description:  Distributed Bug Tracker Extention for Mercurial
#      Author:  Jared Julien <jaredjulien@exsystems.net>
#   Copyright:  (c) 2010-2011 Michael Diamond <michael@digitalgemstones.com>
#               (c) 2022 Jared Julien, Nexteer Automotive
# ---------------------------------------------------------------------------------------------------------------------
"""b's business logic and programatic API."""

# ======================================================================================================================
# Import Statements
# ----------------------------------------------------------------------------------------------------------------------
import os
import re
import shutil
import subprocess
import time
from operator import itemgetter
from typing import Dict

from b import exceptions
from b import helpers




# ======================================================================================================================
# BugsDict Class
# ----------------------------------------------------------------------------------------------------------------------
class BugsDict(object):
    """A set of bugs, issues, and tasks, both finished and unfinished, for a given repository.

    The list's file is read from disk when initialized. The items can be written back out to disk with the write()
    function.

    You can specify any taskdir you want, but the intent is to work from the cwd and therefore anything calling this
    class ought to handle that change (normally to the repo root)
    """

    def __init__(self, bugsdir: str, user: str, editor: str, fast_add=False):
        """Initialize by reading the task files, if they exist."""
        self.bugsdir = bugsdir
        self.user = user
        self.editor = editor
        self.fast_add = fast_add
        self.file = 'bugs'
        self.detailsdir = 'details'
        self.last_added_id = None

        self.bugs = {}
        path = os.path.join(os.path.expanduser(str(self.bugsdir)), self.file)
        if os.path.exists(path):
            with open(path, 'r') as tfile:
                tlns = tfile.readlines()
                tls = [tl.strip() for tl in tlns if tl.strip()]
                tasks = map(helpers.task_from_taskline, tls)
                for task in tasks:
                    self.bugs[task['id']] = task


# ----------------------------------------------------------------------------------------------------------------------
    def list_templates(self, only_defaults: bool = False, only_custom: bool = False) -> Dict[str, str]:
        """Return a dictionary of available templates that can be used to create new bugs.

        Arguments:
            only_defaults: Indicates that only the default templates from within the b tool should be returned - none of
                the custom templates from the .bugs directory.

        Returns:
            A dictionary where keys correspond to the names of the available templates and the values are the paths to
            the corresponding template file(s).
        """
        assert not (only_defaults and only_custom)
        templates = {}

        def add_templates(base):
            directory = os.path.join(base, 'templates')
            if not os.path.exists(directory):
                return
            for template in os.listdir(directory):
                path = os.path.join(directory, template)
                name = os.path.splitext(template)[0]
                templates[name] = path

        # Start with a list of templates from the template folder within the `b` package.
        if not only_custom:
            add_templates('b')

        # Include/override with templates from the project directory when specified.
        if not only_defaults:
            add_templates(os.path.expanduser(str(self.bugsdir)))

        return templates


# ----------------------------------------------------------------------------------------------------------------------
    def customize_template(self, template: str) -> None:
        """Copy the specified template from the tool directory into the project '.bugs' directory and open the editor.
        """
        available = self.list_templates(only_defaults=True)
        if template not in available:
            message = f'The specified default template "{template}" does not exist.'
            message += '\nInvoke `b templates -d` for a list of templates available for customization.'
            raise exceptions.InvalidInput(message)
        source = available[template]
        destination_dir = os.path.join(os.path.expanduser(str(self.bugsdir)), 'templates')
        destination = os.path.join(destination_dir, os.path.basename(source))
        if os.path.exists(destination):
            raise exceptions.InvalidCommand(f'The specified template "{template}" already exists at {destination}.')
        os.makedirs(destination_dir, exist_ok=True)
        shutil.copyfile(source, destination)
        self._launch_editor(destination)


# ----------------------------------------------------------------------------------------------------------------------
    def edit_template(self, template: str) -> None:
        """Open the specified custom template for editing.

        Arguments:
            template: The CUSTOM template name to be edited.
        """
        available = self.list_templates(only_custom=True)
        if template not in available:
            message = f'Custom template {template} does not exit.'
            message += '\nDid you mean to `create` (-c) instead of `edit` (-e)?'
            raise exceptions.InvalidInput(message)
        path = available[template]
        self._launch_editor(path)



# ----------------------------------------------------------------------------------------------------------------------
    def write(self):
        """Flush the finished and unfinished tasks to the files on disk."""
        helpers.mkdir_p(self.bugsdir)
        path = os.path.join(os.path.expanduser(self.bugsdir), self.file)
        tasks = sorted(self.bugs.values(), key=itemgetter('id'))
        with open(path, 'w') as tfile:
            for taskline in helpers.tasklines_from_tasks(tasks):
                tfile.write(taskline)


# ----------------------------------------------------------------------------------------------------------------------
    def __getitem__(self, prefix):
        """Return the task with the given prefix.

        If more than one task matches the prefix an AmbiguousPrefix exception will be raised, unless the prefix is the
        entire ID of one task.

        If no tasks match the prefix an UnknownPrefix exception will be raised.
        """
        matched = [item for item in self.bugs.keys() if item.startswith(prefix)]
        if len(matched) == 1:
            return self.bugs[matched[0]]
        elif len(matched) == 0:
            raise exceptions.UnknownPrefix(prefix)
        else:
            matched = [item for item in self.bugs.keys() if item == prefix]
            if len(matched) == 1:
                return self.bugs[matched[0]]
            else:
                raise exceptions.AmbiguousPrefix(prefix)


# ----------------------------------------------------------------------------------------------------------------------
    def _get_details_path(self, full_id):
        """Returns the directory and file path to the details specified by id."""
        dirpath = os.path.join(self.bugsdir, self.detailsdir)
        path = os.path.join(dirpath, full_id + ".txt")
        return dirpath, path


# ----------------------------------------------------------------------------------------------------------------------
    def _make_details_file(self, full_id, template):
        """Create a details file for the given id."""
        (dirpath, path) = self._get_details_path(full_id)
        if not os.path.exists(dirpath):
            helpers.mkdir_p(dirpath)
        templates = self.list_templates()
        if not os.path.exists(path):
            try:
                template_path = templates[template]
            except KeyError as error:
                raise exceptions.TemplateError(f'Template "{template}" does not exist') from error
            shutil.copy(template_path, path)
        return path


# ----------------------------------------------------------------------------------------------------------------------
    def _users_list(self):
        """Returns a mapping of usernames to the number of open bugs assigned to that user."""
        open_tasks = [item['owner'] for item in self.bugs.values() if helpers.truth(item['open'])]
        closed = [item['owner'] for item in self.bugs.values() if not helpers.truth(item['open'])]
        users = {}
        for user in open_tasks:
            if user in users:
                users[user] += 1
            else:
                users[user] = 1
        for user in closed:
            if user not in users:
                users[user] = 0

        if '' in users:
            users['Nobody'] = users['']
            del users['']
        return users


# ----------------------------------------------------------------------------------------------------------------------
    def _get_user(self, user, force=False):
        """Given a user prefix, returns the appropriate username, or fails if the correct user cannot be identified.

        'me' is a special username which maps to the username specified when constructing the BugsDict.  'Nobody' (and
        prefixes of 'Nobody') is a special username which maps internally to the empty string, indicating no assignment.
        If force is true, the user 'Nobody' is used.  This is unadvisable, avoid forcing the username 'Nobody'.

        If force is true, it assumes user is not a prefix and should be assumed to exist already.
        """
        if user == 'me':
            return self.user
        if user == 'Nobody':
            return ''
        users = self._users_list().keys()
        if not force:
            if user not in users:
                usr = user.lower()
                matched = [u for u in users if u.lower().startswith(usr)]
                if len(matched) > 1:
                    raise exceptions.AmbiguousUser(user, matched)
                if len(matched) == 0:
                    raise exceptions.UnknownUser(user)
                user = matched[0]
            # Needed twice, since users can also type a prefix of "Nobody"
            if user == 'Nobody':
                return ''
        else:  # we're forcing a new username
            if '|' in user:
                raise exceptions.InvalidInput("Usernames cannot contain '|'.")
        return user


# ----------------------------------------------------------------------------------------------------------------------
    def id(self, prefix):
        """ Given a prefix, returns the full id of that bug."""
        return self[prefix]['id']


# ----------------------------------------------------------------------------------------------------------------------
    def add(self, text):
        """Adds a bug with no owner to the task list."""
        task_id = helpers.hash(text, self.user, str(time.time()))
        self.bugs[task_id] = {'id': task_id, 'open': 'True', 'owner': self.user,
                              'text': text, 'time': time.time()}
        self.last_added_id = task_id
        if self.fast_add:
            short_task_id = "%s..." % task_id[:10]
        else:
            prefix = helpers.prefixes(self.bugs.keys())[task_id]
            short_task_id = "%s:%s" % (prefix, task_id[len(prefix):10])
        return "Added bug %s" % short_task_id


# ----------------------------------------------------------------------------------------------------------------------
    def rename(self, prefix, text):
        """Renames the bug.

        If more than one task matches the prefix an AmbiguousPrefix exception will be raised, unless the prefix is the
        entire ID of one task.

        If no tasks match the prefix an UnknownPrefix exception will be raised.
        """
        task = self[prefix]
        if text.startswith('s/') or text.startswith('/'):
            text = re.sub('^s?/', '', text).rstrip('/')
            find, _, repl = text.partition('/')
            text = re.sub(find, repl, task['text'])

        task['text'] = text


# ----------------------------------------------------------------------------------------------------------------------
    def users(self):
        """Prints a list of users along with their number of open bugs."""
        users = self._users_list()
        if len(users) > 0:
            ulen = max([len(user) for user in users.keys()]) + 1
        else:
            ulen = 0
        out = "Username: Open Bugs\n"
        for (user, count) in users.items():
            out += "%s: %s\n" % (user, str(count).rjust(ulen - len(user)))
        return out


# ----------------------------------------------------------------------------------------------------------------------
    def assign(self, prefix, user, force=False):
        """Specifies a new owner of the bug.  Tries to guess the correct user, or warns if it cannot find an appropriate
        user.

        Using the -f flag will create a new user with that exact name, it will not try to guess, or warn the user.
        """
        task = self[prefix]
        user = self._get_user(user, force)
        task['owner'] = user
        if user == '':
            user = 'Nobody'
        return "Assigned %s: '%s' to %s" % (prefix, task['text'], user)


# ----------------------------------------------------------------------------------------------------------------------
    def details(self, prefix):
        """ Provides additional details on the requested bug.

        Metadata (like owner, and creation time) which are not stored in the details file are displayed along with the
        details.

        Sections (denoted by a [text] line) with no content are not displayed.
        """
        task = self[prefix]  # confirms prefix does exist
        path = self._get_details_path(task['id'])[1]
        if os.path.exists(path):
            with open(path) as f:
                text = f.read()

            text = re.sub("(?m)^#.*\n?", "", text)

            while True:
                oldtext = text
                retext = re.sub("\[\w+\]\s+\[", "[", text)
                text = retext
                if oldtext == retext:
                    break

            text = re.sub("\[\w+\]\s*$", "", text)
        else:
            text = 'No Details File Found.'

        header = "Title: %s\nID: %s\n" % (task['text'], task['id'])
        if not helpers.truth(task['open']):
            header = header + "*Resolved* "
        if task['owner'] != '':
            header = header + ("Owned By: %s\n" % task['owner'])
        header = header + ("Filed On: %s\n\n" % helpers.formatted_datetime(task['time']))
        text = header + text

        return text.strip()


# ----------------------------------------------------------------------------------------------------------------------
    def edit(self, prefix, template):
        """Allows the user to edit the details of the specified bug"""
        task = self[prefix]  # confirms prefix does exist
        path = self._get_details_path(task['id'])[1]
        if not os.path.exists(path):
            self._make_details_file(task['id'], template)
        self._launch_editor(path)

# ----------------------------------------------------------------------------------------------------------------------
    def _launch_editor(self, path: str) -> None:
        """Open the specified file in the editor specified by the user.

        Arguments:
            path: The path to the file to be edited.
        """
        subprocess.call("%s \"%s\"" % (self.editor, path), shell=True)


# ----------------------------------------------------------------------------------------------------------------------
    def comment(self, prefix, comment, template):
        """Allows the user to add a comment to the bug without launching an editor.

        If they have a username set, the comment will show who made it."""
        task = self[prefix]  # confirms prefix does exist
        path = self._get_details_path(task['id'])[1]
        if not os.path.exists(path):
            self._make_details_file(task['id'], template)

        # If the user has a known name, prepend that to the comment.
        if self.user != '':
            comment = "By: %s\n%s" % (self.user, comment)

        # Prepend a date/time to the comment.
        comment = "On: %s\n%s" % (helpers.formatted_datetime(), comment)

        # Write the comment out to the end of the file.  This is why the comments section must be at the end.
        with open(path, "a") as f:
            f.write("\n\n" + comment)


# ----------------------------------------------------------------------------------------------------------------------
    def resolve(self, prefix):
        """Marks a bug as resolved"""
        task = self[prefix]
        task['open'] = 'False'


# ----------------------------------------------------------------------------------------------------------------------
    def reopen(self, prefix):
        """Reopens a bug that was previously resolved"""
        task = self[prefix]
        task['open'] = 'True'


# ----------------------------------------------------------------------------------------------------------------------
    def list(self, is_open=True, owner='*', grep='', alpha=False, chrono=False, truncate=0):
        """Lists all bugs, applying the given filters"""
        tasks = dict(self.bugs.items())

        prefixes = helpers.prefixes(tasks).items()
        for task_id, prefix in prefixes:
            tasks[task_id]['prefix'] = prefix

        if owner != '*':
            owner = self._get_user(owner)

        small = [task for task in tasks.values()
                 if helpers.truth(task['open']) == is_open
                 and (owner == '*' or owner == task['owner'])
                 and (grep == '' or grep.lower() in task['text'].lower())]
        if len(small) > 0:
            plen = max([len(task['prefix']) for task in small])
        else:
            plen = 0
        out = ''
        if alpha:
            small = sorted(small, key=lambda x: x['text'].lower())
        if chrono:
            small = sorted(small, key=itemgetter('time'))
        for task in small:
            line = '%s - %s' % (task['prefix'].ljust(plen), task['text'])
            if 0 < truncate < len(line):
                line = line[:truncate - 4] + '...'
            out += line + '\n'
        return out + helpers.describe_print(len(small), is_open, owner, grep)




# End of File
