# ======================================================================================================================
#        File:  migrations.py
#     Project:  B Bug Tracker
# Description:  Simple bug tracker
#      Author:  Jared Julien <jaredjulien@exsystems.net>
#   Copyright:  (c) 2010-2011 Michael Diamond <michael@digitalgemstones.com>
#               (c) 2022-2023 Jared Julien <jaredjulien@exsystems.net>
# ---------------------------------------------------------------------------------------------------------------------
"""Exceptions used by b."""

# ======================================================================================================================
# Imports
# ----------------------------------------------------------------------------------------------------------------------
import os
import re
import logging
from glob import glob




# ======================================================================================================================
# Migrations
# ----------------------------------------------------------------------------------------------------------------------
def details_to_markdown(bugsdir: str):
    """Migrate the details files from .txt format to .md format and swap the headers inside each."""
    logging.info('Performing migration from .txt format detail files to .md format.')
    for txt_path in glob(os.path.join(bugsdir, 'details', '*.txt')):
        logging.info('Migrating %s from .txt to .md', txt_path)
        md_path = os.path.splitext(txt_path)[0] + '.md'
        with open(txt_path, 'r') as handle:
            contents = handle.read()

        # Change the headers inside of the files from [box style] to `## Markdown Style`.
        def replace(match) -> str:
            return '## ' + match.group(1).title()
        contents = re.sub(r'^\[(.+)\]$', replace, contents, flags=re.MULTILINE)

        # Remove the original .txt file.
        logging.debug('Deleting file %s', txt_path)
        os.remove(txt_path)

        # Write Markdown to new filename.
        logging.debug('Writing contents to new file: %s', md_path)
        with open(md_path, 'w') as handle:
            handle.write(contents)




# End of File
