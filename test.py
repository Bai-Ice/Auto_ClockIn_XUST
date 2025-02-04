# coding=utf-8 
from selenium import webdriver
import time
# from webdriver.chrome.options import Options
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
import configparser
import os
import sys, traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

mobile_emulation = {"deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},
                    "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"}

# 配置加载策略
# desired_capabilities = DesiredCapabilities.CHROME  # 修改页面加载策略
# desired_capabilities["pageLoadStrategy"] = "eager"  # 注释这两行会导致最后输出结果的延迟，即等待页面加载完成再输出
chrome_options = Options()  # 实例化一个启动参数对象

chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)  # 这里看清楚了，不是add_argument
# chrome_options.add_argument('--window-size=1366,1400')  # 设置浏览器窗口大小
prefs = {"profile.managed_default_content_settings.images": 2, 'permissions.default.stylesheet': 2}  # 禁止加载图片和CSS样式
chrome_options.add_experimental_option("prefs", prefs)


chrome_options.add_argument('window-size=1024,768')  # 16年之后，chrome给出的解决办法，抢了PhantomJS饭碗
chrome_options.add_argument('--headless')  # 16年之后，chrome给出的解决办法，抢了PhantomJS饭碗
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')  # root用户不加这条会无法运行
# driver = webdriver.Chrome(options=chrome_options)  # 获取浏览器句柄


# 1.打开浏览器
def fun1(uid):

    driver = webdriver.Chrome(options=chrome_options)  # 获取浏览器句柄
    try:
        wait = WebDriverWait(driver, 3)  # 后面可以使用wait对特定元素进行等待
        # 3.访问打卡页面并模拟点击来打卡
        url_login = "http://ehallplatform.xust.edu.cn/default/jkdk/mobile/mobJkdkAdd_test.jsp?uid="+ uid

        driver.get(url=url_login)
        # driver.find_elements(By.CSS_SELECTOR,url_login)
        # driver.find_element(By.CSS_SELECTOR)

        time.sleep(3)

        driver.execute_script('$("#ssq").show();')
        driver.execute_script('$("#xxd").show();')
        driver.execute_script('$("#hqddlx").val("2");')
        driver.execute_script('$("#guo").val("中国");')
        driver.execute_script('''$("#sheng").val('陕西省');''')
        driver.execute_script('''$("#shi").val('西安市');''')
        driver.execute_script('''$("#xian").val('碑林区');''')
        driver.execute_script('''$("#szdd4").val('中国 陕西省 西安市 碑林区');''')
        driver.execute_script('''$(".szdd4").text('中国 陕西省 西安市 碑林区');''')
        driver.execute_script('''$("#jingdu").val('108.967363');''')
        driver.execute_script('''$("#weidu").val('34.231581');''')

        time.sleep(1)
        input = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input.srk.jiaodian')))

        target = driver.find_elements(by=By.CSS_SELECTOR,value='input.srk.jiaodian')[1]
        driver.execute_script("arguments[0].scrollIntoView();", target)


        time.sleep(2)
        driver.find_elements(by=By.CSS_SELECTOR,value='input.srk.jiaodian')[1].click()

        driver.switch_to.active_element.send_keys(u'西安科技大学')

        # 今日体温
        jQuery = r'$("input[name=\'jrtwfw5\']")[0].click()'
        driver.execute_script(jQuery)
        radios = driver.find_elements(by=By.CSS_SELECTOR,value='input[type=radio]')
        for radio in radios:
            if radio.get_attribute(u"name") == u"jrsfzx3" and radio.get_attribute(u"value") == u"是":
                if not radio.is_selected():
                    radio.click()
                    print("今日在校：" + radio.get_attribute("value"))

            # if radio.get_attribute(u"name") == u"jrtwfw5" and radio.get_attribute(u"value") == u"正常体温:36～37.2℃":
            #     if not radio.is_selected():
            #         radio.click()
        # 获取提交按钮并点击	jiaodian = driver.find_elements_by_xpath('//*[@id="xxd"]/ul/li/input')[0]
        driver.find_elements(by=By.CSS_SELECTOR,value='span#submit')[0].click()

        dig_confirm = driver.switch_to.alert
        # 打印对话框的内容
        print(dig_confirm.text)
        # 点击“确认”按钮
        dig_confirm.accept()

        try:
            driver.find_elements(by=By.XPATH,value="//*[text()='已完成']")
            driver.quit()
            print("\t打卡成功")
            return True, "none"
        except Exception as e:
            print(traceback.format_exc())
            return False, e
        finally:
            driver.quit()
    except Exception as e:
        print(traceback.format_exc())
        driver.quit()
        return False, e


def daka(uid, SERVERPUSHKEY, MSG_TO):


    status, e = fun1(uid)
    desp = ""
    if (status == False):
        print("重新再次打卡")
        status, e = fun1(uid)
        if (status == False):
            text = "打卡失败:"
            print("打卡失败")
            desp = str(e)
        else:
            text = "打卡成功:"
    else:
        text = "打卡成功:"

    if SERVERPUSHKEY:
        if text == "打卡失败:":
            driver = webdriver.Chrome(options=chrome_options)  # 获取浏览器句柄
            url = "https://sc.ftqq.com/" + SERVERPUSHKEY + ".send?text=" + text
            if (len(desp)):
                url += "desp=" + desp
            driver.get(url)
    elif MSG_TO:
        pass
    else:
        pass

UID=os.environ["UID"]
SERVERPUSHKEY = None
MSG_TO = None
if "SERVERPUSHKEY" in os.environ:
    SERVERPUSHKEY = os.environ["SERVERPUSHKEY"]
if "MSG_TO" in os.environ:
    MSG_TO = os.environ["MSG_TO"]

daka(UID, SERVERPUSHKEY, MSG_TO)
