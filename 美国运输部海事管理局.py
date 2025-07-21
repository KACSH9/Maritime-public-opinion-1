import requests
from lxml import etree
from datetime import datetime
import re
import time as time_module


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


headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.mofa.go.jp/index.html",
    "Connection": "keep-alive",
    "Accept-Encoding": "gzip, deflate, br",
    "Cookie": "oFs68KIaLjNm_KkD6ZyKImmmB9durAka2sbPGJRldrs-1752996164-1.0.1.1-mUfo8n4si89ekDI1yWfA8pBJSBF8XUNvyAkLP9aouB2aoqJFu017mRTA1TgkwEp33JJ8OKgHrwCb3wapCFnVasmfTwCT1DKFgK5vhGHJwNg",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
}


# 爬取新闻
url = "https://www.maritime.dot.gov/newsroom"
resp = requests.get(url, headers=headers)
resp.encoding = 'utf_8'
result = resp.text

html = etree.HTML(result)
items = html.xpath('//div[@class="news-item views-row"]')

for item in items:
    # 日期
    date = item.xpath('.//div[@class="views-field views-field-field-effective-date"]//div[@class="field-content"]/text()')
    # 标题
    title = item.xpath('.//div[@class="views-field views-field-title"]//a/text()')
    # 链接
    link = item.xpath('.//div[@class="views-field views-field-title"]//a/@href')

    # 数据清洗
    date_str = date[0].strip() if date else ""
    title_str = title[0].strip() if title else ""
    link_str = "https://www.maritime.dot.gov" + link[0].strip() if link else ""

    # 日期格式转换
    try:
        formatted_date = datetime.strptime(date_str, "%B %d, %Y").strftime("%Y-%m-%d")
    except Exception:
        formatted_date = date_str

    resp2 = requests.get(link_str, headers=headers)
    resp2.encoding = 'utf_8'
    result2 = resp2.text
    html2 = etree.HTML(result2)
    items2 = html2.xpath('//div[@class="mb-4 clearfix"]')
    for item2 in items2:
        news_list = item2.xpath('.//p/text()')
        news = ''.join([t.strip() for t in news_list if t.strip()])

    all_news.append((formatted_date, title_str, news, link_str))



# 筛选当日新闻
today = datetime.now().strftime('%Y-%m-%d')   # 获取当前日期
today_news = []
for formatted_date, title_str, news, link_str in all_news:
    if formatted_date == today:
        today_news.append((formatted_date, title_str, news, link_str))



for formatted_date, title_str, news, link_str in today_news:
    translation_title = get_news_title(title_str)
    summary = get_news_summary(news)
    print(f"时间：{formatted_date}")
    print(f"题目：{translation_title}")
    print(f"摘要：{summary}")
    print(f"链接：{link_str}")
    print()  # 空行分隔
    time_module.sleep(0.5)  # 避免API限制

