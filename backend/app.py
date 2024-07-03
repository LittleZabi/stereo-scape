import json
from math import e
from time import process_time
from turtle import isvisible
from bson import ObjectId
from flask import Flask, request, send_from_directory
import os
from flask_cors import CORS
from utils.load_model import LoadNeRF
from utils.fun__ import deleteFilesAndFolder, randomString, resizeAndSave,saveAndExtractPoses
from utils.setup_dataset import setupDataset
from flask_socketio import SocketIO
from db_ops.ops import saveUsersData, updateVideoPath
from utils.use_colmap import COLMAP
from utils.nerf import NeRF

os.environ['colmap'] = f'{os.getcwd()}\\colmap\\'

app = Flask(__name__)
CORS(app)
socket = SocketIO(app, cors_allowed_origins='*')
size = (100, 100)

@app.route('/results/<path:filename>')
def sendResultImage(filename):
    return send_from_directory('results', filename)

@app.route('/videos/<path:filename>')
def sendFiles(filename):
    return send_from_directory('videos', filename)

@app.route('/media/<path:filename>')
def sendMedia(filename):
    return send_from_directory('media', filename)


global processStoped
processStoped = False
@socket.on('stop_process')
def handleStop(a):
    global processStoped
    processStoped = True

def checkProcessExecution(message=''):
    global processStoped
    if processStoped:
        socket.emit('process_stop', {'message': message} if message != '' else {})
    return processStoped

@app.route('/get-visualz', methods=['GET'])
def getVisualz():
    theta = request.args.get('theta')
    phi = request.args.get('phi')
    rad = request.args.get('radius')
    prevImg = request.args.get('prevImg')
    if not theta:
        theta = 0
    if not phi:
        phi = 0
    if not rad:
        rad = 0
    media = request.args.get('media')
    model = LoadNeRF(media)
    img = model.getView(int(theta), float(phi), float(rad), str(prevImg))
    return img 

@app.route('/generate-video', methods=["POST"])
def generateVideo():
    form = request.form
    media = form.get('media')
    user = form.get('user')
    _id = form.get('_id')
    model = LoadNeRF(media)
    outupt = model.Video360()
    updateVideoPath(_id, outupt)
    # except Exception as e:
    #     return {'message': f"Error: {e}", 'success': 0}
    return {'message': 'Successfully generated!', 'success': 1, 'video': outupt}

@app.route('/load-project/<string:media>/get-view', methods=['GET'])
def LoadModel(media):
    # path = f"{os.getcwd()}{os.sep}media{os.sep}{media}{os.sep}"
    model = LoadNeRF(media)
    img_path = model.getView()
    outupt = model.Video360()
    return {'message': 'success', 'image_path': img_path, 'success': 1, 'video': outupt} 

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
    isVideo = False
    isNPZ =False 
    for f in request.files:
        i = i + 1
        file = request.files[f]
        ex = file.filename.split('.')[-1]
        fp = p + '/'
        if ex == 'mp4': 
            isVideo = True
            fp = fp + 'vid-'
        
        if ex == 'npz':
            isNPZ = True
            fp = fp + 'dataset.npz'
            file.save(fp)
            files.append(fp)
        else:
            fp = fp + str(i) + '.' + ex
            files.append([file, fp])

    if (isVideo == False and isNPZ == False) and len(files) < 4:
        processStoped = True 
        checkProcessExecution("Process is stopped due to lack of images. select more than 4 images.")
        return {'message': 'Failed please select more 4 images.', 'success': 0}

    if settings and settings.get('image_width') and settings.get('image_height'):
        size = (settings.get('image_width'), settings.get('image_height'))
    
    npzDatasetPath = ''

    if isNPZ == False:
        if isVideo:
            _, fsize, numberOfImages = saveAndExtractPoses(files[0], outputFolder = p, size = size, emit = socket.emit)
        else:
            numberOfImages = 0
            fsize = 0
            for file in files:
                _, fz = resizeAndSave(file[0], file[1], size)
                if type(fsize) == int:
                    fsize += fz
                numberOfImages= 1 + numberOfImages 
                percent = numberOfImages / len(files) * 100
                socket.emit('progress', {'title': f'Resizing Image ({file[0].filename}): ', 'progress': percent, 'process': 'res_image'})
        # colmap = COLMAP(p, socket.emit, checkProcessExecution=checkProcessExecution)
        # if colmap.error:
        #     socket.emit('progress', {'process': 'colmap', 'title': 'Extracting features failed ❌', 'progress': 4 / 5 * 100})
        # ds = setupDataset(p, not colmap.error, socket.emit)

        ds = setupDataset(p, False, socket.emit)
        if ds.isDatasetCreated():
            npzDatasetPath = ds.output_npz 

    else:
        npzDatasetPath = files[0]

    if npzDatasetPath != '':
        nerf = NeRF(socket.emit, checkProcessExecution=checkProcessExecution, config=settings, media_path=p, save_modal=True)
        nerf.loadDataset(npzDatasetPath)
        nerf.Run()
        
    else:
       socket.emit('progress', {'message': "Creating dataset is failed please try again later.",'process': 'generating_npz', 'title': 'Dataset creation failed ❌', 'progress': 4 / 5 * 100})
    if processStoped:
        deleteFilesAndFolder(p,  deleteFolder=True, deleteFiles=True)
        return {'message': "Processing Stopped!", 'success': 0}
    else:
        col_d = {'user': ObjectId(user_id), 'images_len': numberOfImages, 'psnrs':nerf.psnrs, 'media': fn, 'size': {'images': fsize}}
        saveUsersData(col_d)
        socket.emit('process_complete', {'media': fn})
        return {'message': 'Complete!', 'success': 1}


if __name__ == "__main__":
    socket.run(app, debug=True)
