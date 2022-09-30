import time
from config import RunConfig
from data.ExcelConfig import TestSteps, Elements, CaseData, TestCases
from base.BaseAction import Action, screenshot_allure
from utils.ExcelInputHandler import ExcelInputHandler
from utils.GetAllKeyValue import GetKeyValue
from utils.LogUtil import my_log
from selenium.webdriver import Chrome, ChromeOptions
from conf import Conf
from utils.YamlUtil import YamlReader
import allure
import platform

"""
1、重构，代码整理
2、pytest测试用例编写，新建测试文件
3、pytest框架用例执行，run.py，pytest.ini
4、运行及调试
"""

#//*[text()='默认商品8'] web
#//*[@text='帐号与安全'] app

#
log = my_log("operate")

import json


# data = Data(Conf.testcase_file)
# #执行测试用例列表
# run_list = data.run_list()


class Operate():
    def __init__(self, driver):
        self.driver = driver
        self.gb = globals()

    @staticmethod
    def start_web_driver():
        if RunConfig.is_local:
            opt = ChromeOptions()  # 创建Chrome参数对象
            opt.add_argument('--no-sandbox')
            opt.add_argument('--start-maximized')
            opt.add_argument('--disable-gpu')
            webdriver = Chrome(options=opt)
            return webdriver
        else:
            opt = ChromeOptions()  # 创建Chrome参数对象
            opt.add_argument('--no-sandbox')
            opt.add_argument('--headless')  # 把Chrome设置成可视化无界面模式
            opt.add_argument('--disable-gpu')
            opt.add_argument('--window-size=1920,1080')
            if platform.platform() == "Windows-10-10.0.19044-SP0":
                print("Windows创建drivier中")
                webdriver = Chrome(options=opt)
                return webdriver
            else:
                webdriver = Chrome(executable_path='/usr/bin/chromedriver', options=opt)
                print("Linux创建drivier中")
                return webdriver

    def get_keyword(self, name):
        # 1、读取配置文件，文件路径：绝对路径
        keyword_file = Conf.keywords_path
        # 2、YamlReader，data()
        reader = YamlReader(keyword_file).data()
        # 3、key获取值 name
        value = reader[name]
        return value

    def str_to_dict(self, content, globaldict=globals()):
        totalfunctionlist = []
        totalfunctionlistno = []
        resultdict = {}
        if content and not isinstance(content, dict):
            innerkwargs = json.loads(content)
        elif content and isinstance(content, dict):
            innerkwargs = content
        elif not content:
            innerkwargs = {}
        gv = GetKeyValue(innerkwargs, mode='j')
        innerwithparamlist, innerwithoutparamlist, after_json_object = gv.extract_func_name_from_str(innerkwargs)
        totalfunctionlist.extend(innerwithparamlist)
        totalfunctionlistno.extend(innerwithoutparamlist)

        for i in totalfunctionlist:
            res = ExcelInputHandler.handle_excel_pre_with_param(i, content)
            resultdict.update(res)
        for i in totalfunctionlistno:
            res = ExcelInputHandler.handle_excel_pre_without_param(i)
            resultdict.update(res)

        gv.json_get_actual_value_from_result_dict(after_json_object, resultdict, globaldict)
        globaldict.update(after_json_object)
        return after_json_object

    def test_run(self, run_case):
        log.info("执行用例内容:{}".format(run_case))
        self.step(run_case)

    @screenshot_allure
    def step(self, data, run_case):
        platformdriverdict = {}
        tc_id = run_case[TestSteps.STEP_TC_ID]
        # 获取步骤
        steps = data.get_steps_by_tc_id(tc_id)
        clear_before = run_case[TestCases.CASE_CLEAR_ENVIRONMENT_BEFORE_RUN]
        if clear_before.upper() == "Y" or clear_before.upper() == "YES":
            print("前置清理环境中.....")
            #PersonTearDown.total_tear_down()
            time.sleep(2)

        clear_after = run_case[TestCases.CASE_CLEAR_ENVIRONMENT_AFTER_RUN]
        # allure报告
        # feature
        allure.dynamic.feature(run_case[TestCases.CASES_NOTE])
        # story
        allure.dynamic.story(run_case[TestCases.CASES_DESC])
        # title
        allure.dynamic.title(run_case[CaseData.DATA_CASE_ID] + "-" + run_case[CaseData.DATA_NAME])
        platformtypelist = []
        for i in steps:
            platformtypelist.append(i[TestSteps.WEB_TYPE])
        distinctplatformlist = list(set(platformtypelist))
        for i in distinctplatformlist:
            if i and i.upper() == "MALL":
                backdriver = Operate.start_web_driver()
                backdriver.get(RunConfig.MALL_WEB_URL)
                backdriver.maximize_window()
                platformdriverdict.update(
                    {"%s_window" % i.upper(): backdriver.current_window_handle,
                     "%s_driver" % i.upper(): backdriver})
            elif i and i.upper() == "MANAGER":
                backdriver = Operate.start_web_driver()
                backdriver.get(RunConfig.MANAGE_WEB_URL)
                backdriver.maximize_window()
                platformdriverdict.update(
                    {"%s_window" % i.upper(): backdriver.current_window_handle,
                     "%s_driver" % i.upper(): backdriver})
            elif i and i.upper() == "MAINPAGE":
                backdriver = Operate.start_web_driver()
                backdriver.get(RunConfig.MAIN_PAGE_WEB_URL)
                backdriver.maximize_window()
                platformdriverdict.update(
                    {"%s_window" % i.upper(): backdriver.current_window_handle,
                     "%s_driver" % i.upper(): backdriver})
        data_input = run_case[CaseData.DATA_INPUT]
        send = self.str_to_dict(data_input, self.gb)

        for step in steps:
            log.debug("执行步骤{}".format(step))
            # 获取元素信息
            element_name = step[TestSteps.STEP_ELEMENT_NAME]
            element_index = step[TestSteps.STEP_ELEMENT_INDEX]
            element = data.get_element_by_element_name(step[TestSteps.STEP_TC_ID], element_name)
            log.debug("元素信息{}".format(element))
            # 操作步骤 关键表映射 click_btn
            operate = self.get_keyword(step[TestSteps.STEP_OPERATE])
            # 操作判断，是否存在，不存在不执行步骤
            platformtype = step[TestSteps.WEB_TYPE]
            expect = step[TestSteps.STEP_EXPECT_RESULT]
            if platformtype:
                currenthwindow=platformdriverdict["%s_driver" % platformtype.upper()].current_window_handle
                platformdriverdict["%s_driver" % platformtype.upper()].switch_to.window(
                    currenthwindow)
                print("现在正在操作%s!" % platformdriverdict["%s_driver" % platformtype.upper()].title)
            if operate and element:
                # 定义方法参数：字典
                param_value = dict()
                # 根据getattr判断执行哪个方法
                if platformtype:
                    action_method = getattr(
                        Action(self.driver, platformdriverdict["%s_driver" % platformtype.upper()], self.gb),
                        operate)
                else:
                    action_method = getattr(Action(self.driver, None, self.gb),
                                            operate)
                log.debug("该关键字是{}".format(operate))
                # 定义具体的参数
                by = element[Elements.ELE_BY]
                value = element[Elements.ELE_VALUE]
                location_type = element[Elements.ELE_LOCATION_TYPE]

                # 1、获取by,value,send_value内容
                send_value = step[TestSteps.STEP_DATA]
                # 2、send_value内容转换，通过case data数据内容
                param_value["by"] = by
                param_value["value"] = value
                param_value["locatetype"] = location_type

                if isinstance(element_index, str) and "global_" in element_index and element_index.split("global_")[
                    1] in self.gb.keys():
                    dealelementindex = self.gb[element_index.split("global_")[1]]
                    param_value["elementindex"] = dealelementindex
                if isinstance(expect, str) and "global_save_" in expect:
                    param_value["paramkey"] = expect
                if isinstance(expect, str) and "global_" in expect and "_fix_" not in expect and expect.split("global_")[1] in self.gb.keys():
                    dealexpect = self.gb[expect.split("global_")[1]]
                    param_value["expect"] = dealexpect
                elif isinstance(expect, str) and "global_" in expect and "_fix_"  in expect and expect.split("global_")[1] in self.gb.keys():
                    prestr=expect.split("_fix_")[0]
                    afterstr=self.gb[expect.split("_fix_")[1].split("global_")[1]]
                    dealexpect = prestr+afterstr
                    print("拆分结合后的str为")
                    print(dealexpect)
                    param_value["expect"] = dealexpect
                elif isinstance(expect, str) and "global_" not in expect:
                    dealexpect = expect
                    param_value["expect"] = dealexpect
                elif expect and isinstance(expect, float):
                    dealexpect = expect
                    param_value["expect"] = float(dealexpect)
                elif expect and isinstance(expect, int):
                    dealexpect = expect
                    param_value["expect"] = int(dealexpect)
                elif expect and isinstance(expect, bool):
                    dealexpect = expect
                    param_value["expect"] = bool(dealexpect)
                # 判断假如有输入内容 字符转换
                if send_value:
                    if type(send[send_value]) == str and "global_" in send[send_value]:
                        if len(send[send_value].split("_")) == 2 and send[send_value].split("_")[
                            1] in self.gb.keys():
                            param_value["send"] = self.gb[send[send_value].split("_")[1]]
                            log.debug("发出的内容为:{}".format(self.gb[send[send_value].split("_")[1]]))
                        elif len(send[send_value].split("_")) == 3 and send[send_value].split("_")[
                            2] in self.gb.keys():
                            if send[send_value].split("_")[1].upper() == "STR":
                                param_value["send"] = str(self.gb[send[send_value].split("_")[2]])
                                log.debug("发出的内容为:{}".format(str(self.gb[send[send_value].split("_")[2]])))
                            elif send[send_value].split("_")[1].upper() == "INT":
                                param_value["send"] = int(self.gb[send[send_value].split("_")[2]])
                                log.debug("发出的内容为:{}".format(str(self.gb[send[send_value].split("_")[2]])))
                            elif send[send_value].split("_")[1].upper() == "FLOAT":
                                param_value["send"] = float(self.gb[send[send_value].split("_")[2]])
                                log.debug("发出的内容为:{}".format(str(self.gb[send[send_value].split("_")[2]])))
                    else:
                        param_value["send"] = send[send_value]
                        log.debug("发出的内容为:{}".format(str(send[send_value])))
                # step
                with allure.step(step[TestSteps.STEP_NAME]):
                    res = action_method(**param_value)
                    if expect and isinstance(expect, str) and "global_save_" in expect and res and isinstance(res,
                                                                                                              dict) and \
                            expect.split("global_save_")[
                                1] in res.keys():
                        self.gb.update(res)
                        # 把页面获取的东西同步更新到send 一遍后面作为入参 但是请确保这个key 要和已有的send中的key 不重复
                        send.update(res)

            elif operate and not element and not expect and not element_index:
                if platformtype:
                    action_method = getattr(
                        Action(self.driver, platformdriverdict["%s_driver" % platformtype.upper()]),
                        operate, self.gb)
                else:
                    action_method = getattr(Action(self.driver, None),
                                            operate, self.gb)
                log.debug("该关键字是{}".format(operate))
                with allure.step(step[TestSteps.STEP_NAME]):
                    action_method()

            # 通过方法获取数组的长度然后更新element中的index
            elif operate and not element and not expect and element_index and "global_save_" in element_index:
                if platformtype:
                    action_method = getattr(
                        Action(self.driver, platformdriverdict["%s_driver" % platformtype.upper()]),
                        operate, self.gb)
                else:
                    action_method = getattr(Action(self.driver, None),
                                            operate, self.gb)
                log.debug("该关键字是{}".format(operate))
                with allure.step(step[TestSteps.STEP_NAME]):
                    res = action_method()
                    if res and isinstance(res,
                                          dict) and \
                            element_index.split("global_save_")[
                                1] in res.keys():
                        self.gb.update(res)
                    else:
                        pass

            # 这种方式是调用的方法需要入参 通过expect 传入
            elif operate and not element and expect and "global_" in expect and "_fix_" not in expect:
                param_value = dict()
                if isinstance(expect, str) and "," not in expect:
                    dealexpect = self.gb[expect.split("_")[1]]
                    param_value["expect"] = dealexpect
                elif isinstance(expect, str) and ","  in expect:
                    paramlist=[]
                    for i in expect.split(","):
                        paramlist.append(self.gb[i.split("_")[1]])
                    param_value["expect"]=paramlist
                if platformtype:
                    action_method = getattr(
                        Action(self.driver, platformdriverdict["%s_driver" % platformtype.upper()]),
                        operate, self.gb)
                else:
                    action_method = getattr(Action(self.driver, None),
                                            operate, self.gb)
                log.debug("该关键字是{}".format(operate))
                with allure.step(step[TestSteps.STEP_NAME]):
                    res = action_method(**param_value)
                    print(res)

            elif operate and not element and expect and "global_" not in expect:
                param_value = dict()
                if isinstance(expect, str):
                    param_value["expect"] = expect
                if platformtype:
                    action_method = getattr(
                        Action(self.driver, platformdriverdict["%s_driver" % platformtype.upper()]),
                        operate, self.gb)
                else:
                    action_method = getattr(Action(self.driver, None),
                                            operate, self.gb)
                log.debug("该关键字是{}".format(operate))
                with allure.step(step[TestSteps.STEP_NAME]):
                    res = action_method(**param_value)
                    print(res)

            else:
                log.error("没有operate信息：{}".format(operate))

        for k, v in platformdriverdict.items():
            if k.endswith("_driver"):
                platformdriverdict[k].close()
        #TestKeyword.teardown()

        if clear_after.upper() == "Y" or clear_before.upper() == "YES":
            print("后置清理环境中....")
            #PersonTearDown.total_tear_down()
            time.sleep(2)


# allure定制测试报告
# 1、testcases 备注 feature
# 2、testcases 描述 story
# 3、casedata case_id+用例名称  title
# 4、teststeps 步骤名称 step
if __name__ == '__main__':
    op = Operate(driver=None)
    content = {
        "username": "pre.reflect_config_utils.ReflectConfig.get_randomtelphone[username]",
        "verifycode": "666666",
        "firstname": "李",
        "secondname": "嘉睿",
        "email": "ljrdemail@sohu.com",
        "shop_editor_username_back": "pre.reflect_config_utils.ReflectConfig.get_reflect_config[BRAND_SHOP_EDITOR_USERNAME_2]",
        "shop_editor_password_back": "pre.reflect_config_utils.ReflectConfig.get_reflect_config[BRAND_SHOP_EDITOR_PASSWORD_2]",
        "shop_editor_phone_back_second": "pre.reflect_config_utils.ReflectConfig.get_reflect_config[BRAND_SHOP_EDITOR_SECOND_TELEPHONE_2]",
        "shop_editor_password_back_two": "pre.reflect_config_utils.ReflectConfig.get_reflect_config[BRAND_SHOP_EDITOR_SECOND_PASSWORD_2]",
        "memeberno": "pre.reflect_config_utils.ReflectConfig.get_mem_card_no[memeberno]",
        "accumulatecost": "1000",
        "shop_auditor_username_back": "pre.reflect_config_utils.ReflectConfig.get_reflect_config[BRAND_SHOP_AUDITOR_USERNAME_2]",
        "shop_auditor_password_back": "pre.reflect_config_utils.ReflectConfig.get_reflect_config[BRAND_SHOP_AUDITOR_PASSWORD_2]",
        "shop_auditor_phone_back_second": "pre.reflect_config_utils.ReflectConfig.get_reflect_config[BRAND_SHOP_AUDITOR_SECOND_TELEPHONE_2]",
        "shop_auditor_password_back_two": "pre.reflect_config_utils.ReflectConfig.get_reflect_config[BRAND_SHOP_AUDITOR_SECOND_PASSWORD_2]",
        "shop_deployer_username_back": "pre.reflect_config_utils.ReflectConfig.get_reflect_config[BRAND_SHOP_DEPLOYER_USERNAME_2]",
        "shop_deployer_password_back": "pre.reflect_config_utils.ReflectConfig.get_reflect_config[BRAND_SHOP_DEPLOYER_PASSWORD_2]",
        "shop_deployer_phone_back_second": "pre.reflect_config_utils.ReflectConfig.get_reflect_config[BRAND_SHOP_DEPLOYER_SECOND_TELEPHONE_2]",
        "shop_deployer_password_back_two": "pre.reflect_config_utils.ReflectConfig.get_reflect_config[BRAND_SHOP_DEPLOYER_SECOND_PASSWORD_2]"
    }
    res = op.str_to_dict(content)
    print(res)
