# -*- coding: utf-8 -*-
"""
# Author: heyue
# Date: 2020-8-6
# Email: heyue_hent@163.com
@description: 
"""

import os

pwd_path = os.path.abspath(os.path.dirname(__file__))

bert_model_dir = os.path.join(pwd_path, '../data/bert_models/chinese_finetuned_lm/')
bert_model_path = os.path.join(pwd_path, '../data/bert_models/chinese_finetuned_lm/pytorch_model.bin')
bert_config_path = os.path.join(pwd_path, '../data/bert_models/chinese_finetuned_lm/config.json')
