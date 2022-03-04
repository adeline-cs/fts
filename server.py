# Author: lijunshi
# Date: 2018-10-28
# Email: lijunshi2015@163.com

import logging
logging.basicConfig(level=logging.INFO)
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "5"

from algo_handler import AlogHandlerBase
from  network_lib.proxy import Proxy
from network_lib.standalone_channel import Standalone
import time


"""
HOST = '127.0.0.1'
PORT = 9999

if __name__ == '__main__':
    s = socket(AF_INET, SOCK_DGRAM)
    s.bind((HOST, PORT))
    a = AlogHandlerBase()
    print ('...waiting for message..')
    while True:
        data, address = s.recvfrom(1024)
        print (data, address)
        result = a.ocr_reco(data)
        print("System has processed one task!")

        s.sendto(str(result).encode('utf-8'), address)
    s.close()
"""


def check_service(q):
    logging.debug("current task queue size is %s", q.get_qsize())


if __name__ == '__main__':
    logging.debug("System start running...")
    algo = AlogHandlerBase()
    algo.in_channel = Standalone()
    algo.in_channel.init_channel()

    proxy = Proxy()
    proxy.out_channel = algo.in_channel

    proxy.run()

    logging.info("alog:------ AlgoHandler Service Start ------")
    while True:
        check_service(algo.in_channel)
        job = algo.in_channel.pull_a_job()
        if job is not None:
            # logging.debug("algo service recieve a job is %s", job)
            result = algo.ocr_reco(job)
            proxy.send(result)
        else:
            time.sleep(0.02)

    proxy.t.join()
