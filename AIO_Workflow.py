import os
import time
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import jieba  # 导入jieba库
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
import csv

page = 1  # 初始化页数
city = 101280100  # 定义城市
position = 100901  # 定义职位

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
        plt.rcParams["font.sans-serif"] = ["SimHei"]
        plt.rcParams["axes.unicode_minus"] = False
        # 加载CSV文件（而不是Excel文件），并指定GB2312编码
        data = pd.read_csv('temporary.csv', encoding='GB2312')
        # 定义清洗和分割技能的函数
        def clean_split_skills(skills):
            skills_list = [skill.strip() for skill in skills.split('-') if skill.strip() != '']
            return skills_list
        # 对'技能要求'列应用函数，并展开DataFrame
        skills_series = data['技能要求'].apply(clean_split_skills).explode()
        # 统计每个技能出现的次数
        skills_counts = skills_series.value_counts()
        # 计算每个学历要求的百分比
        education_counts = data['学历要求'].value_counts(normalize=True) * 100
        # 计算每个经验要求的百分比
        experience_counts = data['经验要求'].value_counts(normalize=True) * 100
        # 创建技能要求词云对象
        wordcloud_skills = WordCloud(font_path='C:\Windows\Fonts\simfang.ttf', width=1600, height=800,
                                     background_color='white').generate_from_frequencies(skills_counts)
        # 添加自定义词汇
        custom_words = ["13薪", "14薪", "15薪"]
        for word in custom_words:
            jieba.add_word(word)
        # 分词处理薪资信息
        salary_words = ' '.join(jieba.cut(' '.join(data['薪资'])))  # 将薪资信息连接成字符串，然后进行分词
        # 创建薪资词云对象
        wordcloud_salary = WordCloud(font_path='C:\Windows\Fonts\simfang.ttf', width=1600, height=800,
                                     background_color='white').generate(salary_words)
        # 清洗和分割公司福利的函数
        def clean_split_benefits(benefits):
            # 确保benefits是字符串类型且非空
            if isinstance(benefits, str):
                benefits_list = [benefit.strip() for benefit in benefits.split('，') if benefit.strip() != '']
                return benefits_list
            else:
                return []  # 如果benefits不是字符串，返回空列表
        # 对'公司福利'列应用函数，并展开DataFrame
        benefits_series = data['公司福利'].apply(clean_split_benefits).explode()
        # 统计每个福利出现的次数
        benefits_counts = benefits_series.value_counts()
        # 创建公司福利词云对象
        wordcloud_benefits = WordCloud(font_path='C:\Windows\Fonts\simfang.ttf', width=1600, height=800,
                                       background_color='white').generate_from_frequencies(benefits_counts)
        # 创建图形
        fig, axs = plt.subplots(2, 2, figsize=(24, 16))
        # 学历要求饼图
        axs[0, 0].pie(education_counts, labels=education_counts.index, autopct=lambda pct: '{:.1f}%'.format(pct),
                      startangle=140,
                      textprops={'fontsize': 18})
        axs[0, 0].axis('equal')  # 确保饼图是圆的

        # 技能要求词云图
        axs[0, 1].imshow(wordcloud_skills, interpolation='bilinear')
        axs[0, 1].axis('off')  # 关闭坐标轴
        # 经验要求饼图
        axs[1, 0].pie(experience_counts, labels=experience_counts.index, autopct=lambda pct: '{:.1f}%'.format(pct),
                      startangle=140,
                      textprops={'fontsize': 14})
        axs[1, 0].axis('equal')  # 确保饼图是圆的
        # 薪资词云图
        axs[1, 1].imshow(wordcloud_salary, interpolation='bilinear')
        axs[1, 1].axis('off')  # 关闭坐标轴
        # # 福利词云图
        # axs[1, 2].imshow(wordcloud_benefits, interpolation='bilinear')
        # axs[1, 2].axis('off')  # 关闭坐标轴

        plt.tight_layout()  # 调整子图
        plt.savefig(f'学历经验技能薪资{page_title}.png')  # 保存子图为PNG文件
        print(f'已生成 学历经验技能薪资{page_title}.png')
        # plt.show()
        plt.figure(figsize=(16, 8))
        plt.imshow(wordcloud_benefits, interpolation='bilinear')
        plt.axis('off')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.savefig(f'福利{page_title}.png')
        print(f'已生成 福利{page_title}.png')
        # plt.show()
        if page_title:
            filename = f'{page_title}.csv'
            # 检查目标文件名是否存在，如果存在则添加一个后缀来避免冲突
            counter = 1
            while os.path.exists(filename):
                filename = f'{page_title}_{counter}.csv'
                counter += 1
            os.rename('temporary.csv', filename)
            print(f'已将数据保存到一个名叫 {filename} 的文件')

if __name__ == "__main__":
    main()

