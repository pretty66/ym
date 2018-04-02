import configparser
import os

# 工具类
class Common(object):
    def __init__(self):
        # 配置
        self.config = None

    def getConfig(self, section, key):
        if not self.config :
            self.config = configparser.ConfigParser()
            path = os.path.split(os.path.realpath(__file__))[0] + '/config.ini'
            self.config.read(path, encoding='utf-8')
        return self.config.get(section, key)
common = Common()