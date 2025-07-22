import subprocess
import concurrent.futures
from tqdm import tqdm
from colorama import init, Fore, Style
import csv
import re

init(autoreset=True)

scripts = [
    "中国外交部.py",
    "中国海事局.py",
    "世界贸易组织.py",
    "国际海事组织.py",
    "国际海底管理局.py",
    "联合国海洋法庭.py",
    "太平洋岛国论坛.py",
    "战略与国际研究中心.py",
    "日本外务省.py",
    "日本海上保安厅.py",
    "日本海上保安大学校.py",
    "美国国务院.py",
    "美国运输部海事管理局.py",
    "越南外交学院.py",
    "越南外交部.py"
]

results = []

def run_script_capture_output(script):
    try:
        completed = subprocess.run(
            ["python3", script],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8'
        )
        return (script, "成功", completed.stdout)
    except subprocess.CalledProcessError as e:
        return (script, "失败", e.stdout + "\n" + e.stderr)
    except Exception as ex:
        return (script, f"错误: {str(ex)}", "")

def extract_info(text):
    time_match = re.search(r'时间[:：]\s*(\d{4}-\d{2}-\d{2})', text)
    title_match = re.search(r'题目[:：]\s*(.+)', text)
    summary_match = re.search(r'摘要[:：]\s*(.+)', text, re.DOTALL)
    link_match = re.search(r'链接[:：]\s*(https?://[^\s]+)', text)

    time = time_match.group(1).strip() if time_match else '无'
    title = title_match.group(1).strip() if title_match else '无'
    summary = summary_match.group(1).strip() if summary_match else '无'
    link = link_match.group(1).strip() if link_match else '无'

    return time, title, summary, link

if __name__ == "__main__":
    max_workers = 8
    print(f"\n共需运行 {len(scripts)} 个脚本，最大并发数：{max_workers}\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_script = {
            executor.submit(run_script_capture_output, script): script
            for script in scripts
        }

        for future in tqdm(concurrent.futures.as_completed(future_to_script), total=len(scripts), desc="执行进度", ncols=80):
            script = future_to_script[future]
            try:
                script, status, output = future.result()
                results.append((script, status == "成功", output))
            except Exception as e:
                results.append((script, False, ""))

    with open('汇总结果.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['渠道', '时间', '题目', '摘要', '链接'])

        for script, success, output in results:
            channel = script.replace('.py', '')
            if success:
                time, title, summary, link = extract_info(output)
                writer.writerow([channel, time, title, summary, link])
            else:
                writer.writerow([channel, '无', '无', '无', '无'])

    print(f"\n{Fore.CYAN}✅ 所有任务执行完毕，结果已写入：汇总结果.csv{Style.RESET_ALL}")

    print("\n运行完成摘要：")
    for script, success, _ in results:
        status = "成功" if success else "失败"
        color = Fore.GREEN if success else Fore.RED
        print(f"{color}{script}: {status}{Style.RESET_ALL}")





