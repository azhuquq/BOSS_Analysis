import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
import csv

page = 1  # 初始化页数
city = 101280600  # 定义城市
position = 230201  # 定义职位


def setChromeOptions():
    options = webdriver.ChromeOptions()  # 创建Chrome浏览器属性
    # options.add_argument('--headless') # 谷歌无头模式
    # options.add_argument('disable-infobars')# 隐藏"Chrome正在受到自动软件的控制"
    options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
    options.add_argument('lang=zh_HK.UTF-8')  # 设置中文
    options.add_argument('window-size=1000,800')  # 指定浏览器分辨率
    options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option("detach", True)
    # options.add_argument('blink-settings=imagesEnabled=false') # 无图模式
    # options.binary_location = r'/Applications/Chrome' # 手动指定使用的浏览器位置
    options.page_load_strategy = 'normal'

    # 更换头部
    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0"
    )
    options.add_argument('user-agent=%s' % user_agent)
    return options


def checkAndRedirect(browser):
    current_url = browser.current_url
    target_url = "https://www.zhipin.com/web/geek/job?query=&city=" + str(city) + "&position=" + str(
        position) + "&page=" + str(page)
    if current_url == "https://www.zhipin.com/":
        browser.get(target_url)


def simplify_url(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"


def getPageData(browser, csv_writer, first_call=False):
    global page_title  # 使用全局变量来存储页面标题
    while True:
        try:
            checkAndRedirect(browser)
            job_list = WebDriverWait(browser, 20).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'job-card-wrapper'))
            )
            if first_call:  # 首次调用时获取页面标题
                page_title = browser.title
            for job in job_list:
                checkAndRedirect(browser)
                # 链接
                job_link = job.find_element(By.CSS_SELECTOR, '.job-card-body > a').get_attribute('href')
                simplified_job_link = simplify_url(job_link)
                # 标题
                job_title = job.find_element(By.CLASS_NAME, 'job-name').text
                # 地区
                job_area = job.find_element(By.CLASS_NAME, 'job-area').text
                # 薪水
                salary = job.find_element(By.CLASS_NAME, 'salary').text
                # 经验要求
                exptag = job.find_element(By.CSS_SELECTOR, '.job-info .tag-list').text
                tags = exptag.split('\n')
                expreq = tags[-2]
                edureq = tags[-1]
                # exptag = exptag.replace('\n', '-')
                # 公司名
                company_name = job.find_element(By.CLASS_NAME, 'company-name').text
                # 公司背景
                companytag_elements = job.find_elements(By.CSS_SELECTOR, '.company-tag-list li')
                companytag = '-'.join([element.text for element in companytag_elements])
                # 技能要求
                footertag_elements = job.find_elements(By.CSS_SELECTOR, '.job-card-footer .tag-list li')
                footertag = '-'.join([element.text for element in footertag_elements])
                # 公司福利
                welfare = job.find_element(By.CLASS_NAME, 'info-desc').text
                print(
                    f'职位名称: {job_title}, 地区: {job_area}, 薪资: {salary}, 经验要求: {expreq}, 学历要求: {edureq}, 公司名称: {company_name}, 公司背景: {companytag}, 技能要求: {footertag}, 公司福利: {welfare}, 链接: {simplified_job_link}')
                # 将获取的数据写入 CSV 文件
                csv_writer.writerow([job_title, job_area, salary, expreq, edureq, company_name, companytag, footertag, welfare,
                                     simplified_job_link])
                pass
            break  # 成功执行后退出循环
        except StaleElementReferenceException:
            continue
        except TimeoutException:
            # 当找不到 job-card-wrapper 时循环调用 checkAndRedirect
            print("等待超时，未找到职位列表，尝试重新定位")
            checkAndRedirect(browser)


def clickNextPage(browser):
    global page
    try:
        next_page_button = browser.find_element(By.XPATH, "//a[i[@class='ui-icon-arrow-right']]")
        if "disabled" not in next_page_button.get_attribute("class"):
            actions = ActionChains(browser)
            actions.move_to_element(next_page_button).pause(1).click(next_page_button).perform()
            # next_page_button.click()  # 过时方案
            time.sleep(3)
            page += 1
            print(f"正在获取第 {page} 页的数据")
            return True
        else:
            print("已经是最后一页了")
            return False
    except NoSuchElementException:
        print("找不到下一页按钮")
        return False


def main():
    global page_title, page  # 声明为全局变量
    options = setChromeOptions()
    browser = webdriver.Chrome(options=options)
    browser.set_window_position(600, 200)
    try:
        url = "https://www.zhipin.com/web/geek/job?query=&city=" + str(city) + "&position=" + str(
            position) + "&page=" + str(page)
        browser.get(url)
        checkAndRedirect(browser)

        # 初始化文件名为空
        page_title = None

        with open('temporary.csv', mode='w', newline='', encoding='gb2312', errors='ignore') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(
                ['职位名称', '地区', '薪资', '经验要求', '学历要求', '公司名称', '公司背景', '技能要求', '公司福利', '链接'])
            getPageData(browser, csv_writer, first_call=True)
            time.sleep(1)
            while clickNextPage(browser):
                checkAndRedirect(browser)
                getPageData(browser, csv_writer)
                time.sleep(1)
                pass
    finally:
        browser.quit()
        # 检查是否已获取页面标题，并重命名文件
        if page_title:
            filename = f'数据_{page_title}.csv'
            # 检查目标文件名是否存在，如果存在则添加一个后缀来避免冲突
            counter = 1
            while os.path.exists(filename):
                filename = f'数据_{page_title}_{counter}.csv'
                counter += 1
            os.rename('temporary.csv', filename)
            print(f'已将数据保存到一个名叫 {filename} 的文件')


if __name__ == "__main__":
    main()
