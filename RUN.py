import subprocess

# 所有待运行的爬虫脚本列表
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

def run_scripts(script_list):
    for script in script_list:
        print(f"\n正在运行：{script}")
        try:
            # 使用 subprocess 调用每个脚本
            subprocess.run(["python", script], check=True)
        except subprocess.CalledProcessError as e:
            print(f"运行 {script} 时出错：{e}")
        except Exception as ex:
            print(f"运行 {script} 时发生未知错误：{ex}")

if __name__ == "__main__":
    run_scripts(scripts)
