Bug File Format
========================================================================================================================
Bugs in `b` are stored in the `.bugs` directory of each project.

Each bug resides in a single YAML format file with the ID of the bug as a filename and with a file extension of .bug.yaml.

A schema for these .bug.yaml files is located within the `b` component at "b/schema/bug.schema.json".  Most modern editors will allow you to setup a schema that works with files based upon their extension.  For example, to setup schema validation in VS Code for the .bugs in your project, add a Workspace Setting:

    {
        "yaml.schemas": {
            "C:/absolute/path/to/b/schema/bug.schema.json": "*.bug.yaml",
        }
    }

The bug files themselves are really just plain text.  This allows them to be edited using any text editor that you might prefer.
