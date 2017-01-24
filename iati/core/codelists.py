from lxml import etree

import iati.core.resources

class Codelist(object):
    """Representation of a Codelist as defined within the IATI SSOT"""

    def __init__(self, name=None, path=None, xml=None):
        def parse_from_xml(xml):
            """Parse a Codelist from the XML that defines it

            TODO: Define relevant tests and add error handling
            """
            tree = etree.fromstring(xml)

            self.name = tree.attrib['name']
            for codeEl in tree.findall('codelist-items/codelist-item'):
                value = codeEl.find('code').text
                name = codeEl.find('description/narrative').text
                self.add_code(iati.core.codelists.Code(value, name))

        self.codes = []
        self.name = name
        self.path = path

        if xml:
            parse_from_xml(xml)

    def add_code(self, code):
        """Add a Code to the Codelist"""
        if isinstance(code, Code):
            self.codes.append(code)


class Code(object):
    """Representation of a Code contained within a Codelist"""

    def __init__(self, value=None, name=None):
        self.name = name
        self.value = value
