import requests
from lxml import etree
import re
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


# 海上安全信息
def extract_other_emergency_info(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www6.kaiho.mlit.go.jp/index.html",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip, deflate, br",
        "Cookie": "oFs68KIaLjNm_KkD6ZyKImmmB9durAka2sbPGJRldrs-1752996164-1.0.1.1-mUfo8n4si89ekDI1yWfA8pBJSBF8XUNvyAkLP9aouB2aoqJFu017mRTA1TgkwEp33JJ8OKgHrwCb3wapCFnVasmfTwCT1DKFgK5vhGHJwNg",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
    }

    base_url = "https://www6.kaiho.mlit.go.jp"
    resp = requests.get(url, headers=headers)
    resp.encoding = 'utf-8'
    html = etree.HTML(resp.text)


    # 找到包含 alt="その他の緊急情報" 的项目
    items = html.xpath('//a[img[@alt="その他の緊急情報"]]')
    for img in items:
        img_id = img.xpath('./img/@id')
        if not img_id:
            continue
        popup_id = img_id[0].replace("popup", "popup-content")
        li_items = html.xpath(f'//div[@id="{popup_id}"]//li/a')
        for a in li_items:
            href = a.xpath('./@href')[0]
            title = a.xpath('string(.)').strip()
            date_match = re.search(r'(\d{8})', href)
            if date_match:
                raw_date = date_match.group(1)
                date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
            else:
                date = "未知"

            full_link = href if href.startswith("http") else base_url + href

            # 访问详情页
            try:
                detail_resp = requests.get(full_link, headers=headers, timeout=10)
                detail_resp.encoding = 'utf-8'
                detail_html = etree.HTML(detail_resp.text)

                def extract_td(th_text):
                    xpath_expr = f'//th[text()="{th_text}"]/following-sibling::td[1]'
                    td = detail_html.xpath(xpath_expr)
                    return td[0].xpath('string(.)').strip() if td else ""

                published_at = extract_td("発表日時")
                department = extract_td("発表部署")
                sea_area = extract_td("対象海域") or "無"
                period = extract_td("対象期間") or "無"
                remarks = extract_td("備考") or "無"

                # 内容：一段文字，无换行
                content_td = detail_html.xpath('//th[text()="内容"]/following-sibling::td[1]')
                if content_td:
                    content = ''.join(content_td[0].xpath('.//p//text()')).strip()
                else:
                    content = ""

                # 合并为一段 detail
                content = (
                    f"発表日時：{published_at} "
                    f"発表部署：{department} "
                    f"対象海域：{sea_area} "
                    f"対象期間：{period} "
                    f"備考：{remarks} "
                    f"内容：{content}"
                )

            except Exception as e:
                content = f"详情页获取失败: {e}"


            all_news.append((date, title, content, full_link))

extract_other_emergency_info('https://www6.kaiho.mlit.go.jp/01kanku/kinkyu.html')
extract_other_emergency_info('https://www6.kaiho.mlit.go.jp/02kanku/kinkyu.html')
extract_other_emergency_info('https://www6.kaiho.mlit.go.jp/03kanku/kinkyu.html')
extract_other_emergency_info('https://www6.kaiho.mlit.go.jp/04kanku/kinkyu.html')
extract_other_emergency_info('https://www6.kaiho.mlit.go.jp/05kanku/kinkyu.html')
extract_other_emergency_info('https://www6.kaiho.mlit.go.jp/06kanku/kinkyu.html')
extract_other_emergency_info('https://www6.kaiho.mlit.go.jp/07kanku/kinkyu.html')
extract_other_emergency_info('https://www6.kaiho.mlit.go.jp/08kanku/kinkyu.html')
extract_other_emergency_info('https://www6.kaiho.mlit.go.jp/09kanku/kinkyu.html')
extract_other_emergency_info('https://www6.kaiho.mlit.go.jp/10kanku/kinkyu.html')
extract_other_emergency_info('https://www6.kaiho.mlit.go.jp/11kanku/kinkyu.html')


# 新闻
def extract_kouhou_news(url):
    base_url = "https://www.kaiho.mlit.go.jp"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    }

    resp = requests.get(url, headers=headers)
    resp.encoding = 'utf-8'
    html = etree.HTML(resp.content)


    items = html.xpath('//li[div[@class="titleBasic"]]')
    for item in items[:20]:

        raw_date = item.xpath('.//div[@class="titleBasic"]/h3/text()')[0].strip()
        try:
            year, month, day = raw_date.split('/')
            year = str(2000 + int(year))  # “25”表示2025年
            date = f"{year}-{month}-{day}"
        except:
            date = "未知"

        title = item.xpath('.//div[@class="titleBasic"]/h3/a/text()')[0].strip()

        href = item.xpath('.//div[@class="titleBasic"]/h3/a/@href')[0]
        full_link = base_url + href
        # 抓取详情页
        try:
            detail_resp = requests.get(full_link, headers=headers, timeout=10)
            detail_resp.encoding = 'utf-8'
            detail_html = etree.HTML(detail_resp.content)
            # 提取正文内容：class="text_container__inner rich-text"
            content_node = detail_html.xpath('//div[@class="text_container__inner rich-text"]')
            if content_node:
                # 提取文本内容并合并为一段
                paragraphs = content_node[0].xpath('.//text()')
                content = ''.join([t.strip() for t in paragraphs if t.strip()])
            else:
                content = "未找到正文内容"
        except Exception as e:
            content = f"请求详情页失败: {e}"

        all_news.append((date, title, content, full_link))

extract_kouhou_news('https://www.kaiho.mlit.go.jp/info/kouhou/')

# 筛选当日新闻
today = datetime.now().strftime('%Y-%m-%d')   # 获取当前日期
today_news = []
for date, title, content, full_url in all_news:
    if date == today:
        today_news.append((date, title, content, full_url))

seen_titles = set()
unique_news = []
for date, title, content, full_url in today_news:
    # 彻底清理标题：去除所有空白字符，统一比较
    clean_title = re.sub(r'\s+', '', title) if title else ''
    if clean_title and clean_title not in seen_titles:
        seen_titles.add(clean_title)
        unique_news.append((date, title.strip(), content, full_url))  # 保存原始标题（只去前后空格）

for date, title, content, full_url in unique_news:
    translation_title = get_news_title(title)
    summary = get_news_summary(content)
    print(f"时间：{date}")
    print(f"题目：{translation_title}")
    print(f"摘要：{summary}")
    print(f"链接：{full_url}")
    print()  # 空行分隔
    time_module.sleep(0.5)  # 避免API限制







