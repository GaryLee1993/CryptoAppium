
from utils.LogUtil import my_log
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import allure
import datetime
import time



class Action:
    def __init__(self, driver=None, backdriver=None, outerglobal={}):
        self.driver = driver
        self.backdriver = backdriver
        self.log = my_log("Base_Page")
        self.innerglobal = outerglobal

    def scorll_down(self):
        time.sleep(1)
        screen = self.driver.get_window_size()
        self.driver.swipe(screen["width"] * 0.5, screen["height"] * 3 / 5, screen["width"] * 0.5,
                          screen["height"] * 1 / 5,
                          3000)


    def print_app_content(self, **kwargs):
        try:
            by = kwargs["by"]
            value = kwargs["value"]
            if by.upper() == "ID":
                ele = self.by_find_element(By.ID, value)
            elif by.upper() == "XPATH":
                ele = self.by_find_element(By.XPATH, value)
            elif by.upper() == "CLASS_NAME":
                ele = self.by_find_element(By.CLASS_NAME, value)
            self.log.info("获取页面内容为：{}".format(ele.text))
            return True
        except Exception as e:
            self.log.error("获取页面元素内容失败，错误信息：{}".format(e))
            return 0

    def click_btn(self, **kwargs):
        # 根据by类型，进行by_id,by_xpath方法调用
        by, value = kwargs["by"], kwargs["value"]
        if by == "id":
            loc = self.by_find_element(By.ID, value)
        elif by == "xpath":
            loc = self.by_find_element(By.XPATH, value)
        loc.click()

    def by_find_element(self, by, value, timeout=60, poll=0.5):
        """
        隐式等待，寻找元素
        :param by:
        :param value:
        :param timeout:
        :param poll:
        :return:
        """
        try:
            WebDriverWait(self.driver, timeout, poll).until(lambda x: x.find_element(by, value))
            return self.driver.find_element(by, value)
        except Exception as e:
            self.log.error("没有找到该元素：{}".format(e))

# 定义装饰器
# 1、定义装饰2层函数
def screenshot_allure(func):
    def get_err_screenshot(self, *args, **kwargs):
        # 2、定义内部函数，拍图操作
        try:
            func(self, *args, **kwargs)
        except Exception as e:
            png = self.driver.get_screenshot_as_png()
            name = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            allure.attach(png, name, allure.attachment_type.PNG)
            raise e

    # 3、返回内部函数名称
    return get_err_screenshot


# 4、重构toast断言
# 5、调用装饰器@

if __name__ == '__main__':
    ac = Action()
    res = ac.api_brand_advisor_loginuser()
    print(res)
