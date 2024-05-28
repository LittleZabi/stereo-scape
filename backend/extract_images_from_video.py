import cv2



cap = cv2.VideoCapture('./data/test.mp4')
frame_no = 0
image_path = './colmap/images/'
i = 0
while (cap.isOpened):
    ret, frame = cap.read()
    if frame_no % 10 == 0:
        i += 1 
        target = str(image_path + f'/{i}.jpg')
        x = cv2.resize(frame, (100, 100))
        cv2.imwrite(target, x)
    frame_no += 1

    if frame_no > 60 * 30:
        break

cap.release()
print('done')