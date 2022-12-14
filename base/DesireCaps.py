#encoding:utf8
import os

from utils.YamlUtil import YamlReader
from conf import Conf
from appium import webdriver

#1、通过yaml来读取caps.yml
reader = YamlReader(Conf.conf_caps)
data = reader.data()
#2、结果，字典转换

def appium_desired_caps(host,port,systemPort="8200"):
    #2、desired创建字典
    desired_caps=dict()
    #3、platformName
    desired_caps['platformName'] = data['platformName']
    #4、platformVersion
    desired_caps['platfromVersion']=data['platfromVersion']
    #5、deviceName
    desired_caps['deviceName'] = data['deviceName']
    #安装app
    desired_caps["app"] = os.path.join(Conf.get_app_path(),data['appName'])
    #6、启动程序的包名appPackage
    desired_caps["appPackage"] = data['appPackage']
    #7、启动界面名appActivity
    desired_caps['appActivity'] = data['appActivity']
    #解决中文
    desired_caps["unicodeKeyboard"] = data['unicodeKeyboard']
    desired_caps["newCommandTimeout"] = data['newCommandTimeout']
    desired_caps["resetKeyboard"] = data['resetKeyboard']
    #获取toast automationName = uiautomator2
    desired_caps["automationName"] = data['automationName']
    #不清除app里的原有数据
    desired_caps["noReset"] = data["noReset"]
    #解决并发测试
    desired_caps["systemPort"] = systemPort
    # 8、http，连接appium服务器
    driver = webdriver.Remote('http://%s:%s/wd/hub'%(host,port), desired_caps)
    driver.implicitly_wait(200)
    return driver