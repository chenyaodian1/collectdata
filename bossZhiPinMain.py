# 这是一个示例 Python 脚本。
import sys
import traceback

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。
from playwright.sync_api import sync_playwright
from cloakbrowser import launch_persistent_context

import os
import time
from bs4 import BeautifulSoup
import requests
import pymysql
STATE_FILE = "boss_state.json"

captured_jobs = []
def load_headers_from_file(file_path):
    """
    读取文本文件并解析为字典
    支持格式: Key: Value
    """
    headers = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                # 去除首尾空白字符（包括换行符）
                line = line.strip()

                # 跳过空行
                if not line:
                    continue

                # 检查是否包含分隔符 ':'
                if ':' in line:
                    # 只分割第一个冒号，防止 value 中包含冒号（如 URL 或时间）被错误切割
                    key, value = line.split(':', 1)
                    headers[key.strip()] = value.strip().replace("\"","")
    except FileNotFoundError:
        print(f"错误：找不到文件 {file_path}")
    except Exception as e:
        print(f"读取文件时发生错误: {e}")

    return headers



def handle_request(request):
    pass
    # 过滤 XHR 和 Fetch 请求（即常见的 API 请求）
    #if request.resource_type in ["xhr", "fetch"]:
        #print(f"🔗 捕获到 API 请求: {request.method} {request.url}")

        # 获取请求头
        #if "joblist" in request.url:
        #  headerStr = ""
        #  headers = request.headers
        #  for key, value in headers.items():
        #      headerStr += "{key}:{value}\n".format(key=key, value=value)
          #print(type(headers))
          #print(f"📋 请求头: {headers}")
        #  with open("joblistreq.txt", "w", encoding="utf-8") as file:
        #      file.write(headerStr)
        #  post_data = request.post_data
        #  if post_data:
              #print(type(post_data))
              #print(f"📦 请求体(Payload): {post_data}")
         #     with open("joblistresponse.txt", "w", encoding="utf-8") as file1:
         #         file1.write(post_data)


        # 获取 POST 请求体 (Payload)


# 2. 监听响应（获取后台返回的数据）
def handle_response(response):
    # 拦截 Boss直聘 的职位列表 API
    if "wapi/zpgeek/search/joblist" in response.url:
        #print(f"[捕获接口] {response.status} -> {response.url}")

        # 确保请求成功且返回的是 JSON 格式
        if response.status == 200 and "application/json" in response.headers.get("content-type", ""):
            try:
                data = response.json()
                job_list = data.get("zpData", {}).get("jobList", [])
                for job in job_list:
                    job_info = {

                        "encrypt_job_id": job.get("encryptJobId"),
                        "job_name": job.get("jobName"),
                        "brand_name": job.get("brandName"),
                        "skills": ",".join(job.get("skills", [])),
                        "salary_desc": job.get("salaryDesc"),
                        "city_name": job.get("cityName"),
                        "boss_name": job.get("bossName"),
                        "boss_title": job.get("bossTitle"),
                        "encrypt_boss_id": job.get("encryptBossId"),
                        "boss_online": job.get("bossOnline"),
                        "job_degree": job.get("jobDegree"),
                        "brand_scale_name": job.get("brandScaleName"),
                        "encrypt_brand_id": job.get("encryptBrandId"),
                        "brand_industry": job.get("brandIndustry"),
                    }
                    captured_jobs.append(job_info)
                    print(f"  -> 获取到岗位: {job_info['job_name']} | {job_info['salary_desc']}")

            except Exception as e:
                print(f"解析 JSON 失败: {e}")
                traceback.print_exc()
    #if response.request.resource_type in ["xhr", "fetch"]:
        # 只处理成功的请求
    #    if response.status == 200:
    #        print(f"✅ 收到响应: {response.url}")
    #        try:
                # 尝试将返回内容解析为 JSON
    #            json_data = response.json()
    #            print(f"📊 返回的 JSON 数据: {json_data}")
    #        except Exception as e:
    #            print("该请求返回的不是 JSON 格式")


def save_boss_login():
    with sync_playwright() as p:
        # 1. 启动真实的 Chrome 浏览器，并隐藏自动化特征
        browser = p.chromium.launch(headless=False, channel="chrome", args=[
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
            '--disable-dev-shm-usage',
        ])

        # 2. 如果之前有保存过状态，先加载进去（防止 Cookie 还没过期时重复登录）
        if os.path.exists(STATE_FILE):
            context = browser.new_context(storage_state=STATE_FILE)
        else:
            context = browser.new_context(viewport={"width": 1920, "height": 1080},
            locale="zh-CN",
            timezone_id="Asia/Shanghai")

        page = context.new_page()



        # 3. 打开 Boss直聘 登录页
        page.goto("https://www.zhipin.com/web/user/?ka=header-login")

        print("⏳ 请在弹出的浏览器中手动扫码或账号密码登录...")
        print("✅ 登录成功并进入首页后，请回到终端按【回车键】保存状态。")

        # 4. 暂停脚本，等待你手动完成登录
        input()

        # 5. 将包含 Cookie 和 LocalStorage 的完整状态保存到 JSON 文件
        context.storage_state(path=STATE_FILE)
        print(f"💾 登录状态已成功保存至 {STATE_FILE}")

        browser.close()

if __name__ == "__main__1":
    timestamp_ms = int(time.time() * 1000)
    print(timestamp_ms)  # 例如: 1715678901234
    url = 'https://www.zhipin.com/wapi/zpgeek/search/joblist.json?_='+ str(timestamp_ms)
    header_file = 'joblistreq.txt'  # 你的文件名
    custom_headers = load_headers_from_file(header_file)
    print(custom_headers)
    post_data = "page=10&pageSize=15&city=101200100&query=java&expectInfo=&multiSubway=&multiBusinessDistrict=&position=&jobType=&salary=&experience=&degree=&industry=&scale=&stage=&scene=1&encryptExpectId="
    try:
        response = requests.post(url, headers=custom_headers, data=post_data, timeout=100)

        # 4. 处理响应
        print(f"状态码: {response.status_code}")
        # 尝试打印 JSON 响应，如果不是 JSON 则打印文本
        try:
            print(response.json())
        except ValueError:
            print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
if __name__ == "__main__2":
    # 读取之前保存的 HTML 文件
    with open("boss_job_page_step4.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    #job_list_div = soup.find('div', class_='job-list-container')
    job_cards = soup.find_all(class_='job-card-wrap')
    # 或者更精确地指定标签：soup.find_all('div', class_='job-card-wrap')

    print(f"✅ 共找到 {len(job_cards)} 个职位卡片")
    #print(job_list_div)
    for index, card in enumerate(job_cards):
         print(card)
         # 提取职位名称（假设 class 为 job-name）
         job_name = card.find(class_='job-name').get_text(strip=True) if card.find(class_='job-name') else "未知"

         # 提取薪资（假设 class 为 salary）
         salary = card.find(class_='job-salary').get_text(strip=True) if card.find(class_='job-salary') else "面议"

         # 提取公司名称（假设 class 为 company-name）
         company = card.find(class_='boss-name').get_text(strip=True) if card.find(class_='boss-name') else "未知"

         print(f"--- 职位 {index + 1} ---")
         print(f"名称: {job_name}")
         print(f"薪资: {salary}")
         print(f"公司: {company}")

def insertJobData():
    conn = pymysql.connect(host='192.168.154.128', user='cyd', password='Cyd!123456789', database='collect-data', charset='utf8mb4')
    cursor = conn.cursor()

    columns = [
        'encrypt_job_id', 'job_name', 'brand_name', 'salary_desc',
        'skills', 'city_name', 'boss_name', 'boss_title',
        'encrypt_boss_id', 'boss_online', 'job_degree',
        'brand_scale_name', 'encrypt_brand_id', 'brand_industry'
    ]

    # 使用列表推导式，将字典列表转换为元组列表
    tuple_list = [tuple(job.get(col) for col in columns) for job in captured_jobs]

    sql = """
            INSERT INTO boss_job_details 
            (encrypt_job_id, job_name, brand_name, salary_desc, skills, city_name, boss_name, boss_title, encrypt_boss_id, boss_online, job_degree, brand_scale_name, encrypt_brand_id, brand_industry) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                job_name = VALUES(job_name),
                brand_name = VALUES(brand_name),
                salary_desc = VALUES(salary_desc),
                skills = VALUES(skills),
                city_name = VALUES(city_name),
                boss_name = VALUES(boss_name),
                boss_title = VALUES(boss_title),
                encrypt_boss_id = VALUES(encrypt_boss_id),
                boss_online = VALUES(boss_online),
                job_degree = VALUES(job_degree),
                brand_scale_name = VALUES(brand_scale_name),
                encrypt_brand_id = VALUES(encrypt_brand_id),
                brand_industry = VALUES(brand_industry)
        """
    batch_size = 1000  # 每批插入 1000 条
    try:
        for i in range(0, len(tuple_list), batch_size):
            batch = tuple_list[i:i + batch_size]
            cursor.executemany(sql, batch)

        # 所有批次执行完毕后，统一提交一次事务
        conn.commit()
        print(f"成功插入 {len(captured_jobs)} 条数据")
    except Exception as e:
        traceback.print_exc()
        conn.rollback()
        print("插入失败，已回滚：", e)
    finally:
        cursor.close()
        conn.close()



if __name__ == "__main__":
    PROFILE_DIR = "./boss_profile"
    context = launch_persistent_context(
        PROFILE_DIR,
        headless=False,
        humanize=True,
        args=["--fingerprint-webrtc-ip=auto"]
    )

    page = context.pages[0] if context.pages else context.new_page()

    # ✅ 关键修改：先访问干净的主页，而不是深层链接
    page.goto("https://www.zhipin.com/")

    # 等待主页加载完成
    page.wait_for_load_state("domcontentloaded")

    page.on("request", handle_request)
    page.on("response", handle_response)

    # 等待登录按钮出现并点击
    #page.wait_for_selector("a.header-login-btn", state="visible")
    #page.click("a.header-login-btn", force=True)
    print("✅ 已点击登录按钮，正在等待跳转...")

    # 等待页面跳转到登录页
    #page.wait_for_url("**/web/user/**", timeout=15000)

    # 截图确认当前页面
    #page.screenshot(path="login_page.png")
    print("✅ 已成功跳转到登录页，截图已保存。")

    #page.wait_for_load_state("networkidle")
    final_content_step1 = page.content()
    #print(final_content_step1)
    with open("boss_job_page_step1.html", "w", encoding="utf-8") as file:
        file.write(final_content_step1)

    page.wait_for_selector("span.switchover-city", state="visible")
    page.click("span.switchover-city")

    time.sleep(5)
    final_content_step2 = page.content()
    #print(final_content_step2)
    with open("boss_job_page_step2.html", "w", encoding="utf-8") as file:
        file.write(final_content_step2)

    time.sleep(5)
    #武汉
    page.wait_for_selector('a[ka="city-sites-101200100"]', state="visible")
    page.click('a[ka="city-sites-101200100"]')
    #广州
    #page.wait_for_selector('a[ka="city-sites-101280100"]', state="visible")
    #page.click('a[ka="city-sites-101280100"]')

    time.sleep(5)
    final_content_step3 = page.content()
    #print(final_content_step3)
    with open("boss_job_page_step3.html", "w", encoding="utf-8") as file:
        file.write(final_content_step3)

    time.sleep(5)
    page.fill('input.ipt-search', '机器人')
    page.click('button[ka="search_box_index"]')

    time.sleep(5)

    # 1. 获取当前网页的完整总高度（画卷的长度）
    last_height = page.evaluate("document.body.scrollHeight")


    while True:
        # 2. 每次向下滚动“一屏”的距离（窗户的高度）
        # 这样既不会滚动得太慢，也不会直接跳到底部导致中间的图片/数据不加载
        page.mouse.wheel(0, 10000)

        # 等待新数据加载
        time.sleep(2)

        # 3. 再次获取网页的完整总高度
        new_height = page.evaluate("document.body.scrollHeight")

        # 4. 判断逻辑：如果画卷的总长度没有变长，说明已经到底了，且没有新数据了
        if new_height == last_height:
            break

        # 更新高度，继续下一次循环
        last_height = new_height


    print("✅ 已滚动至页面最底部")

    time.sleep(20)

    insertJobData()
    #final_content_step4 = page.content()
    #print(final_content_step4)
    #with open("boss_job_page_step4.html", "w", encoding="utf-8") as file:
    #    file.write(final_content_step4)



    input("按回车键退出...")
    context.close()