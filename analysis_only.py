import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import jieba  # 导入jieba库

# 设置字体，以便支持中文
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# 加载CSV文件（而不是Excel文件），并指定GB2312编码
file_path = '数据_「深圳汽车销售招聘」-2023年深圳汽车销售人才招聘信息 - BOSS直聘.csv'
data = pd.read_csv(file_path, encoding='GB2312')
cleaned_file_path = file_path.replace('.csv', '')  # 去除.xlsx

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
axs[0, 0].pie(education_counts, labels=education_counts.index, autopct=lambda pct: '{:.1f}%'.format(pct), startangle=140,
              textprops={'fontsize': 18})
axs[0, 0].axis('equal')  # 确保饼图是圆的

# 技能要求词云图
axs[0, 1].imshow(wordcloud_skills, interpolation='bilinear')
axs[0, 1].axis('off')  # 关闭坐标轴

# 经验要求饼图
axs[1, 0].pie(experience_counts, labels=experience_counts.index, autopct=lambda pct: '{:.1f}%'.format(pct), startangle=140,
              textprops={'fontsize': 14})
axs[1, 0].axis('equal')  # 确保饼图是圆的

# 薪资词云图
axs[1, 1].imshow(wordcloud_salary, interpolation='bilinear')
axs[1, 1].axis('off')  # 关闭坐标轴

# # 福利词云图
# axs[1, 2].imshow(wordcloud_benefits, interpolation='bilinear')
# axs[1, 2].axis('off')  # 关闭坐标轴

plt.tight_layout()  # 调整子图
plt.savefig('学历经验技能薪资'+cleaned_file_path+'.png')  # 保存子图为PNG文件
# plt.show()

plt.figure(figsize=(16, 8))
plt.imshow(wordcloud_benefits, interpolation='bilinear')
plt.axis('off')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.savefig('福利'+cleaned_file_path+'.png')
# plt.show()
