b, A distributed bug tracker
========================================================================================================================
This version of `b` was forked from [foss.heptapod.net](https://foss.heptapod.net/mercurial/b).  Originally with only minor modifications, but now it's likely safer to say that this tool simply took inspiration from B.

So, with that stated, full credit for the inspiration for this tool goes to Michael Diamond.  Thank you for taking the time and investing the effort to create `b`, without which this tool I love wouldn't likely exist.

The original purpose of B was to serve as a low-feature stand-in for a real, convoluted bug tracking system.  I loved that concept, but have taken the tool much further; much beyond the original, modest scope to the point of adding many features and capabilities to rival those of a fully fledged bug tracking system, but still in a distributed package.

- Now a standalone command-line tool with no dependency upon Mercurial allowing it to be used with any VCS.
    - See the available [commands](https://jwjulien.github.io/b/commands/index) for more info.
- Supports Rich output to make interacting a bit more friendly.
- Supports bug templates to offer a better starting point for new bugs.
    - Also supports customization at the project level - see [templates](https://jwjulien.github.io/b/commands/templates) for more info.
- Handles it's own configuration, outside of Mercurial, in support of independence.
    - See [config command](https://jwjulien.github.io/b/commands/config) for more info about the available configuration options and config file location.

See the [installation](https://jwjulien.github.io/b/installation) and [getting started](https://jwjulien.github.io/b/getting_started) guides for help with installing and using `b` on your project.




Introduction
------------------------------------------------------------------------------------------------------------------------
`b` is a tool for tracking bugs and open issues that works with any distributed version control system.  Bugs are tracked as YAML files (i.e., nearly plain text) directly in the `.bugs` directory of the project.  That means that when a user adds a new bug they will need to add it into the VCS and commit it.  Then, all changes made to the bug during the process of diagnosis and resolution will be tracked.

The use of YAML files means that bugs can be opened directly in an editor and manually edited.  In fact, `b` itself does not the ability to set many of the attributes in the bug files from the command line.  It is expected that users will manually open bugs (optionally using the `edit` command) and edit their contents directly.  For more info about the format of these YAML files and the supporting schema, have a look at [the bug file format](https://jwjulien.github.io/b/bugs).




Some Suggested Use Cases
------------------------------------------------------------------------------------------------------------------------
Small scripts and tasks deserve version control, even if they're never going to be distributed elsewhere.  This is easy with Mercurial.  With `b` installed you get a fully functional bug tracker along with your VCS, no additional setup required! As soon as you install `b`, every repository on your machine now has issue tracking functionality ready to use.

Working on a project with a few other team members is ideal for `b`, it's powerful enough to let everyone track what they need to do, and allow everyone to contribute what they can to any of the bugs on file.  They can search titles for matching bugs, and even grep through the details directory to find details matching what they're looking for.
