from networks import FaceBox
from encoderl import DataEncoder

import torch
import numpy as np
from torch.autograd import Variable
import torch.nn.functional as F
import cv2
import time


def detect(im):
    h, w, _ = im.shape
    dim_diff = np.abs(h - w)
    pad1, pad2 = dim_diff // 2, dim_diff - dim_diff // 2
    pad = ((pad1, pad2), (0, 0), (0, 0)) if h <= w else ((0, 0), (pad1, pad2), (0, 0))
    input_img = np.pad(im, pad, 'constant', constant_values=128)
    input_img = cv2.resize(input_img,(1024,1024))/255.

    im_tensor = torch.from_numpy(input_img.transpose((2,0,1))).float()

    loc, conf = net(im_tensor.unsqueeze(0))

    boxes, labels, probs = data_encoder.decode(loc.data.squeeze(0),
                                                F.softmax(conf.squeeze(0), dim=1))
    if probs[0] != 0:
        boxes = boxes.numpy()
        probs = probs.detach().numpy()
        if h <= w:
            boxes[:,1] = boxes[:,1]*w-pad1
            boxes[:,3] = boxes[:,3]*w-pad1
            boxes[:,0] = boxes[:,0]*w
            boxes[:,2] = boxes[:,2]*w
        else:
            boxes[:,1] = boxes[:,1]*h
            boxes[:,3] = boxes[:,3]*h
            boxes[:,0] = boxes[:,0]*h-pad1
            boxes[:,2] = boxes[:,2]*h-pad1

    return boxes, probs

def testIm(im):
    
    if im is None:        
        return
    h,w,_ = im.shape
    boxes, probs = detect(im)

    if probs[0] == 0:
        print('There is no face in the image')
        exit()
    for i, (box) in enumerate(boxes):
        print('i=', i, 'box=', box)
        x1 = int(box[0])
        x2 = int(box[2])
        y1 = int(box[1])
        y2 = int(box[3])
        cv2.rectangle(im,(x1,y1+4),(x2,y2),(0,255,0),2)
        cv2.putText(im, str(probs[i]), (x1,y1), cv2.FONT_HERSHEY_COMPLEX, 0.4, (0,255,0))
    cv2.imshow('photo', im)
#    cv2.imwrite('picture/1111.jpg', im)
#    cv2.waitKey(0)

def cvDemo():
    
    if cap.isOpened() is False:
        print("Error opening the camera")
        return
    while cap.isOpened():
        ret,frame = cap.read()

        if ret is True:
            # Display the captured frame:
            testIm(frame)
    
            # Press q on keyboard to exit the program
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        # Break the loop
        else:
            break
        
    


if __name__ == '__main__':
    net = FaceBox()
    net.load_state_dict(torch.load('weight/faceboxes.pt', map_location=lambda storage, loc:storage), strict=False) 
    net.eval()
    data_encoder = DataEncoder()

    # given image path, predict and show
    root_path = "picture/"
    #picture = 'img_36.jpg' timg.jpg
    picture = 'timg.jpg'
    #testIm(root_path + picture)
    #im = cv2.imread(root_path + picture)
    cap = cv2.VideoCapture(0)
    cvDemo()
    cap.release()
    cv2.destroyAllWindows()

