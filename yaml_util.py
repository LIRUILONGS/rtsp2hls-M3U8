#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   yaml_util.py
@Time    :   2022/03/22 14:10:46
@Author  :   Li Ruilong
@Version :   1.0
@Contact :   1224965096@qq.com
@Desc    :   加载配置文件

pip install pyyaml 
"""

# here put the import lib

import os
import time
import yaml
import logging
import json

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

class Yaml:
    _config = None

    def __new__(cls, *args, **kw):
        # hasattr函数用于判断对象是否包含对应的属性。
        if not hasattr(cls, '_instance'):
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, file_name="config.yaml"):
        config_temp = None
        try:
            # 获取当前脚本所在文件夹路径
            cur_path = os.path.dirname(os.path.realpath(__file__))
            # 获取yaml文件路径
            yaml_path = os.path.join(cur_path, file_name)

            f = open(yaml_path, 'r', encoding='utf-8')
            config_temp = f.read()
        except Exception as e:
            logging.info("配置文件加载失败", e)
        finally:
            f.close()
        self._config = yaml.safe_load(config_temp)  # 用load方法转化


    def __str__(self):
        return json.dumps(self._config,indent=4)

    def __del__(self):
        self._config = None
        self = None


    @staticmethod
    def get_config(file_name="config.yaml"):
        config = Yaml(file_name)._config
        logging.info("加载配置数据："+str(config))
        return config

    @staticmethod
    def refresh_config(cls, file_name="config.yaml"):
        del cls
        return Yaml(file_name)._config

def set_config(contain, file_name="config_.yaml"):
    # 配置字典由内存导入静态文件
    cur_path = os.path.dirname(os.path.realpath(__file__))
    yaml_path = os.path.join(cur_path, file_name)
    with  open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(contain, f)

def get_yaml_config(file_name="config.yaml"):
    # 配置文件读入内存为配置字典
    config =  Yaml.get_config(file_name) 
    return config


def refresh_yaml_config(cls, file_name="config.yaml"):
    # 配置文件的动态加载读入内存为字典
    return Yaml.refresh_config(cls,file_name)


if __name__ == '__main__':
    my_yaml_1 = Yaml()
    my_yaml_2 = Yaml()
    #id关键字可用来查看对象在内存中的存放位置
    print(id(my_yaml_1) == id(my_yaml_2))
    time.sleep(10)
    # 修改配置文件后从新加载配置字典会刷新
    refresh_yaml_config(my_yaml_1)

