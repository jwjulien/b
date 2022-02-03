# ======================================================================================================================
#        File:  interface.py
#     Project:  B Bug Tracker
# Description:  Distributed Bug Tracker Extention for Mercurial
#      Author:  Jared Julien <jaredjulien@exsystems.net>
#   Copyright:  (c) 2010-2011 Michael Diamond <michael@digitalgemstones.com>
#               (c) 2022 Jared Julien, Nexteer Automotive
# ---------------------------------------------------------------------------------------------------------------------
"""Extensions that integrate b into Mercurial."""

# ======================================================================================================================
# Import Statements
# ----------------------------------------------------------------------------------------------------------------------
import errno
import os
import tempfile
import importlib_metadata
from mercurial.error import Abort
from mercurial import commands

from b import exceptions
from b import helpers
from b import decorators
from b.bugs_dict import BugsDict




# ======================================================================================================================
# Helpers
# ----------------------------------------------------------------------------------------------------------------------
def _track(ui, repo, path):
    """Adds new files to Mercurial."""
    if os.path.exists(path):
        ui.pushbuffer()
        commands.add(ui, repo, path.encode('utf-8'))
        ui.popbuffer()


# ----------------------------------------------------------------------------------------------------------------------
def _cat(ui, repo, path, todir, rev=None):
    ui.pushbuffer(error=True)
    success = commands.cat(ui, repo, path, rev=rev, output=os.path.join(todir, path))
    msg = ui.popbuffer()
    if success != 0:
        raise IOError(errno.ENOENT, "Failed to access %s at rev %s\nDetails: %s" % (path, rev, msg))




# ======================================================================================================================
# Command Line Interface
# ----------------------------------------------------------------------------------------------------------------------
class CLI(object):
    """Command line interface."""

    def __init__(self, ui, repo):
        self.ui = ui
        self.repo = repo
        self.bugsdir = helpers.bugs_dir(ui)

        self.user = self.ui.config(b"bugs", b"user", b'').decode('utf-8')
        if self.user == 'hg.user':
            ui.warn(b"No need to set bugs.user=hg.user in your hgrc - just remove this line\n")
            self.user = ''
        if not self.user:
            # Use Mercurial username if bugs.user is not set
            # not sure if there's a better way to optionally get the username
            try:
                self.user = self.ui.username().decode('utf-8')
            except Abort:
                pass

        self._bd = None
        self._revpath = None


# ----------------------------------------------------------------------------------------------------------------------
    def bd(self, opts):
        if self._bd:
            raise Exception("Don't construct the BugsDict more than once.")

        os.chdir(self.repo.root)

        # handle other revisions
        #
        # The methodology here is to use or create a directory in the user's /tmp directory for the given revision and
        # store whatever files are being accessed there, then simply set path to the temporary repodir
        if opts['rev']:
            # FIXME error on bad rev?
            rev = str(self.repo[opts['rev']])
            tempdir = tempfile.gettempdir()
            self._revpath = os.path.join(tempdir, 'b-' + rev)
            helpers.mkdir_p(os.path.join(self._revpath, self.bugsdir))
            relbugsdir = os.path.join(self.bugsdir, 'bugs')
            revbugsdir = os.path.join(self._revpath, relbugsdir)
            if not os.path.exists(revbugsdir):
                _cat(self.ui, self.repo, relbugsdir, self._revpath, rev)
            os.chdir(self._revpath)

        fast_add = self.ui.configbool(b"bugs", b"fast_add", False)
        self._bd = BugsDict(self.bugsdir, self.user, fast_add)
        return self._bd


# ----------------------------------------------------------------------------------------------------------------------
    def _cat_rev_details(self, task_id, rev):
        # Try to write the details file for this revision if the lookup fails, we don't need to worry about it, the
        # standard error handling will catch it and warn the user
        fullid = self._bd.id(task_id)
        detfile = os.path.join(self.bugsdir, 'details', fullid + '.txt')
        revdetfile = os.path.join(self._revpath, detfile)
        if not os.path.exists(revdetfile):
            helpers.mkdir_p(os.path.join(self._revpath, self.bugsdir, 'details'))
            os.chdir(self.repo.root)  # TODO rearrange so this isn't necessary
            _cat(self.ui, self.repo, detfile, self._revpath, rev)
            os.chdir(self._revpath)


# ----------------------------------------------------------------------------------------------------------------------
    def invoke(self, cmd, *args, **opts):
        commands = ['add', 'assign', 'comment', 'details', 'edit', 'help', 'id',
                    'list', 'rename', 'resolve', 'reopen', 'users', 'version']

        cmd = cmd.decode('utf-8')
        args = [arg.decode('utf-8') for arg in args]
        for key, value in opts.items():
            if isinstance(value, bytes):
                opts[key] = value.decode('utf-8')

        candidates = [c for c in commands if c.startswith(cmd)]
        exact_candidate = [c for c in candidates if c == cmd]
        if exact_candidate:
            pass  # already valid command
        elif len(candidates) > 1:
            raise exceptions.AmbiguousCommand(candidates)
        elif len(candidates) == 1:
            cmd = candidates[0]
        else:
            raise exceptions.UnknownCommand(cmd)

        getattr(self, cmd, None)(args, opts)

        # Add all new files to Mercurial - does not commit
        if not opts['rev']:
            _track(self.ui, self.repo, self.bugsdir)


# ----------------------------------------------------------------------------------------------------------------------
    @decorators.ValidOpts('edit')
    def add(self, args, opts):
        title = ' '.join(args).strip()
        if not title:
            raise exceptions.InvalidCommand("Must specify issue title")
        self.ui.write((self.bd(opts).add(title) + '\n').encode('utf-8'))
        self._bd.write()

        self._maybe_edit(self._bd.last_added_id, opts)


# ----------------------------------------------------------------------------------------------------------------------
    @decorators.ValidOpts('edit')
    @decorators.prefix_plus_args
    def rename(self, task_id, args, opts):
        title = ' '.join(args).strip()
        if not title:
            raise exceptions.InvalidCommand("Must specify issue title")
        self.bd(opts).rename(task_id, title)
        self._bd.write()

        self._maybe_edit(task_id, opts)


# ----------------------------------------------------------------------------------------------------------------------
    @decorators.ValidOpts('rev')
    @decorators.zero_args
    def users(self, opts):
        self.ui.write((self.bd(opts).users() + '\n').encode('utf-8'))


# ----------------------------------------------------------------------------------------------------------------------
    @decorators.ValidOpts('force', 'edit')
    @decorators.prefix_plus_args
    def assign(self, task_id, args, opts):
        if not args:
            raise exceptions.InvalidCommand("Must provide a username to assign")
        if len(args) > 1:
            raise exceptions.InvalidCommand("Unexpected arguments: %s" % args[1:])
        self.ui.write((self.bd(opts).assign(task_id, args[0], opts['force']) + '\n').encode('utf-8'))
        self._bd.write()

        self._maybe_edit(task_id, opts)


# ----------------------------------------------------------------------------------------------------------------------
    @decorators.ValidOpts('rev')
    @decorators.prefix_arg
    def details(self, task_id, opts):
        if opts['rev']:
            self._cat_rev_details(task_id, opts['rev'])
        self.ui.write((self.bd(opts).details(task_id) + '\n').encode('utf-8'))


# ----------------------------------------------------------------------------------------------------------------------
    @decorators.ValidOpts()
    @decorators.prefix_arg
    def edit(self, task_id, opts):
        self.bd(opts).edit(task_id, self.ui.geteditor().decode('utf-8'))


# ----------------------------------------------------------------------------------------------------------------------
    def _maybe_edit(self, task_id, opts):
        if opts['edit']:
            self._bd.edit(task_id, self.ui.geteditor().decode('utf-8'))


# ----------------------------------------------------------------------------------------------------------------------
    @decorators.ValidOpts('edit')
    @decorators.prefix_plus_args
    def comment(self, task_id, args, opts):
        comment = ' '.join(args).strip()
        if not comment and not opts['edit']:
            raise exceptions.InvalidCommand("Must include comment text in command or use --edit")
        self.bd(opts).comment(task_id, comment)

        self._maybe_edit(task_id, opts)


# ----------------------------------------------------------------------------------------------------------------------
    @decorators.ValidOpts('edit')
    @decorators.prefix_arg
    def resolve(self, task_id, opts):
        self.bd(opts).resolve(task_id)
        self._bd.write()

        self._maybe_edit(task_id, opts)


# ----------------------------------------------------------------------------------------------------------------------
    @decorators.ValidOpts('edit')
    @decorators.prefix_arg
    def reopen(self, task_id, opts):
        self.bd(opts).reopen(task_id)
        self._bd.write()

        self._maybe_edit(task_id, opts)


# ----------------------------------------------------------------------------------------------------------------------
    @decorators.ValidOpts('alpha', 'chrono', 'grep', 'owner', 'resolved', 'rev', 'truncate')
    @decorators.zero_args
    def list(self, opts):
        self.ui.write((self.bd(opts).list(
            not opts['resolved'],
            opts['owner'],
            opts['grep'],
            opts['alpha'],
            opts['chrono'],
            self.ui.termwidth() if opts['truncate'] else 0)
                      + '\n').encode('utf-8'))


# ----------------------------------------------------------------------------------------------------------------------
    @decorators.ValidOpts('rev')
    @decorators.prefix_arg
    def id(self, task_id, opts):
        self.ui.write((self.bd(opts).id(task_id) + '\n').encode('utf-8'))


# ----------------------------------------------------------------------------------------------------------------------
    @decorators.ValidOpts()
    @decorators.zero_args
    def help(self, _opts):
        commands.help_(self.ui, b'b')


# ----------------------------------------------------------------------------------------------------------------------
    @decorators.ValidOpts()
    @decorators.zero_args
    def version(self, _opts):
        self.ui.write(("b Version %s\n" % importlib_metadata.version('b')).encode('utf-8'))




# End of File
