#coding:utf-8
# Author: heyue
# Date: 2020-10-8
# Email: heyue_hent@163.com

# --------------------------------------------------------
# A simple client 1 simulator for FTS
# This simulator will send OCR service request to FTS server to
# test the performance and stability of FTS system.
# --------------------------------------------------------

import time
import os
import multiprocessing as mp
import random
import argparse
import base64
import cv2
import json
import requests
import numpy as np
import urllib

HOST = '127.0.0.1'
PORT = 9997
IMAGE_PATH = './test_images'
image_list = os.listdir(IMAGE_PATH)
result_dir = './receive_result'

class Client(object):
    def __init__(self):
        self.t = None
        self.id = 1

    def test(self):
        while True:
            # message = raw_input('send message:>>')
            res={}
            random.shuffle(image_list)
            for i in range(len(image_list)):
                image_path = os.path.join(IMAGE_PATH, image_list[i])
                save_extension='pdf'### add the file extension type
                #img = cv2.imread(image_path)
                img_file = open(image_path, 'rb')
                img_b64encode = base64.b64encode(img_file.read()).decode()
                print(type(img_b64encode))
                res = {"image": img_b64encode,
                       "image_name": image_list[i],
                       "name": "ocr_req",
                       "need_text_file": "True",
                       "need_text_loc": "True",
                       "rotate_img_vis": "True",
                       "table_detect_vis": "True",
                       "save_docx": "True",
                       "use_correct": "False",
                       "save_extension": save_extension
                      }
                print(res)
                s = requests.post("http://" + HOST + ":" + str(PORT), data=json.dumps(res))
                response = s.text
                print("\n\n\n\n\n\nclient %d rev a response:" % self.id)
                #print(response.decode('unicode_escape'))
                print(response.encode('utf-8').decode('unicode_escape'))
                response_path=json.loads(response)["download"]
                print(response_path)

                if not os.path.exists(result_dir):
                    os.mkdir(result_dir)
                url= "http://"+ HOST + ":" + str(PORT)+'/'+response_path
                print(url)
                save_path=result_dir+'/'+image_list[i].split('.')[0]+'.'+save_extension
                print(save_path)
                try:
                    urllib.request.urlretrieve(url,save_path)
                except Exception as e:
                    print("Error occurred when downloading file, error message:")
                    print(e)
                time.sleep(10)
                 

    def run(self):
        self.t = mp.Process(target=Client.test, args=(self,))
        self.t.daemon = True
        self.t.start()


def args_parse():
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--client_num", required=False,
        help="client number", default='1')

    args = vars(ap.parse_args())
    return args



if __name__ == '__main__':
    ap = args_parse()
    CLIENT_NUM = int(ap['client_num'])
    client_list = []
    for i in range(CLIENT_NUM):
        client = Client()
        client.id = i
        client.run()
        client_list.append(client)

    for i in range(CLIENT_NUM):
        client_list[i].t.join()
