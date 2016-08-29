import logging
import markdown2
import textwrap

from xblock.core import XBlock
from xblock.fields import Scope, String, List
from xblock.fragment import Fragment
from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable import StudioEditableXBlockMixin

log = logging.getLogger(__name__)
loader = ResourceLoader(__name__)


class MarkdownXBlock(StudioEditableXBlockMixin, XBlock):
    """
    Displays markdown content as HTML

    """
    display_name = String(
        help="This name appears in the horizontal navigation at the top of the page.",
        default="Markdown",
        scope=Scope.settings)
    filename = String(
        help="Relative path to a markdown file uploaded to the static store.  For example, \"markdown_file.md\".",
        default="",
        scope=Scope.content)
    content = String(
        help="Markdown content to display for this module.",
        default=u"",
        multiline_editor=True,
        scope=Scope.content)
    extras = List(
        help="Markdown2 module extras to turn on for the instance.",
        list_style="set",
        list_values_provider=lambda _: [
            # Taken from https://github.com/trentm/python-markdown2/wiki/Extras
            {"display_name": "Code Friendly", "value": "code-friendly"},
            {"display_name": "Fenced Code Blocks", "value": "fenced-code-blocks"},
            {"display_name": "Footnotes", "value": "footnotes"},
            {"display_name": "GFM Tables", "value": "tables"},
            {"display_name": "File Variables", "value": "use-file-vars"},
            {"display_name": "Cuddled lists", "value": "cuddled-lists"},
            {"display_name": "Google Code Wiki Tables", "value": "wiki-tables"},
            {"display_name": "Header IDs", "value": "header-ids"},
            {"display_name": "HTML classes", "value": "html-classes"},
            {"display_name": "Link patterns", "value": "link-patterns"},
            {"display_name": "Markdown in HTML", "value": "markdown-in-html"},
            {"display_name": "Metadata", "value": "metadata"},
            {"display_name": "No Follow", "value": "nofollow"},
            {"display_name": "Pyshell", "value": "pyshell"},
            {"display_name": "SmartyPants", "value": "smarty-pants"},
            {"display_name": "Spoiler Block", "value": "spoiler"},
            {"display_name": "Table of Contents", "value": "toc"},
            {"display_name": "Twitter Tag Friendly", "value": "tag-friendly"},
            {"display_name": "XML", "value": "xml"},
        ],
        default=[
            "code-friendly",
            "fenced-code-blocks",
            "footnotes",
            "tables",
            "use-file-vars",
        ],
        scope=Scope.content)

    editable_fields = (
        'display_name',
        'filename',
        'content',
        'extras')

    @classmethod
    def parse_xml(cls, node, runtime, keys, id_generator):
        """
        Parses the source XML in a way that preserves indenting, needed for markdown.

        """
        block = runtime.construct_xblock_from_class(cls, keys)

        # Load the data
        for name, value in node.items():
            if name in block.fields:
                value = (block.fields[name]).from_string(value)
                setattr(block, name, value)

        # Load content
        text = node.text
        if text:
            # Fix up whitespace.
            if text[0] == "\n":
                text = text[1:]
            text.rstrip()
            text = textwrap.dedent(text)
            if text:
                block.content = text

        return block

    def student_view(self, context=None):
        """
        The student view of the MarkdownXBlock.

        """
        if self.filename:
            # These can only be imported when the XBlock is running on the LMS
            # or CMS.  Do it at runtime so that the workbench is usable for
            # regular XML content.
            from xmodule.contentstore.content import StaticContent
            from xmodule.contentstore.django import contentstore
            from xmodule.exceptions import NotFoundError
            from opaque_keys import InvalidKeyError
            try:
                course_id = self.xmodule_runtime.course_id
                loc = StaticContent.compute_location(course_id, self.filename)
                asset = contentstore().find(loc)
                content = asset.data
            except (NotFoundError, InvalidKeyError):
                pass
        else:
            content = self.content

        html_content = ""
        if content:
            html_content = markdown2.markdown(content, extras=self.extras)

        # Render the HTML template
        context = {'content': html_content}
        html = loader.render_template('templates/main.html', context)
        frag = Fragment(html)

        if "fenced-code-blocks" in self.extras:
            frag.add_css_url(self.runtime.local_resource_url(self, 'public/css/pygments.css'))

        return frag

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("MarkdownXBlock",
             """<vertical_demo>
                <mdown>
                    # This is an h1

                    ## This is an h2

                    This is a regular paragraph.

                        This is a code block.

                    ```
                    #!/bin/bash

                    echo "This is a fenced code block.
                    ```

                    ```python
                    from xblock.core import XBlock

                    class MarkdownXBlock(XBlock):
                        "This is a colored fence block."
                    ```

                    > This is a blockquote.

                    * This is
                    * an unordered
                    * list

                    1. This is
                    1. an ordered
                    1. list

                    [Link to cat](http://i.imgur.com/3xVUnyA.jpg)

                    ![Cat](http://i.imgur.com/3xVUnyA.jpg)
                </mdown>
                </vertical_demo>
             """),
        ]
