import json
from time import process_time
from flask import Flask, request, send_from_directory
import os
from flask_cors import CORS
from utils.fun__ import deleteFilesAndFolder, randomString, resizeAndSave
from utils.setup_dataset import setupDataset
from flask_socketio import SocketIO
from db_ops.ops import saveUsersData
from utils.use_colmap import COLMAP
from utils.nerf import NeRF

os.environ['colmap'] = f'{os.getcwd()}\\colmap\\'

app = Flask(__name__)
CORS(app)
socket = SocketIO(app, cors_allowed_origins='*')

@app.route('/results/<path:filename>')
def sendResultImage(filename):
    return send_from_directory('results', filename)

@app.route('/videos/<path:filename>')
def sendFiles(filename):
    return send_from_directory('videos', filename)

global processStoped
processStoped = False
@socket.on('stop_process')
def handleStop(a):
    global processStoped
    processStoped = True

def checkProcessExecution():
    global processStoped
    if processStoped:
        socket.emit('process_stop', {})
    return processStoped

@app.route('/files', methods=['POST'])
def Files():
    global processStoped 
    processStoped = False
    user_id = request.form.get('user')
    settings = request.form.get('config')
    if settings:
        settings = json.loads(settings)
    if not len(request.files):
        return {'success': 0, 'error': "emptyRequest", 'message': "Please add some images of the object from different view points"}
    fn = randomString(10)
    p = os.getcwd()+'/media/' + fn 
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
    size = (100, 100)
    if settings and settings.get('image_width') and settings.get('image_height'):
        size = (settings.get('image_width'), settings.get('image_height'))
    for file in files:
        _, fz = resizeAndSave(file[0], file[1], size)
        if type(fsize) == int:
            fsize += fz
        file_= 1 + file_
        percent = file_ / len(files) * 100
        socket.emit('progress', {'title': f'Resizing Image ({file[0].filename}): ', 'progress': percent, 'process': 'res_image'})
    
    colmap = COLMAP(p, socket.emit, checkProcessExecution=checkProcessExecution)
    if colmap.error:
        socket.emit('progress', {'process': 'colmap', 'title': 'Extracting features failed ❌', 'progress': 4 / 5 * 100})
    ds = setupDataset(p, not colmap.error, socket.emit)
    if ds.isDatasetCreated():
        nerf = NeRF(socket.emit, checkProcessExecution=checkProcessExecution, config=settings)
        nerf.loadDataset(ds.output_npz)
        nerf.Run()
        
    else:
       socket.emit('progress', {'message': "Creating dataset is failed please try again later.",'process': 'generating_npz', 'title': 'Dataset creation failed ❌', 'progress': 4 / 5 * 100})
    if processStoped:
        deleteFilesAndFolder(p,  deleteFolder=True, deleteFiles=True)
        return {'message': "Processing Stopped!", 'success': 0}
    else:
        col_d = {'user': user_id, 'images': p, 'psnrs':nerf.psnrs, 'dataset': ds.output_npz,'video': nerf.output_video, 'size': {'images': fsize, 'dataset': ds.output_size, 'vidoe': nerf.video_size}}
        saveUsersData(col_d)
        socket.emit('process_complete', {'video': nerf.output_video})
        return {'message': 'Complete!', 'success': 1}


if __name__ == "__main__":
    socket.run(app, debug=True)
