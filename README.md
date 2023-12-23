# BOSS直聘数据爬虫及分析

## 项目介绍
本项目是一个使用Selenium的BOSS直聘网站数据爬虫，旨在自动化抓取职位信息。爬虫收集的数据将用于进一步的数据分析和可视化，使用Matplotlib库来展示结果。

## 功能特点
- **数据爬取**: 使用Selenium自动化工具模拟浏览器操作，有效地从BOSS直聘网站抓取职位相关信息。
- **数据分析**: 对收集到的数据进行清洗、处理和分析，提取有价值的信息。
- **数据可视化**: 利用Matplotlib将分析结果以图表的形式展示，直观呈现数据趋势和特征。

## 环境要求
- Python 3.x
- Selenium
- pandas
- Matplotlib
- jieba (如果进行中文文本分析)

## 安装指南

### 准备环境
确保您的计算机上安装了Python 3.x。您可以从[Python官网](https://www.python.org/downloads/)下载和安装。

### 安装Chrome浏览器
Selenium需要一个浏览器和相应的WebDriver来执行。如果您还没有安装Chrome浏览器，请从[Chrome官方网站](https://www.google.com/chrome/)下载并安装它。

### 安装Chrome WebDriver
1. 需要下载与您的Chrome浏览器版本相对应的Chrome WebDriver。您可以在[Chrome For Testing](https://googlechromelabs.github.io/chrome-for-testing/)查找适合您浏览器版本的WebDriver。
2. 下载后，将WebDriver文件放置在Python安装目录中，或者您可以在运行爬虫脚本时指定其路径。

### 安装项目依赖
1. 克隆仓库到本地：
   ```
   git clone https://github.com/azhuquq/BOSS_Analysis.git
   ```
2. 在命令行中导航到项目文件夹，并安装所需依赖：
   ```
   pip install -r requirements.txt
   ```

## 使用说明
1. 修改配置文件，包括设置爬虫参数和WebDriver的路径。
2. 运行爬虫脚本：
   ```
   python AIO_Workflow.py
   ```
3. 脚本运行后，查看生成的数据和可视化结果。

## 注意事项
- 确保你有合适的网络环境以及BOSS直聘网站的访问权限。
- 请遵守网站的爬虫协议和相关法律法规，合理使用爬虫。
