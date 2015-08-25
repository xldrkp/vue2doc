# This Python file uses the following encoding: utf-8

""" Converter for VUE Concept Maps
    Converts the contents of a VUE concept map to various document formats
    by printing the notes of nodes and links.

    This script makes use of the PyQuery library
    (https://pypi.python.org/pypi/pyquery/1.2.9)

    :author: Axel Dürkop <axel.duerkop@tu-harburg.de>
    :date: 2015-05-10
"""

import os
import re
import shutil
import time
import subprocess
import zipfile
import glob
from pyquery import PyQuery as pq


class Converter():

    def __init__(self, title, folders, timestamp='1234567890'):
        self.timestamp = timestamp
        self.filename = '%s.vue' % self.timestamp
        self.folders = folders
        self.map_title = title
        self.markdown_filename = "%s.md" % self.timestamp
        self.pdf_filename = "%s.pdf" % self.timestamp
        self.html_filename = "%s.html" % self.timestamp
        self.odt_filename = "%s.odt" % self.timestamp
        self.pdfmap_filename = "ConceptMapScreenshot.pdf"
        self.caption_pdfmap = "Concept Map"
        self.pandoc_path = '/usr/bin/pandoc'
        self.ALLOWED_EXTENSIONS = set(['vue', 'vpk'])
        self.UPLOAD_FOLDER = self.folders['uploads']
        self.DOWNLOAD_FOLDER = self.folders['downloads']
        self.path_to_uploaded_file = self.folders[
            'uploads'] + '/' + self.timestamp + '/' + self.filename
        self.d = pq(filename=self.path_to_uploaded_file, parser='html')

    def clean_text(self, dirty_string):
        """ First of all cleans line breaks from notes with regex
        :return: String The cleaned text
        """
        # Remove abundant newlines
        regex = re.compile(r'(%nl;)+')
        clean = regex.sub('\n\n', dirty_string)
        regex = re.compile(r'([\$|\_])')
        clean = regex.sub(r'\\\1', clean)
        return clean

    def get_linked_nodes(self, child):
        """ Build a dictionary with IDs and arrow direction for linkes nodes
        :param child: The child node on first level
        :return: dictionary of IDs
        """
        # Get all child elements of the link
        children_of_child = self.d(child).children()

        # Links can have four types of arrow states:
        # 0: no arrows at all
        # 1: ID1 <- ID2
        # 2: ID1 -> ID2
        # 3: ID1 <-> ID2
        arrowstate = self.d(child).attr('arrowstate')
        # Store the IDs in a dictionary
        linked_nodes = {'arrowstate': arrowstate}

        # to postfix the IDs
        counter = 1
        # Iterate over the child elements...
        for n in children_of_child:
        # ... looking for nodes
            if self.d(n).attr('xsi:type') == 'node':
        # put them in the dictionary
                linked_nodes['id' + str(counter)] = self.d(n).text()
                counter += 1
        return linked_nodes

    def get_urlresources_if_any(self, n):
        """ Builds a string for the URL resources of a node
        :param n: Node object
        :return: String Formatted string with the URL
        """
        urlresource = self.d(n).children('resource')
        if urlresource \
                and urlresource.attr('xsi:type') == 'URLResource' \
                and urlresource.children('property').attr('key') == 'URL':
            text = '#### Quelle im Netz ####\n\n'
            text += '* ' + urlresource.children('property').attr('value') + '\n\n'
            return text
        else:
            return ''

    def get_image_if_any(self, n):
        """ Builds a string for the image resources of a node
        :param n: Node object
        :return: String Formatted string with the URL
        """
        image = self.d(n).children('child')
        if image and image.attr('xsi:type') == 'image':

            # Strips off the absolute path from the user's OS
            filename = os.path.join(self.UPLOAD_FOLDER, self.timestamp,
                                    os.path.basename(image.children('resource').attr('spec')))
            title = image.children('resource').children('title').text()
            title_extension_stripped = os.path.splitext(title)[0]
            # text = 'Siehe Abb. @fig:%s \n\n![%s](%s) %s\n\n' % (
            text = '\n\n![%s](%s)\n\n' % (
                title_extension_stripped,
                filename
            )
            return text
        else:
            return ''

    def build_headline_for_links(self, link, node_dictionary):
        """ Builds the headline for linked nodes
        :param link: HTML object
        :param node_dictionary: dictionary with IDs and arrow state
        :return: String
        """
        # TODO: Write some code to check, if the link is correctly connect to both nodes. There may be cases where the link appears to be one, but
        # technically is not!
        if int(node_dictionary['arrowstate']) == 0:
            return '### %s -- %s -- %s ###\n\n' % (
                self.get_label_for_linked_node(node_dictionary['id1']),
                self.get_label_for_link(link),
                self.get_label_for_linked_node(node_dictionary['id2'])
            )

        if int(node_dictionary['arrowstate']) == 1:
            return '### *%s -- %s --> %s* ###\n\n' % (
                self.get_label_for_linked_node(node_dictionary['id2']),
                self.get_label_for_link(link),
                self.get_label_for_linked_node(node_dictionary['id1'])
            )

        if int(node_dictionary['arrowstate']) == 2:
            return '### %s -- %s --> %s ###\n\n' % (
                self.get_label_for_linked_node(node_dictionary['id1']),
                self.get_label_for_link(link),
                self.get_label_for_linked_node(node_dictionary['id2'])
            )

        if int(node_dictionary['arrowstate']) == 3:
            return '### %s <-- %s --> %s ###\n\n' % (
                self.get_label_for_linked_node(node_dictionary['id1']),
                self.get_label_for_link(link),
                self.get_label_for_linked_node(node_dictionary['id2'])
            )
        else:
            return ''

    def get_label_for_linked_node(self, id):
        """ Reads the label text for a linked node
        :param id: the ID of the linked node
        :return: String
        """
        label = self.d('#' + id).attr('label')
        conv = label.encode('ascii', 'xmlcharrefreplace')
        regex = re.compile(r'\n', re.MULTILINE)
        clean = regex.sub(' ', conv)
        return clean

    def get_label_for_link(self, l):
        """ Reads the label text of a node
        :param l: Node object
        :return: String
        """
        label = self.d(l).attr('label')
        # Convert form unicode to ascii
        conv = label.encode('ascii', 'xmlcharrefreplace')
        regex = re.compile(r'\n', re.MULTILINE)
        clean = regex.sub(' ', conv)
        return clean

    def get_pdf_of_map(self):
        """ Checks if a PDF of the map exists. If there is one,
        the Markdown link will be added at the end of the document.
        :return: Boolean
        """
        if os.path.exists(self.pdfmap_filename):
            return True
        else:
            return False

    def convert2markdown(self):
        """ Markdown here is the basis for the other formats. As you will see
        the other two converter functions first call this one before doing
        their own jobs.
        """
        # Store the generated Markdown here
        file = '# %s #\n\n' % self.map_title

        # Open target file
        f = open(
            os.path.join(self.folders['downloads'], self.timestamp, self.markdown_filename), 'wb')

        # Get all children of the map
        children = self.d('child')

        # Iterate over the nodes and links
        for t in children:
            label = self.d(t).attr('label')
            child_type = self.d(t).attr('xsi:type')

            # Get all the nodes
            if child_type == 'node':
                notes = self.d(t).children('notes')

                # the node's title
                node_label = '## %s ##\n\n' % label

                # Remove newlines from node titles
                regex = re.compile(r'\n', re.MULTILINE)
                clean_node_label = regex.sub(' ', node_label)
                file += clean_node_label + '\n\n'

                image = self.get_image_if_any(t)
                if image != '':
                    file += image
                if notes:
                    file += self.d(notes).text() + '\n\n'
                    resources = self.get_urlresources_if_any(t)
                    if resources != '':
                        file += resources

            # Get all the links
            if child_type == 'link':
            # Get the dictionary with ids and arrow direction
                n_dictionary = self.get_linked_nodes(t)
            # Get notes of the link
                notes = self.d(t).children('notes')
                if label:
                    file += self.build_headline_for_links(t, n_dictionary)
                else:
                    file += ''
                if notes:
                    file += self.d(notes).text() + '\n\n'
                else:
                    file += ''

        # Add a link to the PDF of the map if there is one.
        if self.get_pdf_of_map():
            pdf_string = '\n\n![%s](%s)\n\n' % (self.caption_pdfmap, self.pdfmap_filename)
            file += pdf_string

        file = self.clean_text(file).encode('utf-8')

        f.write(file)
        f.close()
        return 0

    def convert2pdf(self):
        subprocess.call(
            ['pandoc', '-s', '-V papersize:a4paper -V geometry:margin=.5in -V lang:german -V documentclass:book', os.path.join(self.folders['downloads'], self.timestamp, self.markdown_filename),
                       '-o', os.path.join(self.folders['downloads'], self.timestamp, self.pdf_filename)])

    def convert2html(self):
        subprocess.call(
            ['pandoc', '-s', os.path.join(self.folders['downloads'], self.timestamp, self.markdown_filename),
                       '-o', os.path.join(self.folders['downloads'], self.timestamp, self.html_filename)])

    def convert2odt(self):
        subprocess.call(
            ['pandoc', '-s', os.path.join(self.folders['downloads'], self.timestamp, self.markdown_filename),
                       '-o', os.path.join(self.folders['downloads'], self.timestamp, self.odt_filename)])

    # Helper functions for file operations

    def extract_filetype(self, filename):
        """ The filetype is important to know: If the concept map uses files as ressources they have to be uploaded together with the .vue file in a zipped format. Otherwise, the falt .vue file is sufficient.
        """
        if '.' in filename:
            ext = filename.rsplit('.', 1)[1]
            if ext in self.ALLOWED_EXTENSIONS:
                return ext
            else:
                return False
        else:
            return False

    def delete_timestamp_folders(self, timestamp):
        """ After successfull conversion all data is being deleted.
        """
        shutil.rmtree(os.path.join(self.UPLOAD_FOLDER, timestamp))
        shutil.rmtree(os.path.join(self.DOWNLOAD_FOLDER, timestamp))

    def make_timestamp_directories(self):
        """ Creates directories with the current timestamp in UPLOAD and DOWNLOAD folder
        """
        try:
            os.mkdir(os.path.join(self.UPLOAD_FOLDER, self.timestamp))
            os.mkdir(os.path.join(self.DOWNLOAD_FOLDER, self.timestamp))
        except IOError:
            print('There was an error creating the directories!')
        except TypeError:
            print('Wrong type!')

    def create_timestamp(self):
        """ Returns the current timestamp as a string. The timestamp in a way is the ID for the individual user's conversion process. It has to be stored in a session when used in HTTP context.
        """
        self.timestamp = '%s' % int(time.time())
        return self.timestamp

    def unzip(self, filename):
        pass

    def save_upload(self, filename, file):
        path = os.path.join(self.UPLOAD_FOLDER, self.timestamp, filename)
        file.save(path)

    def unpack(self):
        path = self.folders[
            'uploads'] + '/' + self.timestamp + '/' + self.timestamp + '.vpk'
        with zipfile.ZipFile(path) as zf:
            zf.extractall(self.folders[
                          'uploads'] + '/' + self.timestamp + '/')
            # Find the one folder with the unpacked VUE data
            directory = os.path.join(self.folders[
                                     'uploads'], self.timestamp)
            # Find all directories
            dirs = [f for f in os.listdir(directory)
                    if os.path.isdir(os.path.join(directory, f))]

            # There should only be one, build the absolute path
            vdr_dir = os.path.join(directory, dirs[0])

            # Gather all files to be moved one level upwards
            files_to_move = os.listdir(vdr_dir)

            # Move'em!
            for f in files_to_move:
                shutil.move(os.path.join(vdr_dir, f), directory)

            # Delete the .vdr folder
            shutil.rmtree(vdr_dir)

            # Rename the .vue file inside
            search_pattern = os.path.join(directory, '*.vue')
            for v in glob.glob(search_pattern):
                os.rename(v, os.path.join(directory, '%s.vue' % self.timestamp))
