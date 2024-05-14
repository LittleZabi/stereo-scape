from flask import Flask, request
import os
from flask_cors import CORS
from utils.fun__ import randomString, resizeAndSave
from utils.create_npz import createNPZ
from flask_socketio import SocketIO, emit

app = Flask(__name__)
CORS(app)
socket = SocketIO(app, cors_allowed_origins='*')

@app.route('/files', methods=['POST'])
def Files():
    if not len(request.files):
        return {'success': 0, 'error': "emptyRequest", 'message': "Please add some images of the object from different view points"}
    fn = randomString(10)
    p = './media/' + fn 
    os.mkdir(p) 
    files = []
    i = 0
    for f in request.files:
        i = i + 1
        file = request.files[f]
        ex = file.filename.split('.')[-1]
        files.append([file, p + '/' + str(i) + '.' + ex])

    file_= 0
    for file in files:
        resizeAndSave(file[0], file[1])
        file_= 1 + file_ 
        percent = file_ / len(files) * 100
        socket.emit('progress', {'percent': percent, 'process': 'Resizing Images'})

    npz = createNPZ(p) 
    success = npz.generate_and_save(socket.emit, f"{p}/{fn}.npz")
    if success: 
        print('successfully created')
    return {'session': fn}


if __name__ == "__main__":
    socket.run(app, debug=True)
