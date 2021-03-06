# python run_video.py --model=mobilenet_v2_large --video=IMG_8209.MOV
import argparse
import logging
import time

import cv2
import numpy as np

from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh

logger = logging.getLogger('TfPoseEstimator-Video')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

fps_time = 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='tf-pose-estimation Video')
    parser.add_argument('--video', type=str, default='')
    parser.add_argument('--resolution', type=str, default='432x368', help='network input resolution. default=432x368')
    parser.add_argument('--model', type=str, default='mobilenet_thin', help='cmu / mobilenet_thin / mobilenet_v2_large / mobilenet_v2_small')
    parser.add_argument('--show-process', type=bool, default=False,
                        help='for debug purpose, if enabled, speed for inference is dropped.')
    parser.add_argument('--showBG', type=bool, default=True, help='False to show skeleton only.')
    args = parser.parse_args()

    logger.debug('initialization %s : %s' % (args.model, get_graph_path(args.model)))
    w, h = model_wh(args.resolution)
    e = TfPoseEstimator(get_graph_path(args.model), target_size=(w, h))
    cap = cv2.VideoCapture(args.video)

    if cap.isOpened() is False:
        print("Error opening video stream or file")
    while cap.isOpened():
        ret_val, image = cap.read()

        humans = e.inference(image, resize_to_default=True, upsample_size=4.0)

        # print('len(humans):',len(humans)) #frame하나당 사람의 좌표
        if not args.showBG:
            image = np.zeros(image.shape)
        (image,hands_centers) = TfPoseEstimator.draw_humans(image, humans, imgcopy=False)
        
        num_hands = len(hands_centers)
        
        if hands_centers != []:
            for i in range(num_hands):
                x = hands_centers[i][0]
                y = hands_centers[i][1]

                # hands_bbox_left_up = (x-(person_width//3, y-(person_height//24)))
                # hands_bbox_right_down = (x+(person_width//3), y+(person_height*7//24))
                
        
        # if num_hands != 0:
        #     for i in range(num_hands):
        #         print('i:',i,'hands_centers_inin:',hands_centers[i])
        
        cv2.putText(image, "FPS: %f" % (1.0 / (time.time() - fps_time)), (10, 10),  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.imshow('tf-pose-estimation result', image)
        fps_time = time.time()
        if cv2.waitKey(1) == 27:
            break

    cv2.destroyAllWindows()
logger.debug('finished+')
