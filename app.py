import os
import sys
import uuid
import time
from flask import Flask, request, send_file, render_template, session, flash, jsonify, redirect, url_for#, redirect, send_from_directory, url_for
from flask_dropzone import Dropzone

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

dropzone = Dropzone(app)


@app.route('/', methods=['POST', 'GET'])
def upload():
    print("'/' route in app.py", file=sys.stderr)
    # flash("'/' route in app.py")

    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
async def analyze():
    print("'/analyze' route in app.py", file=sys.stderr)
    flash("'/analyze' route in app.py")

    unique_filename = f"uploaded_file_{uuid.uuid4()}.xlsx"
    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)

    file = ''

    if request.method == 'POST':
        # print("----------------------------------", file=sys.stderr)
        print("'/analyze' route in app.py - if request.method == 'POST':", file=sys.stderr)
        for key, f in request.files.items():
            if key.startswith('file'):
                print("'/analyze' route in app.py - if key.startswith('file'):", file=sys.stderr)
                file = f
                try:
                    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                    file.save(filepath)
                except Exception as e:
                    return str(e), 500

    messages = []
    try:
        print("'/analyze' trying to make call to API:", file=sys.stderr)
        with open(filepath, 'rb') as f:
            # response = requests.post("http://127.0.0.1:8000/orchestrate_full_analysis", files={"file": f})

            orchestrated_filename = f"DOWNLOADED_FILE_ORCHESTRATED_{uuid.uuid4()}.xlsx"
            orchestrated_filepath = os.path.join(UPLOAD_FOLDER, orchestrated_filename)
            
            try:
                response = await alapi.orchestrate_full_analysis(filepath, orchestrated_filepath)
            except Exception as e:
                # flash(str(e), 'error')
                print(f"ERROR in backend: {e}", file=sys.stderr)
                messages.append(str(e))
                print(f"messages: {messages}")
                return jsonify({'messages': messages, 'status': 'error'}), 500
                # return redirect("/")
                # return redirect("/analyze")
                # time.sleep(3)
                # return redirect(url_for('index'))
                # return render_template('index.html')

                # return render_template('index.html') #TODO: need to show user the ERROR, and reload page

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

    uploaded_filepath = session.get('uploaded_filepath')
    orchestrated_filepath = session.get('orchestrated_filepath')
    filename = session.get('filename')
    print(f"filename in '/download': {filename}", file=sys.stderr)
    print(f"orchestrated_filepath in '/download': {orchestrated_filepath}", file=sys.stderr)

    file_to_send = orchestrated_filepath

    response = send_file(
        file_to_send,
        # orchestrated_filepath,
        as_attachment=True,
        download_name=f"AI_{filename}",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    print('------deleting orchestrated_filepath------', file=sys.stderr)
    os.remove(orchestrated_filepath)
    print('------deleting uploaded_filepath------', file=sys.stderr)
    os.remove(uploaded_filepath)
    return response


@app.route('/completed')
def completed():
    return '<h1>The Redirected Page</h1><p>Upload completed.</p>'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=20000)

