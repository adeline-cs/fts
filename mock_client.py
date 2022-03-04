# Author: lijunshi
# Date: 2018-10-28
# Email: lijunshi2015@163.com

# --------------------------------------------------------
# A simple client simulator for FTS
# This simulator will send OCR service request to FTS server to
# test the performance and stability of FTS system.
# --------------------------------------------------------

import json
from socket import *
import time
import logging
import os
import multiprocessing as mp
import random
import argparse
import base64
from network_lib.job_descriptor import JobDescriptor
logging.basicConfig(level=logging.DEBUG)

HOST = '127.0.0.1'
PORT = 9999
IMAGE_PATH = './test_images'
image_list = os.listdir(IMAGE_PATH)


class Client(object):
    def __init__(self):
        self.s = socket(AF_INET, SOCK_DGRAM)
        self.s.connect((HOST, PORT))
        self.t = None
        self.id = 1

    def __del__(self):
        self.s.close()

    def test(self):
        while True:
            # message = raw_input('send message:>>')
            random.shuffle(image_list)
            for i in range(len(image_list)):
                image_path = os.path.join(IMAGE_PATH, image_list[i])
                jd = JobDescriptor()
                jd.set_field("name", "ocr_req")
                jd.set_field("file_path", image_path)
                jd.set_field("text_loc_save", "True")
                jd.set_field("text_save", "False")
                jd.set_field("debug", "1")
                img_file = open(image_path, 'rb')
                img_b64encode = base64.b64encode(img_file.read())
                img_file.close()
                print(type(img_b64encode))
                #jd.set_field("images64", img_b64encode)
                json_msg = jd.to_json_str()
                print("send msg size is %s" % len(json_msg))
                logging.info("Client %s: send data is %s", self.id, json_msg)
                t1 = time.time()
                self.s.sendall(json_msg.encode('utf-8'))
                data = self.s.recv(1024 * 5)
                t2 = time.time()
                logging.info("Client %s: Recv OCR response, OCR time cost is %s s", self.id, t2 - t1)
                logging.debug("Client %s: Recv is %s", self.id, data.decode('unicode-escape'))
                time.sleep(5)

    def run(self):
        self.t = mp.Process(target=Client.test, args=(self,))
        self.t.daemon = True
        self.t.start()

"""
s = socket(AF_INET, SOCK_DGRAM)
s.connect((HOST, PORT))
while True:
    # message = raw_input('send message:>>')
    for i in range(len(image_list)):
        image_path = os.path.join(IMAGE_PATH, image_list[i])
        jd = JobDescriptor()
        jd.set_field("name", "ocr_req")
        jd.set_field("file_path", image_path)
        jd.set_field("text_loc_save", "True")
        jd.set_field("text_save", "False")
        jd.set_field("debug", "1")
        json_msg = jd.to_json_str()
        logging.debug("send data is %s", json_msg)
        t1 = time.time()
        s.sendall(json_msg.encode('utf-8'))
        data = s.recv(1024*5)
        t2 = time.time()
        logging.info("OCR time cost is %s s", t2-t1)
        logging.debug("recv is %s", data.decode('utf-8'))
        time.sleep(5)
s.close()
"""


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

