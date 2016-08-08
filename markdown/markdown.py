import logging
import markdown2

from fs.osfs import OSFS
from fs.errors import ResourceNotFoundError
from path import Path as path

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
    Displays markdown content as HTML

    """
    display_name = String(
        help="This name appears in the horizontal navigation at the top of the page.",
        display_name="Display Name",
        scope=Scope.settings,
        default=""
    )
    content = String(
        help="Markdown content to display for this module",
        default=u"",
        scope=Scope.content)

    @classmethod
    def parse_xml(cls, node, runtime, keys, id_generator):
        """
        Parse the XML for a markdown block.

        """
        block = runtime.construct_xblock_from_class(cls, keys)

        # Load the data
        filename = node.get('filename')
        if filename is None:
            content = node.text
        else:
            url_name = node.get('url_name')
            location = id_generator.create_definition(node.tag, url_name)
            pointer_path = "markdown/{url_path}".format(
                url_path=location.name.replace(':', '/')
            )
            base = path(pointer_path).dirname()
            filepath = "{base}/{filename}.md".format(
                    base=base,
                    filename=filename)

            # TODO: resource_fs comes from
            # edx-platform/common/lib/xmodule/xmodule/modulestore/xml.py.  Need
            # to figure out how to get these directories from an XBlock, as
            # opposed to an XModule.  Might be best to import resource_fs
            # directly from the runtime.
            resource_fs = OSFS(xmlstore.data_dir / course_dir)
            try:
                with resource_fs.open(filepath) as infile:
                    text = infile.read().decode('utf-8')
            except (ResourceNotFoundError) as err:
                msg = 'Unable to load file contents at path {0}: {1} '.format(
                    filepath, err)
                raise Exception(msg), None, sys.exc_info()[2]

        if content:
            content = content.strip()
            if content:
                block.content = content

        return block

    def definition_to_xml(self, resource_fs):
        """
        Write <markdown filename="" [meta-attrs="..."]> to filename.xml,
        and the markdown string to filename.md.

        """
        # Write markdown to file, return an empty tag
        pathname = self.url_name.replace(':', '/')
        filepath = u'markdown/{pathname}.md'.format(
            pathname=pathname
        )

        resource_fs.makedir(os.path.dirname(filepath), recursive=True, allow_recreate=True)
        with resource_fs.open(filepath, 'w') as filestream:
            markdown_data = self.data.encode('utf-8')
            filestream.write(markdown_data)

        # write out the relative name
        relname = path(pathname).basename()

        elt = etree.Element('markdown')
        elt.set("filename", relname)
        return elt

    def add_xml_to_node(self, node):
        """
        Set attributes and children on `node` to represent ourselves as XML.

        We parse our HTML content, and graft those nodes onto `node`.

        """
        xml = "<html_demo>" + self.content + "</html_demo>"
        html_node = etree.fromstring(xml)

        node.tag = html_node.tag
        node.text = html_node.text
        for child in html_node:
            node.append(child)

    def fallback_view(self, context=None):
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
