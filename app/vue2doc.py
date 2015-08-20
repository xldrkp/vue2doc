import os
import time
import shutil
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import session
from flask import send_from_directory
from werkzeug import secure_filename
from converterclass import Converter

DEBUG = True
SECRET_KEY = 'development key'

app = Flask(__name__)
FOLDERS = {
    'uploads': os.path.join(app.root_path, 'uploads'),
    'downloads': os.path.join(app.root_path, 'downloads')}
# Build configuration keys by reading all upper case variables
app.config.from_object(__name__)


@app.route('/')
@app.route('/home')
def index():
    to_be_deleted = request.args.get('del')
    if to_be_deleted != None:
        clean_up(to_be_deleted)
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        title = request.form['title']
        session['title'] = title
        file = request.files['file']

        conv = Converter(title, FOLDERS)
        timestamp = conv.create_timestamp()

        app.logger.info(timestamp)

        session['timestamp'] = timestamp

        app.logger.info(file)
        try:
            extension = conv.extract_filetype(file.filename)
            if not extension:
                raise
            try:
                # Construct the filename from the timestamp and the extension
                filename = '%s.%s' % (timestamp, extension)
                conv.make_timestamp_directories()
                try:
                    conv.save_upload(filename, file)
                    flash('Alright!', category='success')
                    return render_template('done.html', timestamp=timestamp)
                except:
                    flash('Oops, there was an error! Could not save the file!', category='danger')
                    return redirect(url_for('index'))
            except:
                flash(
                    'Oops, there was an error! Could not create the upload directory!', category='danger')
                return redirect(url_for('index'))
        except:
            flash('Oops, there was an error! Perhaps not a VUE file?', category='danger')
            return redirect(url_for('index'))
    return render_template('about.html')


@app.route('/download/<type>/<int:timestamp>', methods=['GET'])
def download_files(type, timestamp):
    allowed_download_types = ['pdf', 'html', 'markdown', 'odt']
    timestamp = '%s' % timestamp
    if type not in allowed_download_types:
        return "No valid download type!"
    else:
        conv = Converter(session['title'], FOLDERS, timestamp)
        download_folder = os.path.join(FOLDERS['downloads'], timestamp)
        if type == 'pdf':
            conv.convert2markdown()
            conv.convert2pdf()
            filename = '%s.pdf' % timestamp
            return send_from_directory(download_folder,
                                       filename, as_attachment=True)
        elif type == 'html':
            conv.convert2markdown()
            conv.convert2html()
            filename = '%s.html' % timestamp
            return send_from_directory(download_folder,
                                       filename, as_attachment=True)
        elif type == 'odt':
            conv.convert2markdown()
            conv.convert2odt()
            filename = '%s.odt' % timestamp
            return send_from_directory(download_folder,
                                       filename, as_attachment=True)
        elif type == "markdown":
            conv.convert2markdown()
            filename = '%s.md' % timestamp
            return send_from_directory(download_folder,
                                       filename, as_attachment=True)


def do_conversion(file):
    filename = secure_filename(file.filename)
    timestamp = int(time.time())
    filename_ts = '%s.vue' % timestamp
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename_ts))

    conv = Converter(filename_ts, session['title'], {
                     'uploads': app.config['UPLOAD_FOLDER'], 'downloads': app.config['DOWNLOAD_FOLDER']})
    conv.convert2markdown()
    return timestamp


def allowed_file(filename):
    if '.' in filename:
        ext = filename.rsplit('.', 1)[1]
        if ext in ALLOWED_EXTENSIONS:
            return ext
        else:
            return false
    else:
        return false


def clean_up(tbd):
    path_up = os.path.join(FOLDERS['uploads'], session['timestamp'])
    path_down = os.path.join(FOLDERS['downloads'], session['timestamp'])
    if os.path.exists(path_up):
        shutil.rmtree(path_up)
    if os.path.exists(path_down):
        shutil.rmtree(path_down)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
