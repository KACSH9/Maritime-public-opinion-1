import requests
from lxml import etree
from datetime import datetime
from urllib.parse import urljoin
import time as time_module

all_news = []

# AI题目翻译
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

def scrape_csis_articles(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    }
    base_url = 'https://www.csis.org'

    # 请求列表页
    resp = requests.get(url, headers=headers)
    resp.encoding = 'utf-8'
    html = etree.HTML(resp.text)
    articles = html.xpath('//div[@class="views-row"]')

    for article in articles:
        # 标题
        title = article.xpath('.//h3/a/span/text()')
        title = title[0].strip() if title else '无标题'

        # 链接（完整链接）
        link = article.xpath('.//h3/a/@href')
        full_link = urljoin(base_url, link[0].strip()) if link else '无链接'

        # 日期（格式化）
        date_raw = article.xpath('.//div[contains(@class, "contributors")]/p/span[@class="inline-block"]/text()')
        if date_raw:
            try:
                date_obj = datetime.strptime(date_raw[0].strip(), '— %B %d, %Y')
                date_str = date_obj.strftime('%Y-%m-%d')
            except:
                date_str = date_raw[0].strip()
        else:
            date_str = '无日期'

        # 请求详情页正文
        try:
            resp2 = requests.get(full_link, headers=headers)
            resp2.encoding = 'utf-8'
            html2 = etree.HTML(resp2.text)
            news_list = html2.xpath('//div[@class="wysiwyg-wrapper text-high-contrast"]/p//text()')
            news_list = [text.strip() for text in news_list if text.strip()]
            news = '\n'.join(news_list) if news_list else '[正文为空]'
        except:
            news = '[抓取失败]'

        all_news.append((date_str, title, news, full_link))




scrape_csis_articles("https://www.csis.org/topics/maritime-issues-and-oceans")
scrape_csis_articles("https://www.csis.org/topics/climate-change")
scrape_csis_articles("https://www.csis.org/topics/defense-and-security")
scrape_csis_articles("https://www.csis.org/topics/energy-and-sustainability")
scrape_csis_articles("https://www.csis.org/topics/gender-and-international-security")
scrape_csis_articles("https://www.csis.org/topics/geopolitics-and-international-security")
scrape_csis_articles("https://www.csis.org/topics/trade-and-international-business")
scrape_csis_articles("https://www.csis.org/topics/transnational-threats")


# 筛选当日新闻
today = datetime.now().strftime('%Y-%m-%d')   # 获取当前日期
today_news = []
for date_str, title, news, full_link in all_news:
    if date_str == today:
        today_news.append((date_str, title, news, full_link))


for date_str, title, news, full_link in today_news:
    translation_title = get_news_title(title)
    summary = get_news_summary(news)
    print(f"时间：{date_str}")
    print(f"题目：{translation_title}")
    print(f"摘要：{summary}")
    print(f"链接：{full_link}")
    print()  # 空行分隔
    time_module.sleep(0.5)  # 避免API限制
