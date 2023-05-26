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
from datetime import datetime

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



# ----------------------------------------------------------------------------------------------------------------------
def bug_dict_into_yaml_details(bugsdir: str):
    """Migrate the details from the dugs dictionary file into the individual bugs YAML files."""
    logging.info('Migrating details from bugs dictionary into individual YAML files.')
    bugs_filename = os.path.join(bugsdir, 'bugs')
    if not os.path.exists(bugs_filename):
        logging.debug('No bugs dictionary file found, nothing to do.')
        return

    # Read out bug info from dictionary file.
    with open(bugs_filename, 'r') as handle:
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
        bugs.append(meta)
    logging.debug('Found %d bugs in the dictionary.', len(bugs))

    # Handling for multiline strings.
    def str_presenter(dumper, data):
        if len(data.splitlines()) > 1:  # check for multiline string
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)
    yaml.representer.SafeRepresenter.add_representer(str, str_presenter)

    # Write bugs into YAML files.
    for bug in bugs:
        # The YAML filename contains the ID, lets not duplicate it inside the file.
        id = bug['id']
        del bug['id']

        # Make the open attribute boolean
        bug['open'] = bug['open'].lower() == 'true'

        # Switch from timestamp to entered date.
        if 'time' in bug:
            bug['entered'] = datetime.fromtimestamp(float(bug['time'])).astimezone().isoformat()
            del bug['time']

        # Remove the owner if not assigned.
        if 'owner' in bug and not bug['owner']:
            del bug['owner']

        # Merge with existing, if details YAML exists.
        yaml_file = os.path.join(bugsdir, id + '.bug.yaml')
        if os.path.exists(yaml_file):
            logging.debug('Updating %s with data from dictionary.', yaml_file)
            with open(yaml_file, 'r') as handle:
                bug.update(yaml.safe_load(handle))
        else:
            logging.debug('Creating new YAML file for bug %s', id)

        # Write aggregated output to YAML file.
        with open(yaml_file, 'w') as handle:
            yaml.safe_dump(bug, handle, sort_keys=False)

    logging.debug('Merge complete - removing now obsolete dictionary file.')
    os.remove(bugs_filename)




# End of File
