Template Command
========================================================================================================================
`b` supports a somewhat rudimentary, though extensible, tempesting system through the use of the `templates` command.

To get a list of templates that are available, run:

    $ b templates

The output will list one template per line showing the template name and the path to the template file.

By default, `b` will list all of the templates that are available to the `add` command including overrides from the local .bugs/templates directory.  Use the `-d` switch to list only the "default" templates from the `b` package:

    $ b templates -d




Customize Template
------------------------------------------------------------------------------------------------------------------------
Templates can be added to the .bugs directory in a templates folder and customized on a per project basis.

Templates in the .bugs/template directory with the same name as a default template will override the default template.  For example, a template file ".bugs/templates/bug.bug.yaml" will be used when the user specifies the "bug" template, rather than the "bug.bug.yaml" located within the `b` package.

To customize a template, use the -c switch and specify the template file:

    $ b -c bug

`b` will then copy the "bug.bug.yaml" to the .bugs/templates directory and the local file can be adjusted for project-specific settings.

The name of the template may also be changed.  For example, if you wished to create a "task" template, simply create a new file at ".bugs/templates/task.bug.yaml" and populate it with your new task template content.  Then, issuing `b templates` should include your new "task" entry in it's list.




Edit Template
------------------------------------------------------------------------------------------------------------------------
To edit a custom template, you can either open the template file manually by browsing for it within the .bugs/templates directory, or use the `-e` switch:

    $ b templates -e bug

Which will open the template in the editor configured using the "editor" config option.
