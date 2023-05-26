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
from glob import glob
import shutil
import subprocess
from datetime import datetime
from typing import Dict

import yaml
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

        # TODO: Don't load all bugs by default.  Load them on demand to be more resource efficient.
        # If the bugs directory exists, then load the existing bugs.
        self.bugs: Dict[str, Dict[str, any]] = {}
        if os.path.exists(self.bugsdir):
            for filename in glob(os.path.join(self.bugsdir, '*.bug.yaml')):
                id = os.path.basename(filename).split('.', 1)[0]
                with open(filename, 'r') as handle:
                    data = yaml.safe_load(handle)
                data['id'] = id
                self.bugs[id] = data


# ----------------------------------------------------------------------------------------------------------------------
    def _write(self, bug: Dict[str, any]):
        """Flush the finished and unfinished tasks to the files on disk."""
        if not os.path.exists(self.bugsdir):
            raise exceptions.NotInitialized('No bugs directory found for the current directory')

        def str_presenter(dumper, data):
            if len(data.splitlines()) > 1:  # check for multiline string
                return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
            return dumper.represent_scalar('tag:yaml.org,2002:str', data)
        yaml.representer.SafeRepresenter.add_representer(str, str_presenter)

        filename = self._get_details_path(bug['id'])
        bug = dict(bug)
        del bug['id']
        with open(filename, 'w') as handle:
            # TODO: What about sorting the keys in our desired order here?
            # TODO: We should probably warn when the bug violates the schema too.
            yaml.safe_dump(bug, handle, sort_keys=False)



# ----------------------------------------------------------------------------------------------------------------------
    def initialize(self, force: bool):
        """Initialize a new bugs directory at the current working directory."""
        # Warn the user about creating a bugs directory if one was already found in a folder above.
        # Using the "-f" argument to "force" the creation will put a new bugs directory here too.
        if os.path.exists(self.bugsdir) and not force:
            message = f'Bugs directory already exists at {self.bugsdir} - use -f to force creation here'
            raise exceptions.AlreadyInitialized(message)

        # Attempt to make the directory as specified, if it exists the exception will be morphed into AlreadyExists.
        try:
            os.makedirs(self.bugsdir)
        except OSError as error:
            raise exceptions.AlreadyInitialized('Bugs directory already exists in this exact location') from error

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
                name = template.rsplit('.', 2)[0]
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
        return os.path.join(self.bugsdir, full_id + ".bug.yaml")


# ----------------------------------------------------------------------------------------------------------------------
    def _prefixes(self):
        """Return a mapping of elements to their unique prefix in O(n) time.

        This is much faster than the native t function, which takes O(n^2) time.

        Each prefix will be the shortest possible substring of the element that
        can uniquely identify it among the given group of elements.

        If an element is entirely a substring of another, the whole string will be
        the prefix.
        """
        prefixes = {}
        ids = [file.split('.', 1)[0] for file in os.listdir(self.bugsdir) if file.endswith('.bug.yaml')]
        for id in ids:
            for idx in range(1, len(id)):
                prefix = id[:idx]
                matches = [id for id in ids if id.startswith(prefix)]
                if len(matches) == 1:
                    prefixes[id] = prefix
                    break

        return prefixes


# ----------------------------------------------------------------------------------------------------------------------
    def _users_list(self):
        """Returns a mapping of usernames to the number of open bugs assigned to that user."""
        open_owners = [bug.get('owner') for bug in self.bugs.values() if bug['open']]
        closed_owners = [bug.get('owner') for bug in self.bugs.values() if not bug['open']]
        owners = set(open_owners + closed_owners)
        print(owners)
        counts = {}
        for bug in self.bugs.values():
            owner = bug.get('owner')
            if owner not in counts:
                counts[owner] = 0
            if bug['open']:
                counts[owner] += 1
        print(list(counts.items()))
        counts = dict(sorted(list(counts.items()), key=lambda count: count[1], reverse=True))
        return counts


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
                matched = [u for u in users if u and u.lower().startswith(usr)]
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
        # Add the new detail file from template.
        templates = self.list_templates()
        try:
            template_path = templates[template]
        except KeyError as error:
            message = f'Template "{template}" does not exist - use `template` command to view available templates'
            raise exceptions.TemplateError(message) from error

        # Load YAML from template.
        with open(template_path, 'r') as handle:
            bug = yaml.safe_load(handle)

        full_id = helpers.make_id(self.bugs.keys())

        # Populate default attributes.
        bug['id'] = full_id
        bug['title'] = title
        bug['entered'] = datetime.now().astimezone().isoformat()
        bug['author'] = self.user
        bug['open'] = True

        self._write(bug)

        prefix = self._prefixes()[full_id]
        short_task_id = "[bold cyan]%s[/]:[yellow]%s[/]" % (prefix, full_id[len(prefix):])
        print(f"Added bug {short_task_id}")

        return full_id


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
        self._write(bug)


# ----------------------------------------------------------------------------------------------------------------------
    def users(self):
        """Prints a list of users along with their number of open bugs."""
        users = self._users_list()
        width = max([len(user) for user in users.keys() if user is not None]) + 1 if len(users) > 0 else 0
        print(f"{'Username'.rjust(width)}: Open Bugs")
        for (user, count) in users.items():
            print(f"{str(user).rjust(width)}: {count}")


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

        self._write(bug)
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
        if bug.get('owner'):
            print(f"Owned by: [magenta]{bug['owner']}[/]")

        Console().print(f"Filed on: {bug['entered']}", highlight=False)

        # TODO: Print comments.
        # TODO: Print arbitrary remaining sections.



# ----------------------------------------------------------------------------------------------------------------------
    def edit(self, prefix):
        """Allows the user to edit the details of the specified bug"""
        bug = self[prefix]  # confirms prefix does exist
        path = self._get_details_path(bug['id'])
        self._launch_editor(path)


# ----------------------------------------------------------------------------------------------------------------------
    def _launch_editor(self, path: str) -> None:
        """Open the specified file in the editor specified by the user.

        Arguments:
            path: The path to the file to be edited.
        """
        subprocess.call("%s \"%s\"" % (self.editor, path), shell=True)


# ----------------------------------------------------------------------------------------------------------------------
    def comment(self, prefix, text):
        """Allows the user to add a comment to the bug without launching an editor.

        If they have a username set, the comment will show who made it."""
        bug = self[prefix]  # confirms prefix does exist

        # Add a new comments section to the bug if it doesn't already exist.
        if 'comments' not in bug:
            bug['comments'] = []

        # Append this comment to the bug.
        bug['comments'].append({
            'author': self.user,
            'date': datetime.now().astimezone().isoformat(),
            'text': text
        })

        # Write the bug back to file.
        self._write(bug)


# ----------------------------------------------------------------------------------------------------------------------
    def resolve(self, prefix):
        """Marks a bug as resolved"""
        bug = self[prefix]
        bug['open'] = False
        self._write(bug)


# ----------------------------------------------------------------------------------------------------------------------
    def reopen(self, prefix):
        """Reopens a bug that was previously resolved"""
        bug = self[prefix]
        bug['open'] = True
        self._write(bug)


# ----------------------------------------------------------------------------------------------------------------------
    def list(self, is_open=True, owner='*', grep='', alpha=False, chrono=False, truncate=0):
        """Lists all bugs, applying the given filters"""
        if not os.path.exists(self.bugsdir):
            raise exceptions.NotInitialized('No bugs directory found - use `init` command first')

        bugs = dict(self.bugs.items())

        prefixes = self._prefixes()

        if owner != '*':
            owner = self._get_user(owner)

        filtered = [bug for bug in bugs.values()
                    if bug['open'] == is_open
                    and (owner == '*' or owner == bug.get('owner'))
                    and (grep == '' or grep.lower() in bug['title'].lower())]

        if len(filtered) > 0:
            plen = max([len(prefixes[bug['id']]) for bug in filtered])
        else:
            plen = 0

        if alpha:
            filtered = sorted(filtered, key=lambda x: x.title.lower())

        if chrono:
            filtered = sorted(filtered, key=lambda bug: bug['entered'])

        for bug in filtered:
            line = '[bold cyan]%s[/bold cyan] - %s' % (prefixes[bug['id']].rjust(plen), bug['title'])
            if 0 < truncate < len(line):
                line = line[:truncate - 4] + '...'
            print(line)

        print(helpers.describe_print(len(filtered), is_open, owner, grep))


# ----------------------------------------------------------------------------------------------------------------------
    def migrate(self) -> None:
        """Migrate the current bugs directory to the latest version."""
        migrations.details_to_markdown(self.bugsdir)
        migrations.details_to_yaml(self.bugsdir)
        migrations.move_details_to_bugs_root(self.bugsdir)
        migrations.bug_dict_into_yaml_details(self.bugsdir)




# End of File
