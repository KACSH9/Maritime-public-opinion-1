import requests
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime
from lxml import etree
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

def get_csis_articles(section_name, referer_url, section_id="3060"):
    """
    获取 CSIS 某一板块第一页文章的标题、日期、链接。
    默认使用 section_id = 3060，可适配多个主题板块。
    """
    url = "https://www.csis.org/views/ajax"
    params = {
        "page": "0",
        "_wrapper_format": "drupal_ajax",
        "view_name": "search_default_index",
        "view_display_id": "block_1",
        "view_args": section_id,
        "view_path": referer_url.replace("https://www.csis.org", ""),
        "_drupal_ajax": "1"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Referer": referer_url,
        "Origin": "https://www.csis.org",
        "X-Requested-With": "XMLHttpRequest"
        # 如仍失败，可以再添加 'Cookie': '复制浏览器中的Cookie值'
    }

    try:
        resp = requests.get(url, headers=headers, params=params)
    except Exception as e:
        print(f"\n❌ [{section_name}] 网络请求失败：{e}")
        return

    if not resp.text.strip().startswith("["):
        print(f"\n❌ [{section_name}] 数据拉取失败：响应不是JSON，可能被封锁或参数无效")
        print(resp.text[:300])  # 打印前 300 字符调试
        return

    try:
        data = json.loads(resp.text)
    except json.JSONDecodeError:
        print(f"\n❌ [{section_name}] JSON解析失败")
        return

    html_block = ""
    for block in data:
        if isinstance(block, dict) and 'data' in block and isinstance(block['data'], str):
            html_block = block['data']
            break

    soup = BeautifulSoup(html_block, 'html.parser')
    articles = soup.select('article')

    #print(f"\n------ {section_name} ------")
    for article in articles:
        a_tag = article.select_one('h3.headline-md a, h3.headline-sm a')
        if not a_tag:
            continue
        title = a_tag.get_text(strip=True)

        href = a_tag.get('href')
        link = href if href.startswith("http") else "https://www.csis.org" + href

        resp2 = requests.get(link, headers=headers)
        resp2.encoding = 'utf-8'
        html2 = etree.HTML(resp2.text)
        news_list = html2.xpath('//div[@class="wysiwyg-wrapper text-high-contrast"]/p//text()')
        news_list = [text.strip() for text in news_list if text.strip()]
        news = '\n'.join(news_list)

        raw_text = article.get_text(separator=" ", strip=True)
        pub_date = "N/A"
        date_match = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}", raw_text)
        if date_match:
            try:
                parsed = datetime.strptime(date_match.group(0), "%B %d, %Y")
                pub_date = parsed.strftime("%Y-%m-%d")
            except:
                pass

        if pub_date != "N/A":
            all_news.append((pub_date, title, news, link))



get_csis_articles("海事问题与海洋", "https://www.csis.org/topics/maritime-issues-and-oceans")
get_csis_articles("气候变化", "https://www.csis.org/topics/climate-change")
get_csis_articles("国防和安全", "https://www.csis.org/topics/defense-and-security")
get_csis_articles("能源与可持续性", "https://www.csis.org/topics/energy-and-sustainability")
get_csis_articles("性别与国际安全", "https://www.csis.org/topics/gender-and-international-security")
get_csis_articles("地缘政治与国际安全", "https://www.csis.org/topics/geopolitics-and-international-security")
get_csis_articles("贸易和国际商务", "https://www.csis.org/topics/trade-and-international-business")
get_csis_articles("跨国威胁", "https://www.csis.org/topics/transnational-threats")



# 筛选当日新闻
today = datetime.now().strftime('%Y-%m-%d')   # 获取当前日期
today_news = []
for pub_date, title, news, link in all_news:
    if pub_date == today:
        today_news.append((pub_date, title, news, link))


for pub_date, title, news, link in today_news:
    translation_title = get_news_title(title)
    summary = get_news_summary(news)
    print(f"时间：{pub_date}")
    print(f"题目：{translation_title}")
    print(f"摘要：{summary}")
    print(f"链接：{link}")
    print()  # 空行分隔
    time_module.sleep(0.5)  # 避免API限制





