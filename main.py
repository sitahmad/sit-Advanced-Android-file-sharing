from flask import Flask, request, jsonify, send_file
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
socketio = SocketIO(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

paired_devices = []

@socketio.on('pair')
def handle_pair(data):
    device_id = data['device_id']
    if len(paired_devices) == 0:
        paired_devices.append(device_id)
        emit('status', {'message': 'Waiting for another device'}, broadcast=True)
    elif len(paired_devices) == 1 and device_id not in paired_devices:
        paired_devices.append(device_id)
        emit('status', {'message': 'Devices paired successfully!'}, broadcast=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return jsonify({'message': 'File uploaded successfully'})

@app.route('/download', methods=['GET'])
def download_file():
    # Compress all files in uploads folder into a single zip
    from zipfile import ZipFile
    zip_filename = 'sit_shared_files.zip'
    with ZipFile(zip_filename, 'w') as zipf:
        for root, _, files in os.walk(app.config['UPLOAD_FOLDER']):
            for file in files:
                zipf.write(os.path.join(root, file), file)
    return send_file(zip_filename, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Default to 5000 if no PORT variable is set
    socketio.run(host="0.0.0.0", port=port, debug=True)

    
