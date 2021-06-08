from selenium.webdriver import ActionChains  # 控制鼠标操作
from selenium.webdriver.chrome.options import Options  # 不展示浏览器窗口  测试不通过
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.chrome.service import Service
import time
from selenium import webdriver
from PIL import Image  # Python图像库
import numpy as np  # 矩阵计算的函数库
import cv2  # 图像处理和计算机视觉库
import os
import pymysql
import json
import sys
import random


class Login(object):
    def __init__(self):
        if len(sys.argv) < 3:
            self.account = '1778973****'
            self.password = '******'
        else:
            self.account = sys.argv[1]
            self.password = sys.argv[2]
        self.url = "https://www.zhihu.com/signin?next=%2Fsettings%2Faccount"
        # self.url = "https://detail.1688.com/offer/622477660714.html"
        self.browser = 'chrome'

        if self.browser == 'chrome':
            driver_path = "D:\Develop\GeckoDriver\chromedriver_win32\chromedriver.exe"
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

    def urllib_download(self,  imgurl, imgsavepath):
        """
        下载图片
        :param imgurl:      需要下载图片的url
        :param imgsavepath: 图片存放位置
        """
        from urllib.request import urlretrieve
        urlretrieve(imgurl, imgsavepath)

    """
    复杂图像处理：
        https://blog.csdn.net/sinat_36458870/article/details/78825571?utm_medium=distribute.pc_relevant.none-task-blog-2%7Edefault%7EBlogCommendFromMachineLearnPai2%7Edefault-1.control&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2%7Edefault%7EBlogCommendFromMachineLearnPai2%7Edefault-1.control
    """
    def get_position_senior(self, chunk, canves):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # cv2.imread()用于读取图片文件；图片路径，读取图片的形式（1表示彩色图片[默认]，0表示灰度图片，-1表示原来的格式）
        chunk = cv2.imread(chunk)  # 读取大图(灰化)
        canves = cv2.imread(canves)  # 读取拼图(灰化)

        chunk_gray = cv2.cvtColor(chunk, cv2.COLOR_BGR2GRAY)    # 灰化
        canves_gray = cv2.cvtColor(canves, cv2.COLOR_BGR2GRAY)  # 灰化

        chunk_blurred = cv2.GaussianBlur(chunk_gray, (9, 9), 0)     # 去噪
        canves_blurred = cv2.GaussianBlur(canves_gray, (9, 9), 0)   # 去噪

        chunk_gradX = cv2.Sobel(chunk_blurred, ddepth=cv2.CV_32F, dx=1, dy=0)   # 提取梯度
        chunk_gradY = cv2.Sobel(chunk_blurred, ddepth=cv2.CV_32F, dx=0, dy=1)
        canves_gradX = cv2.Sobel(canves_blurred, ddepth=cv2.CV_32F, dx=1, dy=0)
        canves_gradY = cv2.Sobel(canves_blurred, ddepth=cv2.CV_32F, dx=0, dy=1)

        chunk_gradient = cv2.subtract(chunk_gradX, chunk_gradY)
        chunk_gradient = cv2.convertScaleAbs(chunk_gradient)
        canves_gradient = cv2.subtract(canves_gradX, canves_gradY)
        canves_gradient = cv2.convertScaleAbs(canves_gradient)

        methods = [cv2.TM_SQDIFF_NORMED, cv2.TM_CCORR_NORMED, cv2.TM_CCOEFF_NORMED]
        methods = [cv2.TM_CCOEFF_NORMED]
        th, tw = canves_gradient.shape[:2]
        for md in methods:
            result = cv2.matchTemplate(chunk_gradient, canves_gradient, md)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            if md == cv2.TM_SQDIFF_NORMED:
                tl = min_loc
            else:
                tl = max_loc
            br = (tl[0] + tw, tl[1] + th)
            cv2.rectangle(chunk, tl, br, [0, 0, 0])
            # cv2.imshow("pipei" + np.str(md), chunk)
            cv2.imwrite(base_dir + "/image/"+"pipei" + np.str(md)+".jpg", chunk)  # 保存大图

            y, x = np.unravel_index(result.argmax(), result.shape)

        print(x)
        return x

    def get_position(self, chunk, canves):
        """
        判断缺口位置
        :param chunk:   缺口图片(验证码中的大图)
        :param canves:  验证码中的拼图
        :return:        位置 x, y
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # cv2.imread()用于读取图片文件；图片路径，读取图片的形式（1表示彩色图片[默认]，0表示灰度图片，-1表示原来的格式）
        chunk = cv2.imread(chunk, 0)  # 读取大图(灰化)
        canves = cv2.imread(canves, 0)  # 读取拼图(灰化)
        h, w = canves.shape[::1]

        # 二值化后的图片名称Ω
        slide_puzzle = base_dir + "/image/slide_puzzle.jpg"
        slide_bg = base_dir + "/image/slide_bg.jpg"
        # 将二值化后的图片进行保存
        # cv2.imwrite()用于保存图片文件；参数1：保存的图像名称，参数2：需要保存的图像
        cv2.imwrite(slide_bg, chunk)  # 保存大图
        cv2.imwrite(slide_puzzle, canves)  # 保存拼图
        # os.system('chmod 777 ' + base_dir + '/image/slide_puzzle.jpg')
        # os.system('chmod 777 ' + base_dir + '/image/slide_bg.jpg')
        chunk = cv2.imread(slide_bg)  # 使用cv2.imread()读出来的是BGR数据格式
        # cv2.cvtColor(p1, p2) 是颜色空间转换函数    参数1：需要转换的图片，参数2：转换成何种格式
        # cv2.COLOR_BGR2RGB:将BGR格式转换成RGB格式      cv2.COLOR_BGR2GRAY:将BGR格式转换成灰度图片
        chunk = cv2.cvtColor(chunk, cv2.COLOR_BGR2GRAY)

        chunk = abs(255 - chunk)
        cv2.imwrite(slide_bg, chunk)
        chunk = cv2.imread(slide_bg)  # 读取大图
        canves = cv2.imread(slide_puzzle)  # 读取拼图

        # 获取偏移量
        result = cv2.matchTemplate(chunk, canves, cv2.TM_CCOEFF_NORMED)

        # 得到最大和最小值得位置
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        top_left = min_loc  # 左上角的位置
        bottom_right = (top_left[0] + w, top_left[1] + h)  # 右下角的位置

        # 在原图上画矩形
        cv2.rectangle(chunk, top_left, bottom_right, (0, 0, 255), 2)

        # 显示原图和处理后的图像
        cv2.imshow("img_template", chunk)
        cv2.imshow("processed", canves)

        cv2.waitKey(0)

        y, x = np.unravel_index(result.argmax(), result.shape)
        return x

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

        distance += 10  # 先滑过一点，最后再反着滑动回来
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
            s = v0 * t + 0.5 * a * (t ** 2)
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
            # 设置最大等待时间
            driver.implicitly_wait(10)

            # 找到密码登录按钮 并点击
            driver.find_element_by_xpath("//*[@class='SignFlow-tabs']/*[2]").click()

            # 随机等待时间，以免被反爬虫
            time.sleep(random.uniform(1, 3))

            driver.find_element_by_xpath("//input[@name='username']").send_keys(self.account)
            driver.find_element_by_xpath("//input[@name='password']").send_keys(self.password)

            # 随机等待时间，以免被反爬虫
            time.sleep(random.uniform(1, 3))

            driver.find_element_by_xpath("//button[@type='submit']").click()

            # 随机等待时间，以免被反爬虫
            time.sleep(random.uniform(1, 3))

            bk_block = driver.find_element_by_xpath('//img[@class="yidun_bg-img"]')
            web_image_width = bk_block.size['width']
            bk_block_x = bk_block.location['x']

            slide_block = driver.find_element_by_xpath('//img[@class="yidun_jigsaw"]')  # 获取验证码中的拼图
            # print(bk_block.location)                  # 该图片对象在弹出的验证码框中的位置，返回字典的格式，例如：{'x': 36, 'y': 102}
            slide_block_x = slide_block.location['x']  # 获取该图片对象在验证码框中的位置(x轴)

            # 获取验证码中的大图url
            bk_block = driver.find_element_by_xpath('//img[@class="yidun_bg-img"]').get_attribute('src')
            # 获取验证码中的拼图url
            slide_block = driver.find_element_by_xpath('//img[@class="yidun_jigsaw"]').get_attribute('src')
            # 获取滑块
            slid_ing = driver.find_element_by_xpath('//div[@class="yidun_slider"]')

            base_dir = os.path.dirname(os.path.abspath(__file__))
            os.makedirs(base_dir + '/image/', exist_ok=True)
            self.urllib_download(bk_block, base_dir + '/image/bkBlock.png')
            # os.system('chmod 777 ' + base_dir + '/image/bkBlock.png')
            self.urllib_download(slide_block, base_dir + '/image/slideBlock.png')
            # os.system('chmod 777 ' + base_dir + '/image/slideBlock.png')

            # 随机等待时间，以免被反爬虫
            time.sleep(random.uniform(1, 3))

            img_bkblock = Image.open(base_dir + '/image/bkBlock.png')
            real_width = img_bkblock.size[0]
            width_scale = float(real_width) / float(web_image_width)

            position_x = self.get_position_senior(base_dir + '/image/bkBlock.png',
                                           base_dir + '/image/slideBlock.png')  # 获取到 大图 与 拼图 位移的距离 (实际滑动的距离就是x轴的距离)

            real_position = position_x / width_scale  # 将大图/比例，得到验证码框中大图与拼图实际的滑动距离

            real_position = real_position - (
                    slide_block_x - bk_block_x)  # (slide_block_x - bk_block_x):即拼图到大图的左边距，所以减去左边距后才得到真正的滑动距离

            track_list = self.get_track(real_position)  # 调用get_track()方法，传入真实距离参数，得出移动轨迹

            ActionChains(driver).click_and_hold(on_element=slid_ing).perform()  # 找到滑块元素，点击鼠标左键，按住不放
            time.sleep(0.02)
            # 拖动元素
            for track in track_list:
                ActionChains(driver).move_by_offset(xoffset=track, yoffset=0).perform()  # 根据运动轨迹(x轴)，进行拖动
                time.sleep(0.01)
            time.sleep(0.5)
            print("验证滑块结束")
            ActionChains(driver).release(on_element=slid_ing).perform()  # 释放鼠标
            error_message = driver.find_element_by_xpath('//div[@class="Notification-textSection Notification-textSection--withoutButton"]').text
            """
            滑块验证通过后，知乎会报请求参数异常，展示无法定位原因
            """
            if(error_message):
                print(error_message)
                return False
            else:
                cookies_all = json.dumps(self.driver.get_cookies())
                result = self.save_cookie(cookies_all)
                return True
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
