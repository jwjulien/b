# ======================================================================================================================
#        File:  bugs.py
#     Project:  B Bug Tracker
# Description:  Simple bug tracker
#      Author:  Jared Julien <jaredjulien@exsystems.net>
#   Copyright:  (c) 2010-2011 Michael Diamond <michael@digitalgemstones.com>
#               (c) 2022-2023 Jared Julien <jaredjulien@exsystems.net>
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
from typing import Dict

from rich import print
from rich.console import Console

from b import exceptions, helpers, migrations




# ======================================================================================================================
# Tracker Class
# ----------------------------------------------------------------------------------------------------------------------
class Tracker:
    """A set of bugs, issues, and tasks, both finished and unfinished, for a given repository.

    The list's file is read from disk when initialized. The items can be written back out to disk with the write()
    function.

    You can specify any taskdir you want, but the intent is to work from the cwd and therefore anything calling this
    class ought to handle that change (normally to the repo root)
    """

    def __init__(self, bugsdir: str, user: str, editor: str):
        """Initialize by reading the task files, if they exist."""
        self.user = user
        self.editor = editor

        self.last_added_id = None

        def climb_tree(reference) -> str:
            working = os.getcwd()
            while True:
                test = os.path.join(working, reference)
                if os.path.exists(test):
                    return test

                # Step up one directory.
                new = os.path.dirname(working)
                if new == working:
                    # Bail out if we're at the top of the tree.
                    return reference
                working = new

        bugsdir = os.path.expanduser(bugsdir)
        self.bugsdir = bugsdir if os.path.isabs(os.path.expanduser(bugsdir)) else climb_tree(bugsdir)

        # If the bugs directory exists, then load the existing bugs.
        self.bugs: Dict[str, Dict[str, any]] = {}
        self.bugs_filename = None
        if self.bugsdir is not None and os.path.exists(self.bugsdir):
            self.bugs_filename = os.path.join(self.bugsdir, 'bugs')
            if os.path.exists(self.bugs_filename):
                with open(self.bugs_filename, 'r') as handle:
                    lines = handle.readlines()
                bugs = []
                for line in lines:
                    meta = {}
                    if '|' in line:
                        title, other = line.rsplit('|', 1)
                        meta['title'] = title.strip()
                        for piece in other.strip().split(','):
                            label, data = piece.split(':', 1)
                            meta[label.strip()] = data.strip()
                    else:
                        meta['title'] = line.strip()

                    bugs.append({
                        'title': title.strip(),
                        'id': meta.get('id', helpers.make_id()),
                        'open': bool(meta.get('open', '').lower() != 'false'),
                        'entered': meta.get('time', time.time()),
                        'owner': meta.get('owner')
                    })
                self.bugs = dict((bug['id'], bug) for bug in bugs)


# ----------------------------------------------------------------------------------------------------------------------
    def _write(self):
        """Flush the finished and unfinished tasks to the files on disk."""
        if self.bugs_filename is None:
            raise exceptions.NotInitialized('No bugs directory found for the current directory')
        with open(self.bugs_filename, 'w') as tfile:
            for bug in sorted(self.bugs.values(), key=lambda bug: bug['id']):
                attributes = f"id:{bug['id']},open:{bug['open']},time:{bug['entered']},owner:{bug['owner']}"
                tfile.write(f"{bug['title'].ljust(60)} | {attributes}")



# ----------------------------------------------------------------------------------------------------------------------
    def initialize(self, force: bool):
        """Initialize a new bugs directory at the current working directory."""
        # Warn the user about creating a bugs directory if one was already found in a folder above.
        # Using the "-f" argument to "force" the creation will put a new bugs directory here too.
        if self.bugs_filename is not None and not force:
            message = f'Bugs directory already exists at {self.bugs_filename} - use -f to force creation here'
            raise exceptions.AlreadyInitialized(message)

        # Attempt to make the directory as specified, if it exists the exception will be morphed into AlreadyExists.
        try:
            os.makedirs(self.bugsdir)
        except OSError as error:
            raise exceptions.AlreadyInitialized('Bugs directory already exists in this exact location') from error

        # Set the path for the bugs directory and dictionary file and write it.  File will be empty for now.
        self.bugs_filename = os.path.join(self.bugsdir, 'bugs')
        self._write()

        print(f'Initialized a bugs directory at "{os.path.abspath(self.bugsdir)}"')


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
    def __getitem__(self, prefix):
        """Return the bug with the given prefix.

        If more than one bug matches the prefix an AmbiguousPrefix exception will be raised, unless the prefix is the
        entire ID of one bug.

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
        dirpath = os.path.join(self.bugsdir, 'details')
        path = os.path.join(dirpath, full_id + ".bug.yaml")
        return dirpath, path


# ----------------------------------------------------------------------------------------------------------------------
    def _make_details_file(self, full_id, template):
        """Create a details file for the given id."""
        # Default to the "bug" template when the user didn't specify.
        if template is None:
            template = 'bug'

        # Generate the directory path for detail files if it doesn't exist.
        (dirpath, path) = self._get_details_path(full_id)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)

        # Add the new detail file from template.
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
        open_tasks = [bug['owner'] for bug in self.bugs.values() if bug['open']]
        closed = [bug['owner'] for bug in self.bugs.values() if not bug['open']]
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
            users['*unassigned*'] = users['']
            del users['']
        return users


# ----------------------------------------------------------------------------------------------------------------------
    def _get_user(self, user, force=False):
        """Given a user prefix, returns the appropriate username, or fails if the correct user cannot be identified.

        'me' is a special username which maps to the username specified when constructing the Bugs.  'Nobody' (and
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
        """Given a prefix, returns the full id of that bug."""
        print(self[prefix].id)


# ----------------------------------------------------------------------------------------------------------------------
    def add(self, title, template):
        """Adds a new bug to the list."""
        bug = {
            'title': title,
            'id': helpers.make_id(self.bugs.keys()),
            'open': True,
            'owner': None
        }
        self.bugs[bug['id']] = bug

        self.last_added_id = bug['id']
        prefix = helpers.prefixes(self.bugs.keys())[bug['id']]
        short_task_id = "[bold cyan]%s[/]:[yellow]%s[/]" % (prefix, bug['id'][len(prefix):10])
        self._write()

        # If the user specified a template then add a detail file now.
        if template is not None:
            self._make_details_file(bug['id'], template)

        print(f"Added bug {short_task_id}")


# ----------------------------------------------------------------------------------------------------------------------
    def rename(self, prefix, title):
        """Renames the bug.

        If more than one task matches the prefix an AmbiguousPrefix exception will be raised, unless the prefix is the
        entire ID of one task.

        If no tasks match the prefix an UnknownPrefix exception will be raised.
        """
        bug = self[prefix]
        if title.startswith('s/') or title.startswith('/'):
            title = re.sub('^s?/', '', title).rstrip('/')
            find, _, repl = title.partition('/')
            title = re.sub(find, repl, bug['title'])

        bug['title'] = title
        self._write()


# ----------------------------------------------------------------------------------------------------------------------
    def users(self):
        """Prints a list of users along with their number of open bugs."""
        users = self._users_list()
        if len(users) > 0:
            ulen = max([len(user) for user in users.keys()]) + 1
        else:
            ulen = 0
        print("Username: Open Bugs")
        for (user, count) in users.items():
            print(f"{user}: {str(count).rjust(ulen - len(user))}")


# ----------------------------------------------------------------------------------------------------------------------
    def assign(self, prefix, user, force=False):
        """Specifies a new owner of the bug.  Tries to guess the correct user, or warns if it cannot find an appropriate
        user.

        Using the -f flag will create a new user with that exact name, it will not try to guess, or warn the user.
        """
        bug = self[prefix]
        user = self._get_user(user, force)
        bug['owner'] = user

        if user == '':
            user = 'Nobody'

        self._write()
        print(f"Assigned {prefix}: '{bug['title']}' to {user}")


# ----------------------------------------------------------------------------------------------------------------------
    def details(self, prefix):
        """Provides additional details on the requested bug.

        Metadata (like owner, and creation time) which are not stored in the details file are displayed along with the
        details.

        Sections with no content are not displayed.
        """
        bug = self[prefix]  # confirms prefix does exist

        print(f"Title: [{'red' if bug['open'] else 'green'}]{bug['title']}")

        print(f"ID: [bold cyan]{prefix}[/]:[yellow]{bug['id'][len(prefix):]}")

        print(f"Status: [{'red' if bug['open'] else 'green'}]{'Open' if bug['open'] else 'Resolved'}")

        if bug['owner'] != '':
            print(f"Owned by: [magenta]{bug['owner']}[/]")

        Console().print(f"Filed on: {helpers.formatted_datetime(bug['entered'])}", highlight=False)

        path = self._get_details_path(bug['id'])[1]
        if os.path.exists(path):
            with open(path) as f:
                details = f.read()

            # Strip comments.
            details = re.sub("(?m)^#.*\n?", "", details)

            # Remove empty sections.
            while True:
                previous = details
                details = re.sub("\[\w+\]\s+\[", "[", details)
                if previous == details:
                    break

            # Remove, possibly, empty last section.
            details = re.sub("\[\w+\]\s*$", "", details)

            # Escape the section headers for Rich and add some color.
            details = '\n' + details
            details = re.sub('\n\[(.+?)\]', r'\n[blue]\\[\1][/]', details)

            # Reduce many (3+) blank lines down to two maximum.
            details = re.sub('\n\n+', '\n\n', details)

            print(details.strip())
        else:
            print('No additional details file found.')



# ----------------------------------------------------------------------------------------------------------------------
    def edit(self, prefix, template):
        """Allows the user to edit the details of the specified bug"""
        bug = self[prefix]  # confirms prefix does exist
        path = self._get_details_path(bug['id'])[1]
        if not os.path.exists(path):
            self._make_details_file(bug['id'], template)
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
        bug = self[prefix]  # confirms prefix does exist
        path = self._get_details_path(bug['id'])[1]
        if not os.path.exists(path):
            self._make_details_file(bug['id'], template)

        title = helpers.formatted_datetime()

        # If the user has a known name, prepend that to the title.
        if self.user != '':
            title = f'{self.user} on {title}'

        # Assemble the comment.
        comment = f'\n### {title}\n{comment}\n\n'

        # Insert the comment into the comments section.
        with open(path, "r") as handle:
            contents = handle.read()

        # If a comments section exists, then insert this comment at the end of that section.
        if '\n[comments]\n' in contents:
            find = r'(\n## Comments\n.*?)\n*(\n#+ |\Z)'
            replace = fr'\1\n\n{comment}\2'
            changed = re.sub(find, replace, contents, flags=re.DOTALL | re.MULTILINE)

            # Make sure that the comment was actually injected.
            assert changed != contents

            with open(path, "w") as handle:
                handle.write(changed)

        # If no comments section exists then append it instead.
        else:
            with open(path, 'a') as handle:
                handle.write(f'\n\n[comments]{comment}')


# ----------------------------------------------------------------------------------------------------------------------
    def resolve(self, prefix):
        """Marks a bug as resolved"""
        bug = self[prefix]
        bug['open'] = False
        self._write()


# ----------------------------------------------------------------------------------------------------------------------
    def reopen(self, prefix):
        """Reopens a bug that was previously resolved"""
        bug = self[prefix]
        bug['open'] = True
        self._write()


# ----------------------------------------------------------------------------------------------------------------------
    def list(self, is_open=True, owner='*', grep='', alpha=False, chrono=False, truncate=0):
        """Lists all bugs, applying the given filters"""
        bugs = dict(self.bugs.items())

        prefixes = helpers.prefixes(bugs).items()
        for id, prefix in prefixes:
            bugs[id]['prefix'] = prefix

        if owner != '*':
            owner = self._get_user(owner)

        filtered = [bug for bug in bugs.values()
                    if bug['open'] == is_open
                    and (owner == '*' or owner == bug['owner'])
                    and (grep == '' or grep.lower() in bug['title'].lower())]

        if len(filtered) > 0:
            plen = max([len(bug['prefix']) for bug in filtered])
        else:
            plen = 0

        if alpha:
            filtered = sorted(filtered, key=lambda x: x.title.lower())

        if chrono:
            filtered = sorted(filtered, key=lambda bug: bug['entered'])

        for bug in filtered:
            line = '[bold cyan]%s[/bold cyan] - %s' % (bug['prefix'].rjust(plen), bug['title'])
            if 0 < truncate < len(line):
                line = line[:truncate - 4] + '...'
            print(line)

        print(helpers.describe_print(len(filtered), is_open, owner, grep))


# ----------------------------------------------------------------------------------------------------------------------
    def migrate(self) -> None:
        """Migrate the current bugs directory to the latest version."""
        migrations.details_to_markdown(self.bugsdir)
        migrations.details_to_yaml(self.bugsdir)
        # migrations.move_details_to_bugs_root(self.bugsdir)
        # migrations.bug_dict_into_yaml_details(self.bugs_filename, self.bugsdir)




# End of File
