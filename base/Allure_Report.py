import subprocess

from utils.LogUtil import my_log

log =my_log("allure_generate")
#1、allure_cmd命令
def allure_generate(report_path,report_html):
    allure_cmd = "allure generate %s -o %s --clean"%(report_path,report_html)
    print(allure_cmd)
#2、subprocess.call
    log.info("report_path is %s",report_path)
    try:
        subprocess.call(allure_cmd,shell=True)
        log.info("report_html is %s", report_html)
    except Exception as e:
        log.error("generate report fail please check!")
        raise e