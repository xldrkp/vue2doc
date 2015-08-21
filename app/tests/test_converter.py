# This Python file uses the following encoding: utf-8

import unittest
import os
import time
from converterclass import Converter


class TestConverter(unittest.TestCase):

    def setUp(self):
        # Instantiate a new object of the Converter class
        # self.timestamp = '%d' % int(time.time())
        title = "Testtitel for Concept Map"
        # The folder paths can be absolute due to the docker configuration
        # where the root folder is /app
        folders = {
            'uploads': '/app/uploads',
            'downloads': '/app/downloads'}
        self.c = Converter(title, folders)
        self.timestamp = self.c.create_timestamp()
        self.c.timestamp = self.timestamp
        filename = '%s.vue' % self.timestamp

    def test_clean_text(self):
        dirty_string = 'eingeschlossen. %nl;%nl;%nl;%nl;Quelle: Jendryschik,'
        self.assertEquals(
            self.c.clean_text(
                dirty_string),
            'eingeschlossen. \n\nQuelle: Jendryschik,'
        )

        dirty_string = '$_POST'
        self.assertEquals(self.c.clean_text(dirty_string), '\$\_POST')

    def test_get_linked_nodes(self):

        xml = """<child id="13" label="formatiert" layerid="1" created="1430914674014" x="98.85722" y="378.2456" width="140.06863" height="35.894226" strokewidth="1.0" autosized="false" controlcount="0" arrowstate="1" xsi:type="link">
            <notes>Mithilfe von CSS kann ein HTML-Dokument formatiert werden. Dabei werden HTML-Elemente mit so genannten Selektoren ausgewählt und bezüglich ihrer Eigenschaften verändert. CSS ist in der Lage, einzelne Informationen des Dokuments zu formatieren, aber auch das gesamte Layout des Dokumentes zu definieren.</notes>
            <strokecolor>#404040</strokecolor>
            <textcolor>#404040</textcolor>
            <font>Arial-plain-11</font>
            <uristring>http://vue.tufts.edu/rdf/resource/292e67087f0000013566859e22c35d5a</uristring>
            <point1 x="99.357216" y="378.7456"/>
            <point2 x="238.42584" y="413.63983"/>
            <id1 xsi:type="node">11</id1>
            <id2 xsi:type="node">12</id2>
        </child>"""

        example = {'id1': '11', 'id2': '12', 'arrowstate': '1'}
        dic = self.c.get_linked_nodes(xml)

        self.assertDictEqual(example, dic, "keine Übereinstimmung")

    def test_get_urlresources_if_any(self):

        xml = """<child id="11" label="HTML" layerid="1" created="1430914643652" x="28.357216" y="347.83817" width="71.0" height="44.0" strokewidth="1.0" autosized="true" xsi:type="node">
        <notes>Die Hypertext Markup Language (engl. für Hypertext-Auszeichnungssprache), abgekürzt HTML, ist eine textbasierte Auszeichnungssprache zur Strukturierung digitaler Dokumente wie Texte mit Hyperlinks, Bildern und anderen Inhalten.</notes>
        <resource referencecreated="0" spec="https://de.wikipedia.org/wiki/Hypertext_Markup_Language" type="2" xsi:type="URLResource">
            <property key="URL" value="https://de.wikipedia.org/wiki/Hypertext_Markup_Language"/>
        </resource>
        <fillcolor>#E8E622</fillcolor>
        <strokecolor>#776D6D</strokecolor>
        <textcolor>#000000</textcolor>
        <font>Arial-plain-12</font>
        <uristring>http://vue.tufts.edu/rdf/resource/292e67067f0000013566859e7836a2c2</uristring>
        <shape arcwidth="20.0" archeight="20.0" xsi:type="roundRect"/>
        </child>"""

        example = """#### Quelle im Netz ####

* https://de.wikipedia.org/wiki/Hypertext_Markup_Language

"""

        self.assertEqual(self.c.get_urlresources_if_any(xml), example)

    @unittest.skip('because pandoc-fignos does not work yet.')
    def test_get_image_if_any(self):

        xml = """<child id="14" label="JavaScript" layerid="1" created="1430914680384" x="382.70227" y="316.91513" width="167.0" height="156.0" strokewidth="1.0" autosized="true" xsi:type="node">
        <notes>JavaScript (kurz JS) ist eine Skriptsprache, die ursprünglich für dynamisches HTML in Webbrowsern entwickelt wurde, um Benutzerinteraktionen auszuwerten, Inhalte zu verändern, nachzuladen oder zu generieren und so die Möglichkeiten von HTML und CSS zu erweitern. Heute findet JavaScript auch außerhalb von Browsern Anwendung, so etwa auf Servern und in Microcontrollern.</notes>
        <resource referencecreated="0" size="10268" spec="/home/duerkop/Downloads/JavaScript-logo.png" type="1" xsi:type="URLResource">
            <title>JavaScript-logo.png</title>
            <property key="Content.size" value="10268"/>
            <property key="Content.modified" value="Tue May 19 22:24:26 CEST 2015"/>
            <property key="image.width" value="1052"/>
            <property key="image.height" value="1052"/>
            <property key="image.format" value="png"/>
            <property key="File" value="/home/duerkop/Downloads/JavaScript-logo.png"/>
        </resource>
        <fillcolor>#8AEE95</fillcolor>
        <strokecolor>#776D6D</strokecolor>
        <textcolor>#000000</textcolor>
        <font>Arial-plain-12</font>
        <uristring>http://vue.tufts.edu/rdf/resource/292e67097f0000013566859ed849d6c7</uristring>
        <child id="57" created="1432067082808" x="34.0" y="22.0" width="128.0" height="128.0" strokewidth="0.0" autosized="false" xsi:type="image">
            <resource referencecreated="0" size="10268" spec="/home/duerkop/Downloads/JavaScript-logo.png" type="1" xsi:type="URLResource">
                <title>JavaScript-logo.png</title>
                <property key="Content.size" value="10268"/>
                <property key="Content.modified" value="Tue May 19 22:24:26 CEST 2015"/>
                <property key="image.width" value="1052"/>
                <property key="image.height" value="1052"/>
                <property key="image.format" value="png"/>
                <property key="File" value="/home/duerkop/Downloads/JavaScript-logo.png"/>
            </resource>
            <strokecolor>#404040</strokecolor>
            <textcolor>#000000</textcolor>
            <font>SansSerif-plain-14</font>
            <uristring>http://vue.tufts.edu/rdf/resource/6dd9a36e7f00000174c4acc5cdce5ff8</uristring>
        </child>
        <shape arcwidth="20.0" archeight="20.0" xsi:type="roundRect"/>
    </child>"""

        example = """Siehe Abb. @fig:JavaScript-logo \n\n![JavaScript-logo](/home/duerkop/Downloads/JavaScript-logo.png) {#fig:JavaScript-logo}

"""

        self.assertEquals(self.c.get_image_if_any(xml), example)

    def test_build_headline_for_links(self):

        xml = """<child id="13" label="formatiert" layerid="1" created="1430914674014" x="98.85722" y="378.2456" width="140.06863" height="35.894226" strokewidth="1.0" autosized="false" controlcount="0" arrowstate="1" xsi:type="link">
        <notes>Mithilfe von CSS kann ein HTML-Dokument formatiert werden. Dabei werden HTML-Elemente mit so genannten Selektoren ausgewählt und bezüglich ihrer Eigenschaften verändert. CSS ist in der Lage, einzelne Informationen des Dokuments zu formatieren, aber auch das gesamte Layout des Dokumentes zu definieren.</notes>
        <strokecolor>#404040</strokecolor>
        <textcolor>#404040</textcolor>
        <font>Arial-plain-11</font>
        <uristring>http://vue.tufts.edu/rdf/resource/292e67087f0000013566859e22c35d5a</uristring>
        <point1 x="99.357216" y="378.7456"/>
        <point2 x="238.42584" y="413.63983"/>
        <id1 xsi:type="node">11</id1>
        <id2 xsi:type="node">12</id2>
    </child>"""

        dic = {'arrowstate': '1', 'id2': '12', 'id1': '11'}

        headline = """### *CSS -- formatiert --> HTML* ###\n\n"""

        self.assertEquals(self.c.build_headline_for_links(xml, dic), headline)

    def test_convert2pdf(self):
        pass

    def test_convert2html(self):
        pass

    def test_convert2markdown(self):
        pass

    def test_if_directories_exist(self):
        self.assertTrue(os.path.exists(self.c.UPLOAD_FOLDER))
        self.assertTrue(os.path.exists(self.c.DOWNLOAD_FOLDER))

    def test_extract_filetype(self):
        assert self.c.extract_filetype("file.zip") in self.c.ALLOWED_EXTENSIONS
        assert self.c.extract_filetype("file.vue") in self.c.ALLOWED_EXTENSIONS
        self.assertIs(self.c.extract_filetype("file"), False)

    def test_create_timestamp(self):
        self.assertIs(type(self.c.create_timestamp()), str)

    def test_01_make_timestamp_directories(self):
        self.c.make_timestamp_directories()
        self.assertTrue(os.path.exists(self.c.UPLOAD_FOLDER))
        self.assertTrue(os.path.exists(self.c.DOWNLOAD_FOLDER))

    @unittest.skip('because deleting the timestamped folders does not work from tests.')
    def test_03_delete_timestamp_folders(self):
        self.c.delete_timestamp_folders(self.timestamp)
        self.assertFalse(os.path.exists(self.c.UPLOAD_FOLDER))
        self.assertFalse(os.path.exists(self.c.DOWNLOAD_FOLDER))

    def test_unzip(self):
        upload_folder = self.c.UPLOAD_FOLDER

    def test_label_for_link(self):
        expected = "W&#246;rld Wide Web"
        self.assertEquals(self.c.get_label_for_linked_node('30'), expected)
        expected = "Die Webseite wird nach Benutzeranforderungen je- weils neu generiert"
        self.assertEquals(self.c.get_label_for_linked_node('59'), expected)
