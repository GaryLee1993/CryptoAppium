import os

# 1、获取项目基本目录
# print(__file__)
# print(os.path.dirname(__file__))
# print(os.path.dirname(os.path.dirname(__file__)))
from utils.YamlUtil import YamlReader

current = os.path.dirname(os.path.dirname(__file__))
# 2、conf目录
conf_path = current + os.sep + "conf"
conf_path_yml = conf_path + os.sep + "conf.yml"
# print(conf_path)
# 3、caps.yml
conf_caps = conf_path + os.sep + "caps.yml"
# print(conf_caps)

# log目录
log_path = current + os.sep + "logs"
# keywords文件目录
keywords_path = conf_path + os.sep + "keywords.yml"

# data目录
data_path = current + os.sep + "data"
# data测试用例文件
testcase_file = data_path + os.sep + "data.xls"
# report目录
report_path = current + os.sep + "report"

# 定义app安装目录的路径
_app_path = current + os.sep + "app"

# 1、通过yamlreader获取data
config = YamlReader(conf_path_yml).data()
# 2、根据key来获取对应的内容
print(config["EMAIL"])

def get_app_path():
    return _app_path

def get_report_path():
    return report_path

def get_data_path():
    return data_path

def get_config_path():
    return conf_path

def get_log_path():
    return log_path
