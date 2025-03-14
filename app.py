import os
import sys
import uuid
import time
from flask import Flask, request, send_file, render_template, session, flash, jsonify, redirect, url_for#, redirect, send_from_directory, url_for
from flask_dropzone import Dropzone
import logging

import alp as alapi

app = Flask(__name__)

app.secret_key = 'mysupersecretkey'

UPLOAD_FOLDER = 'uploads'

basedir = os.path.abspath(os.path.dirname(__file__))

app.config.update(
    UPLOADED_PATH=os.path.join(basedir, 'uploads'),
    # Flask-Dropzone config:
    DROPZONE_ALLOWED_FILE_CUSTOM= True,
    DROPZONE_ALLOWED_FILE_TYPE='.xlsx',
    DROPZONE_MAX_FILE_SIZE=5,
    DROPZONE_MAX_FILES=1,
    DROPZONE_UPLOAD_ON_CLICK=True,
)

# logger = logging.getLogger('app_logger')  # Use a named logger
# handler = logging.FileHandler('app.log')
# handler.setLevel(logging.INFO)
# handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s : %(message)s'))
# logger.addHandler(handler)
# logger.setLevel(logging.INFO) 

# logger = logging.getLogger('app_logger') 
# handler = logging.FileHandler('app.log')
# handler.setLevel(logging.INFO)
# handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s : %(message)s'))

# app.logger.addHandler(handler)


dropzone = Dropzone(app)


@app.route('/', methods=['POST', 'GET'])
def upload():
    print("'/' route in app.py", file=sys.stderr)
    logging.info("'/' route in app.py")
    # app.logging.info("'/' route in app.py")
    # flash("'/' route in app.py")

    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
async def analyze():
    print("'/analyze' route in app.py", file=sys.stderr)
    logging.info("'/analyze' route in app.py")
    # app.logging.info("'/analyze' route in app.py")
    flash("'/analyze' route in app.py")

    unique_filename = f"uploaded_file_{uuid.uuid4()}.xlsx"
    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)

    file = ''

    if request.method == 'POST':
        # print("----------------------------------", file=sys.stderr)
        print("'/analyze' route in app.py - if request.method == 'POST':", file=sys.stderr)
        logging.info("'/analyze' route in app.py - if request.method == 'POST':")
        # app.logging.info("'/analyze' route in app.py - if request.method == 'POST':")
        for key, f in request.files.items():
            if key.startswith('file'):
                print("'/analyze' route in app.py - if key.startswith('file'):", file=sys.stderr)
                logging.info("'/analyze' route in app.py - if key.startswith('file'):")
                # app.logging.info("'/analyze' route in app.py - if key.startswith('file'):")
                file = f
                try:
                    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                    file.save(filepath)
                except Exception as e:
                    return str(e), 500

    messages = []
    try:
        print("'/analyze' trying to make call to API:", file=sys.stderr)
        logging.info("'/analyze' trying to make call to API:")
        # app.logging.info("'/analyze' trying to make call to API:")
        with open(filepath, 'rb') as f:
            # response = requests.post("http://127.0.0.1:8000/orchestrate_full_analysis", files={"file": f})

            orchestrated_filename = f"DOWNLOADED_FILE_ORCHESTRATED_{uuid.uuid4()}.xlsx"
            orchestrated_filepath = os.path.join(UPLOAD_FOLDER, orchestrated_filename)
            
            try:
                response = await alapi.orchestrate_full_analysis(filepath, orchestrated_filepath)
            except Exception as e:
                # flash(str(e), 'error')
                print(f"ERROR in backend: {e}", file=sys.stderr)
                logging.info(f"ERROR in backend: {e}")
                # app.logging.info(f"ERROR in backend: {e}")
                messages.append(str(e))
                print(f"messages: {messages}")
                logging.info(f"messages: {messages}")
                # app.logging.info(f"messages: {messages}")
                return jsonify({'messages': messages, 'status': 'error'}), 500

        # if response.status_code == 200:
        if response["status_code"] == 200: #TODO: тре подумать, якась хуйня нє???

            session['uploaded_filepath'] = filepath
            session['orchestrated_filepath'] = orchestrated_filepath
            session['filename'] = file.filename
        
                
        else:
            return f"Analysis service returned {response.status_code}", 500
    except Exception as e:
        return str(e), 500

    return render_template('index.html')


@app.route('/download', methods=['GET'])
def download():
    print("/download route in app.py", file=sys.stderr)
    logging.info("/download route in app.py")
    # app.logging.info("/download route in app.py")

    uploaded_filepath = session.get('uploaded_filepath')
    orchestrated_filepath = session.get('orchestrated_filepath')
    filename = session.get('filename')
    print(f"filename in '/download': {filename}", file=sys.stderr)
    logging.info(f"filename in '/download': {filename}")
    # app.logging.info(f"filename in '/download': {filename}")
    print(f"orchestrated_filepath in '/download': {orchestrated_filepath}", file=sys.stderr)
    logging.info(f"orchestrated_filepath in '/download': {orchestrated_filepath}")
    # app.logging.info(f"orchestrated_filepath in '/download': {orchestrated_filepath}")

    file_to_send = orchestrated_filepath

    response = send_file(
        file_to_send,
        # orchestrated_filepath,
        as_attachment=True,
        download_name=f"AI_{filename}",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    print('------deleting orchestrated_filepath------', file=sys.stderr)
    logging.info('------deleting orchestrated_filepath------')
    # app.logging.info('------deleting orchestrated_filepath------')
    os.remove(orchestrated_filepath)
    logging.info('------deleting uploaded_filepath------')
    # app.logging.info('------deleting uploaded_filepath------')
    os.remove(uploaded_filepath)
    return response


@app.route('/completed')
def completed():
    return '<h1>The Redirected Page</h1><p>Upload completed.</p>'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=20000)

