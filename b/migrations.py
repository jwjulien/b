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
import shutil
import logging
from glob import glob

from rich import print
import yaml




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


# ----------------------------------------------------------------------------------------------------------------------
def details_to_yaml(bugsdir: str):
    """Migrate the details files from Markdown format to YAML format.

    The section headings become keys and the section content becomes string values.
    """
    logging.info('Performing migration from .md format detail files to .yaml format.')
    for md_path in glob(os.path.join(bugsdir, 'details', '*.md')):
        # logging.info('Migrating %s from .md to .yaml', md_path)
        with open(md_path, 'r') as handle:
            contents = handle.read()

        # Parse sections into dict.
        data = {
            'type': 'Bug'
        }
        for title, content in re.findall(r'^##+ +(.+?)$(.*?)(?=^##|\Z)', contents, re.MULTILINE | re.DOTALL):
            title = title.lower().replace(' ', '_')
            if title != 'comments':
                data[title] = content.strip()

                if title == 'why':
                    data['type'] = 'Feature'
            else:
                comments = []
                pattern = r'---+\[ *(.+?) +on +(.+?) *\]-+\n(.+?)(?:\n-|\Z)'
                for author, date, text in re.findall(pattern, content, re.DOTALL):
                    comments.append({
                        'author': author,
                        'date': date,
                        'text': text
                    })
                if comments:
                    data['comments'] = comments

        def str_presenter(dumper, data):
            if len(data.splitlines()) > 1:  # check for multiline string
                return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
            return dumper.represent_scalar('tag:yaml.org,2002:str', data)
        yaml.representer.SafeRepresenter.add_representer(str, str_presenter)

        # Write YAML to new filename.
        yaml_path = os.path.splitext(md_path)[0] + '.bug.yaml'
        if os.path.exists(yaml_path):
            logging.error('YAML already exists at %s', yaml_path)
            continue
        logging.debug('Writing YAML contents to %s', yaml_path)
        with open(yaml_path, 'w') as handle:
            yaml.safe_dump(data, handle, sort_keys=False)

        # Remove the original .md file.
        logging.debug('Deleting original .md file: %s', md_path)
        os.remove(md_path)


# ----------------------------------------------------------------------------------------------------------------------
def move_details_to_bugs_root(bugsdir: str):
    """Relocate the details files from the "details" subdirectory into the root of the .bugs folder."""
    logging.info('Migrating details into .bugs root directory.')
    source = os.path.join(bugsdir, 'details')
    if os.path.exists(source):
        for filename in os.listdir(source):
            logging.debug('Moving %s from %s to %s', filename, source, bugsdir)
            shutil.move(os.path.join(source, filename), bugsdir)

    logging.debug('Removing "details" directory.')
    os.rmdir(source)




# End of File
