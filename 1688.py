from selenium.webdriver import ActionChains  # 控制鼠标操作
from selenium.webdriver.chrome.options import Options  # 不展示浏览器窗口  测试不通过
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.chrome.service import Service
import time
from selenium import webdriver
import os
import pymysql
import json
import sys
import random


class Login(object):
    def __init__(self):
        if len(sys.argv) < 3:
            self.account = '1778973****'
            self.password = '123456'
        else:
            self.account = sys.argv[1]
            self.password = sys.argv[2]
        self.url = "https://login.1688.com/member/signin.htm"
        # self.url = "https://detail.1688.com/offer/622477660714.html"
        self.browser = 'chrome'

        if self.browser == 'chrome':
            driver_path = "D:\phpStudy\PHPTutorial\WWW\zwwl2016\python\chromedriver.exe"
            self.c_service = Service(driver_path)
            self.c_service.command_line_args()
            self.c_service.start()
            chrome_options = Options()
            chrome_options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"')
            # chrome_options.add_argument('--headless')       # 浏览器不提供可视化页面
            chrome_options.add_argument('--no-sandbox')     # 取消沙盒模式
            chrome_options.add_argument('--disable-gpu')    # 禁用GPU加速
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--start-maximized')    # 最大化运行（全屏窗口）
            chrome_options.add_argument("--incognito")      # 隐身模式启动
            # chrome_options.add_argument("disable-infobars")       # 已弃用 去掉提示：Chrome正收到自动测试软件的控制
            # chrome_options.add_experimental_option('useAutomationExtension', False)     # 去掉提示：Chrome正收到自动测试软件的控制

            # 屏蔽提示：chrome正收到自动测试软件的控制
            # 在79(含79)以后的版本无效。谷歌修复了非无头模式下排除“启用自动化”时window.navigator.webdriver是未定义的问题
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])    # 去掉提示：Chrome正收到自动测试软件的控制

            self.driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)

            # CDP执行JavaScript 代码  重定义window.navigator.webdriver的值  绕过反爬机制
            # 检测机制:
            # selenium调用驱动打开浏览器，在控制台window.navigator.webdriver会标记FALSE，
            # 手工正常打开的浏览器控制台window.navigator.webdriver的结果是True
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {
                  get: () => undefined
                })
              """
            })
        elif self.browser == 'firefox':
            driver_path = "/usr/local/bin/geckodriver"
            firefox_options = FirefoxOptions()
            firefox_options.add_argument('--headless')
            firefox_options.add_argument('--no-sandbox')
            firefox_options.add_argument('--disable-gpu')
            #             firefox_options.add_argument('--disable-dev-shm-usage')
            self.driver = webdriver.Firefox(executable_path=driver_path, firefox_options=firefox_options)
        self.driver.delete_all_cookies()
        # self.index = 'https://open.yuewen.com/pub/index/index.html'
        # self.agent = ''

    def after_quit(self):
        """
        关闭浏览器
        """
        self.driver.quit()

    #         self.driver.close()
    #         self.c_service.stop()
    # 去掉提示：Chrome正收到自动测试软件的控制
    def save_cookie(self, cookies, token):
        db = pymysql.Connect(host='127.0.0.1',
                             port=int(3306),
                             user='user',
                             passwd='password',
                             db='db_name',
                             charset='utf8mb4')
        cursor = db.cursor()
        sql = 'SELECT cookie.id FROM pigeon_spider_account_cookie cookie ' +\
            'LEFT JOIN pigeon_spider_account_center spider ' +\
            'ON spider.id = cookie.pigeon_spider_account_center_id ' + \
            'LEFT JOIN pigeon_platform_account_center account ' + \
            'ON account.id = spider.platform_account_center_id ' + \
            'WHERE account.platform= %s AND account.account = %s'
        count = cursor.execute(sql, ('1688', self.account))

        if (count > 0):
            id = cursor.fetchone()[0]
            update_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            sql = 'UPDATE pigeon_spider_account_cookie SET cookies = %s, token = %s,' + \
                  'update_time = %s WHERE id = %s'
            result = cursor.execute(sql, (cookies, token, update_at, id))
        else:
            sql = 'SELECT spider.id FROM pigeon_spider_account_center spider ' + \
                  'LEFT JOIN pigeon_platform_account_center account ' + \
                  'ON account.id = spider.platform_account_center_id ' + \
                  'WHERE account.platform= %s AND account.account = %s'
            count = cursor.execute(sql, ('1688', self.account))
            if(count > 0):
                id = cursor.fetchone()[0]
                create_at = update_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                sql = 'INSERT INTO pigeon_spider_account_cookie (pigeon_spider_account_center_id, ' + \
                      'cookies, token, expires_time, create_time, update_time) ' + \
                      'VALUES (%s, %s, %s, %s, %s, %s)'
                expires_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()+86400))
            result = cursor.execute(sql, (id, cookies, token, expires_time, create_at, update_at))
            print(result)
        db.commit()
        db.close()
        return result

    def get_track(self, distance):
        """
                模拟轨迹 假装是人在操作
                :param distance:
                :return:
                """
        # 初速度
        v = 0
        # 单位时间为0.2s来统计轨迹，轨迹即0.2内的位移
        t = 0.2
        # 位移/轨迹列表，列表内的一个元素代表0.2s的位移
        tracks = []
        # 当前的位移
        current = 0
        # 到达mid值开始减速
        mid = distance * 7 / 8

        # a = random.randint(1,3)
        while current < distance:
            if current < mid:
                # 加速度越小，单位时间的位移越小,模拟的轨迹就越多越详细
                a = random.randint(2, 4)  # 加速运动
            else:
                a = -random.randint(3, 5)  # 减速运动

            # 初速度
            v0 = v
            # 0.2秒时间内的位移
            s = v0 * t + 5 * a * (t ** 2)
            # 当前的位置
            current += s
            # 添加到轨迹列表
            tracks.append(round(s))

            # 速度已经达到v,该速度作为下次的初速度
            v = v0 + a * t

        # 反着滑动到大概准确位置
        # for i in range(4):
        #     tracks.append(-random.randint(2, 3))
        # for i in range(4):
        #     tracks.append(-random.randint(1, 3))
        return tracks

    def login_main(self):
        try:
            #         ssl._create_default_https_context = ssl._create_unverified_context
            driver = self.driver
            driver.get(self.url)

            driver.implicitly_wait(10)
            driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))

            driver.find_element_by_xpath("//*[@id='fm-login-id']").send_keys(self.account)
            driver.find_element_by_xpath("//*[@id='fm-login-password']").send_keys(self.password)

            # 随机等待时间，以免被反爬虫
            time.sleep(random.uniform(10, 15))

            driver.switch_to.frame(driver.find_element_by_id("baxia-dialog-content"))

            # 找到登录窗口滑动背景验证的方块
            slider_square_bg = driver.find_element_by_xpath("//*[@id='nc_2__scale_text']")
            print(slider_square_bg.size)
            slider_square_bg_width = slider_square_bg.size['width']

            # 找到登录窗口滑动验证的方块
            slider_square = driver.find_element_by_xpath("//*[@id='nc_2_n1z']")
            # 得到登录窗口滑动验证方块的宽度
            slider_square_width = slider_square.size['width']
            print(slider_square.size)
            print(slider_square.location)
            location_x = slider_square.location['x']

            # 获取移动轨迹
            track_list = self.get_track(slider_square_bg_width - slider_square_width)   # 调用get_track()方法，传入真实距离参数，得出移动轨迹

            # 判断方块是否显示，是则模拟鼠标滑动，否则跳过
            if slider_square.is_displayed():
                # 找到滑块元素，点击鼠标左键，按住不放
                ActionChains(driver).click_and_hold(slider_square).perform()  # 点击鼠标左键，不松开 perform() ——执行链中的所有动作
                ActionChains(driver).move_by_offset(xoffset=location_x+(slider_square_bg_width - slider_square_width), yoffset=0).perform()  # 根据运动轨迹(x轴)，进行拖动

                # # 拖动元素
                # for track in track_list:
                #     print(track)
                #     ActionChains(driver).move_by_offset(xoffset=track, yoffset=0).perform()  # 根据运动轨迹(x轴)，进行拖动
                #     time.sleep(0.001)

                time.sleep(0.5)
                # print("验证滑块结束")
                ActionChains(driver).release(on_element=slider_square).perform()  # 释放鼠标

            # 切换到主html(最外层html)
            driver.switch_to.default_content()
            print(driver.find_element_by_xpath("//button[@class='fm-button fm-submit password-login']").text())

            cookies_all = json.dumps(self.driver.get_cookies())

            pass
        except Exception as e:
            print('str(Exception):\t', str(Exception))
            print('str(e):\t\t', str(e))
            print('repr(e):\t', repr(e))
            # Get information about the exception that is currently being handled
            self.after_quit()
            return False


if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    attempts = 0
    success = False
    login = Login()
    res = login.login_main()
    print(res)
