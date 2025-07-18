import requests
from lxml import etree
from datetime import datetime
import time as time_module
from datetime import datetime

base_url = 'https://www.imo.org'

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
        return "摘要生成失败"
    except:
        return "摘要生成失败"

# AI总结摘要+翻译
all_news = []
DASHSCOPE_API_KEY = "sk-0700f1fb01214614af26a93ba633f395"  # API密钥
def get_news_summary(news):
    if DASHSCOPE_API_KEY == "YOUR_API_KEY_HERE":
        return "请配置API密钥"
    headers = {
        'Authorization': f'Bearer {DASHSCOPE_API_KEY}',
        'Content-Type': 'application/json',
    }
    prompt = (
        f"请为以下外交新闻内容生成一个150字左右的摘要，包括背景信息、主要人物、地点、事件和意义，然后将该摘要翻译成中文，只给我中文版即可：{news}"
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

def num1(section, url):
    #print(section)
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/138.0.0.0 Mobile Safari/537.36 Edg/138.0.0.0"
    }
    resp = requests.get(url, headers=headers)
    resp.encoding = 'utf-8'
    result = resp.text

    html = etree.HTML(result)
    items = html.xpath('//div[@class="col-md-6 mb-4 mb-md-6"]')

    for item in items:
        # 日期
        date = item.xpath('.//span[@class="badge badge-primary badge-sm"]/text()')
        date = date[0].strip() if date else ""
        date_obj = datetime.strptime(date, "%d %B %Y")
        formatted_date = date_obj.strftime("%Y-%m-%d") if date else ""
        # 题目
        title = item.xpath('.//h3[@class="card-title"]/a/text()')
        title = title[0].strip() if title else ""
        # 链接
        link = item.xpath('.//h3[@class="card-title"]/a/@href')
        link = link[0] if link else ""
        full_link = base_url + link if link.startswith("/") else link
        # 内容
        resp2 = requests.get(full_link, headers=headers)
        resp2.encoding = 'utf-8'
        result2 = resp2.text

        html2 = etree.HTML(result2)

        news = html2.xpath('//div[@class="content"]//p//text()')
        news_cleaned = [text.replace('\u200b', '').strip() for text in news if text.strip()]
        news_str = ' '.join(news_cleaned)

        all_news.append((formatted_date, title, news_str, full_link))

def num2(section, url):
    #print(section)
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/138.0.0.0 Mobile Safari/537.36 Edg/138.0.0.0"
    }
    resp = requests.get(url, headers=headers)
    resp.encoding = 'utf-8'
    result = resp.text

    html = etree.HTML(result)

    items = html.xpath('//div[contains(@class, "card shadow")]')

    for item in items:
        # 日期
        date = item.xpath('.//span[contains(@class, "badge")]/text()')
        date = date[0].strip() if date else ""
        formatted_date = ""
        date_obj = datetime.strptime(date, "%d %B %Y")
        formatted_date = date_obj.strftime("%Y-%m-%d")
        # 标题
        title = item.xpath('.//h3[@class="card-title"]/a/text()')
        title = title[0].strip() if title else ""
        # 链接
        link = item.xpath('.//h3[@class="card-title"]/a/@href')
        link = link[0] if link else ""
        full_link = base_url + link if link.startswith("/") else link
        # 新闻
        resp2 = requests.get(full_link, headers=headers)
        resp2.encoding = 'utf-8'
        html2 = etree.HTML(resp2.text)

        news = html2.xpath('//div[@class="card-text"]//p//text()') or \
               html2.xpath('//div[@class="content"]//p//text()')
        news_cleaned = [t.replace('\u200b', '').strip() for t in news if t.strip()]
        news_str = ' '.join(news_cleaned)

        all_news.append((formatted_date, title, news_str, full_link))

num1('新闻发布会', 'https://www.imo.org/en/mediacentre/pressbriefings/pages/default.aspx')
num2('新闻', 'https://www.imo.org/en/mediacentre/pages/whatsnew.aspx')

# 筛选当日新闻
today = datetime.now().strftime('%Y-%m-%d')   # 获取当前日期
today_news = []
for formatted_date, title, news_str, full_link in all_news:
    if formatted_date == today:
        today_news.append((formatted_date, title, news_str, full_link))


for formatted_date, title, news_str, full_link in today_news:
    translation_title = get_news_title(title)
    summary = get_news_summary(news_str)
    print(f"时间：{formatted_date}")
    print(f"题目：{translation_title}")
    print(f"摘要：{summary}")
    print(f"链接：{full_link}")
    print()  # 空行分隔
    time_module.sleep(0.5)  # 避免API限制

