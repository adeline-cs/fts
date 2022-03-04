# Author: heyue
# Date: 2020-8-8
# Email: heyue_hent@163.com


import json

class JobDescriptor(object):
    def __init__(self, **kwargs):
        self.job = {}
        for k, v in kwargs.items():
            self.job[k] = v

    def set_field(self, k, v):
        self.job[k] = v
        return self

    def get_field(self, k, default_value=None):
        return self.job.get(k, default_value)

    def to_json_str(self):
        return json.dumps(self.__dict__)

    @property
    def name(self):
        return self.job.get("name")
