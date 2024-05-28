import string
import random
import cv2
import numpy as np
import os

def randomString(limit):
    s = string.ascii_lowercase + string.ascii_uppercase
    f = ''
    for i in range(limit):
        index = random.randint(0, len(s) - 1)
        f = f + s[index]
    return f

def resizeAndSave(file, path, size=(100, 100)):
    fs = file.stream
    fb = bytearray(fs.read())
    image = cv2.imdecode(np.array(fb), cv2.IMREAD_COLOR)
    rsi = cv2.resize(image, size)
    cv2.imwrite(path, rsi)
    return path, os.path.getsize(path)

def deleteFilesAndFolder(dir, deleteFolder = False, deleteFiles=True):
    if os.path.exists(dir) and os.path.isdir(dir):
        try:
            for root, dirs, files in os.walk(dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        print(f"Deleted file: {file_path}")
                    except OSError as e:
                        print(f"Error deleting file {file_path}: {e.strerror}")
        except OSError as e:
            print(f"Error accessing directory {dir}: {e.strerror}")
    
    if deleteFolder:
        if os.path.exists(dir):
            try:
                os.remove(dir)
            except OSError as e:
                print(f"Error: {dir} : {e.strerror}")
        else:
            print(f"File not found: {dir}")