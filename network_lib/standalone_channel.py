# -*- coding: utf-8 -*-
# Author: heyue
# Date: 2020-8-8
# Email: heyue_hent@163.com

from abc import abstractmethod, ABCMeta

''' standalone communication mode(IPC) '''

from network_lib.channel import Channel
import multiprocessing as mp


class Standalone(Channel):
    def __init__(self):
        self.q = None

    def init_channel(self):
        if self.q is None:
            self.q = mp.Queue()

    def shutdown_channel(self):
        pass

    def pull_a_job(self):
        try:
            return self.q.get()
        except Exception:
            return None

    def emit_a_job(self, job):
        try:
            self.q.put(job)
            return True
        except Exception:
            return False

    @abstractmethod
    def get_qsize(self):
        return self.q.qsize()
