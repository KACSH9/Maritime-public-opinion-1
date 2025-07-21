import requests
from lxml import etree
from urllib.parse import urljoin
import time as time_module
from datetime import datetime


# AI题目翻译
all_news = []
DASHSCOPE_API_KEY = "sk-0700f1fb01214614af26a93ba633f395"  # API密钥
def get_news_title(news):
    if DASHSCOPE_API_KEY == "YOUR_API_KEY_HERE":
        return "请配置API密钥"
    headers = {
        'Authorization': f'Bearer {DASHSCOPE_API_KEY}',
        'Content-Type': 'application/json',
    }
    prompt = (
        f"请将下面题目翻译成中文：{news}"
    )
    data = {
        "model": "qwen-turbo",
        "input": {"messages": [{"role": "user", "content": prompt}]},
        "parameters": {"max_tokens": 200, "temperature": 0.3}
    }
    try:
        response = requests.post("https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                                 headers=headers, json=data, timeout=30)
        # 移除了所有调试信息输出
        if response.status_code == 200:
            result = response.json()
            if 'output' in result and 'text' in result['output']:
                return result['output']['text'].strip()
        return "翻译生成失败"
    except:
        return "翻译生成失败"

# AI总结摘要+翻译
DASHSCOPE_API_KEY = "sk-0700f1fb01214614af26a93ba633f395"  # API密钥
def get_news_summary(summ):
    if DASHSCOPE_API_KEY == "YOUR_API_KEY_HERE":
        return "请配置API密钥"
    headers = {
        'Authorization': f'Bearer {DASHSCOPE_API_KEY}',
        'Content-Type': 'application/json',
    }
    prompt = (
        f"请为以下外交新闻内容生成一个150字左右的摘要，包括背景信息、主要人物、地点、事件和意义，然后将该摘要翻译成中文，只给我中文版即可：{summ}"
    )
    data = {
        "model": "qwen-turbo",
        "input": {"messages": [{"role": "user", "content": prompt}]},
        "parameters": {"max_tokens": 200, "temperature": 0.3}
    }
    try:
        response = requests.post("https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                                 headers=headers, json=data, timeout=30)
        # 移除了所有调试信息输出
        if response.status_code == 200:
            result = response.json()
            if 'output' in result and 'text' in result['output']:
                return result['output']['text'].strip()
        return "摘要生成失败"
    except:
        return "摘要生成失败"


url = 'https://www.academy.kaiho.mlit.go.jp/index.html'
base = 'https://www.academy.kaiho.mlit.go.jp'

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36 Edg/138.0.0.0"
}

resp = requests.get(url, headers=headers)
resp.encoding = 'utf-8'

html = etree.HTML(resp.text)
items = html.xpath('//dl[@class="info_list"]/div')

#print("---------- 新闻和话题 ----------")
for item in items:
    date = item.xpath('.//time/@datetime')
    title = item.xpath('.//a/text()')
    link = item.xpath('.//a/@href')

    # 提取实际值
    date_str = date[0].strip() if date else ''
    title_str = title[0].strip() if title else ''
    full_link = urljoin(base, link[0].strip()) if link else ''

    # 获取详情页正文内容
    resp2 = requests.get(full_link, headers=headers)
    resp2.encoding = 'utf-8'
    html2 = etree.HTML(resp2.text)
    content_area = html2.xpath('//main[@id="mainContents"]')[0]  # 提取 main 内容区域

    paragraphs = content_area.xpath('.//p//text() | .//h3//text() | .//h6//text() | .//li//text() | .//div//text()')

    content_text = ''.join([t.strip() for t in paragraphs if t.strip()])

    all_news.append((date_str, title_str, content_text, full_link))

# 筛选当日新闻
today = datetime.now().strftime('%Y-%m-%d')   # 获取当前日期
today_news = []
for date_str, title_str, content_text, full_link in all_news:
    if date_str == today:
        today_news.append((date_str, title_str, content_text, full_link))

for date_str, title_str, content_text, full_link in today_news:
    translation_title = get_news_title(title_str)
    summary = get_news_summary(content_text)
    print(f"时间：{date_str}")
    print(f"题目：{translation_title}")
    print(f"摘要：{summary}")
    print(f"链接：{full_link}")
    print()  # 空行分隔
    time_module.sleep(0.5)  # 避免API限制
