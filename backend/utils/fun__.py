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

def resizeAndSave(file, path):
    fs = file.stream
    fb = bytearray(fs.read())
    image = cv2.imdecode(np.array(fb), cv2.IMREAD_COLOR)
    rsi = cv2.resize(image, (100, 100))
    cv2.imwrite(path, rsi)
    return path, os.path.getsize(path)