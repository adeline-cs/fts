# Author: heyue
# Date: 2020-8-8
# Email: heyue_hent@163.com


import time
import logging
import multiprocessing as mp
from socket import *
from abc import abstractmethod, ABCMeta
from network_lib.job_descriptor import JobDescriptor
import json

logging.basicConfig(level=logging.DEBUG)

HOST = '127.0.0.1'
PORT = 9999


class Proxy(object):

    def __init__(self):
        self.out_channel = None
        self.t = None
        self.s = socket(AF_INET, SOCK_DGRAM)
        self.s.bind((HOST, PORT))


    def rebuild_jd_instance(self, jd_str, addr):
        new_jd = JobDescriptor()
        new_jd.set_field("addr", str(addr))
        new_jd.set_field("data", jd_str)
        # logging.debug("new job is %s", new_jd.to_json_str())
        return new_jd


    @abstractmethod
    def send(self, job):
        response_address = job.get_field("addr", "-1")
        response_address = eval(response_address.replace(')(', '),('))
        logging.debug("send addr is %s", response_address)
        response = job.get_field("response", "-1")
        response = json.dumps(response)
        #self.s.sendto(str(response).encode('utf-8'), tuple(response_address))
        self.s.sendto(response, tuple(response_address))

    def accept(self):
        # logging.info("proxy: ------ Network Proxy Service Start ------")
        while True:
            logging.info("proxy: ------ Network Proxy Service Start ------")
            data, address = self.s.recvfrom(1024*1024)
            logging.debug("raw data is %s", data)
            job = self.rebuild_jd_instance(data, address)
            self.out_channel.emit_a_job(job)
            logging.debug("proxy: data is %s, address is %s", data, address)

    def run(self):
        self.t = mp.Process(target=Proxy.accept, args=(self,))
        self.t.daemon = True
        self.t.start()
