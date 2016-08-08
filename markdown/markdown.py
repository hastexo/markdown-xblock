import logging
import markdown2

from xblock.core import XBlock
from xblock.fields import Scope, String
from xblock.fragment import Fragment
from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable import StudioEditableXBlockMixin
from xmodule.contentstore.content import StaticContent
from xmodule.contentstore.django import contentstore
from xmodule.exceptions import NotFoundError
from opaque_keys import InvalidKeyError

log = logging.getLogger(__name__)
loader = ResourceLoader(__name__)


class MarkdownXBlock(StudioEditableXBlockMixin, XBlock):
    """
    Converts markdown files into HTML
    """

    path = String(
        default="",
        scope=Scope.content,
        help="The relative path to the markdown file.  For example, \"markdown_content.md\".")
    editable_fields = (
        'path')
    has_author_view = True

    def author_view(self, context=None):
        """ Studio View """
        return Fragment(u'<em>This XBlock only renders content when viewed via the LMS.</em></p>')

    def student_view(self, context=None):
        """
        The primary view of the MarkdownXBlock, shown to students when viewing
        courses.
        """
        # Load the markdown file and convert it
        content = None
        try:
            loc = StaticContent.compute_location(course_id, self.path)
            asset = contentstore().find(loc)
            content = markdown2.markdown(asset.data)
        except (NotFoundError, InvalidKeyError):
            pass

        # Render the HTML template
        html_context = {'content': content}
        html = loader.render_template('templates/main.html', html_context)
        frag = Fragment(html)

        return frag

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("MarkdownXBlock",
             """<vertical_demo>
                <markdown/>
                </vertical_demo>
             """),
        ]
