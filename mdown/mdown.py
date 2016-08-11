import logging
import markdown2
import textwrap

from xblock.core import XBlock
from xblock.fields import Scope, String
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
        default="",
        scope=Scope.settings)
    content = String(
        help="Markdown content to display for this module.",
        default=u"",
        scope=Scope.content)
    filename = String(
        help="Relative path to a markdown file in the static store.",
        default="",
        scope=Scope.content)

    editable_fields = (
        'display_name',
        'content',
        'filename')

    has_author_view = True

    @classmethod
    def parse_xml(cls, node, runtime, keys, id_generator):
        """
        Parses the source XML in a way that preserves indenting, needed for markdown.

        """
        block = runtime.construct_xblock_from_class(cls, keys)

        # The base implementation: child nodes become child blocks.
        # Or fields, if they belong to the right namespace.
        for child in node:
            if child.tag is etree.Comment:
                continue
            qname = etree.QName(child)
            tag = qname.localname
            namespace = qname.namespace

            if namespace == XML_NAMESPACES["option"]:
                cls._set_field_if_present(block, tag, child.text, child.attrib)
            else:
                block.runtime.add_node_as_child(block, child, id_generator)

        # Attributes become fields.
        for name, value in node.items():
            cls._set_field_if_present(block, name, value, {})

        # Text content becomes "content", if such a field exists.
        if "content" in block.fields and block.fields["content"].scope == Scope.content:
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
            # These can only be imported when the XBlock is running on the LMS.
            # Do it at runtime so that the workbench is usable for regular XML
            # content.
            from xmodule.contentstore.content import StaticContent
            from xmodule.contentstore.django import contentstore
            from xmodule.exceptions import NotFoundError
            from opaque_keys import InvalidKeyError
            try:
                loc = StaticContent.compute_location(course_id, self.filename)
                asset = contentstore().find(loc)
                content = asset.data
            except (NotFoundError, InvalidKeyError):
                pass
        else:
            content = self.content

        if content:
            html = markdown2.markdown(content)

        # Render the HTML template
        context = {'content': html}
        html = loader.render_template('templates/main.html', context)
        frag = Fragment(html)

        return frag

    def author_view(self, context=None):
        """
        Studio preview.

        """
        if self.filename:
            return Fragment(u"<em>If filename is set, no preview is available.</em>")
        else:
            return self.student_view(context)

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
