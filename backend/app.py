from flask import Flask, request, send_from_directory
import os
from flask_cors import CORS
from utils.fun__ import randomString, resizeAndSave
from utils.create_npz import createNPZ
from flask_socketio import SocketIO
from db_ops.ops import saveUsersData


app = Flask(__name__)
CORS(app)
socket = SocketIO(app, cors_allowed_origins='*')

@app.route('/videos/<path:filename>')
def sendFiles(filename):
    return send_from_directory('videos', filename)

@app.route('/files', methods=['POST'])
def Files():
    user_id = request.form['user']
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
    fsize = 0
    for file in files:
        _, fz = resizeAndSave(file[0], file[1])
        if type(fsize) == int:
            fsize += fz
        file_= 1 + file_ 
        percent = file_ / len(files) * 100
        socket.emit('progress', {'percent': percent, 'process': 'Resizing Images'})
    npz = createNPZ(p) 
    dataset_output = f"{p}/{fn}.npz"
    success, dataset_size = npz.generate_and_save(socket.emit, dataset_output)
    print('files size: ', fsize, 'dataset: ', dataset_size)
    if success: 
        print('successfully created')
    col_d = {'user': user_id, 'images': p, 'dataset': dataset_output, 'model': '', 'size': {'images': fsize, 'dataset': dataset_size, 'model': 0}}
    saved_data = saveUsersData(col_d)
    return {'session': fn, 'saved_data_id': saved_data.inserted_id}


if __name__ == "__main__":
    socket.run(app, debug=True)
