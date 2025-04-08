from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os
import time
import json
import re
import requests

def sanitize_filename(name):
    """替换非法字符以便用于文件名"""
    return re.sub(r'[\\/:*?"<>|]', '_', name)

# 初始化 Selenium 浏览器
options = Options()
options.add_argument("--headless")
service = Service()
driver = webdriver.Chrome(service=service, options=options)

# 创建图片保存目录
if not os.path.exists("images"):
    os.makedirs("images")

# 打开主页面
driver.get("https://boardgamegeek.com/browse/boardgame")
time.sleep(3)

# 找到所有游戏链接
game_elements = driver.find_elements(By.CSS_SELECTOR, "a.primary")
game_links = [elem.get_attribute("href") for elem in game_elements]

print(f"共找到 {len(game_links)} 款游戏，正在爬取详细信息...")

games_data = []

for idx, link in enumerate(game_links):
    print(f"[{idx+1}] 抓取: {link}")
    driver.get(link)
    time.sleep(3)

    try:
        name = driver.find_element(By.CSS_SELECTOR, "span[itemprop='name']").text.strip()
    except:
        name = "未知游戏"

    try:
        # 玩家人数
        players_element = driver.find_element(By.CSS_SELECTOR, "span.ng-isolate-scope")
        players = players_element.text.strip()
    except:
        players = "N/A"

    try:
        # 游戏时间
        playtime_element = driver.find_element(By.CSS_SELECTOR, "span[min][max].ng-isolate-scope")
        playtime = playtime_element.text.strip()
    except:
        playtime = "N/A"

    try:
        # 简介（HTML结构中为一个 ng-bind-html 的 <div> 里包了 <p>）
        description_div = driver.find_element(By.CSS_SELECTOR, "div[ng-bind-html]")
        description = description_div.text.strip()
        if not description:
            description = "无简介"
    except:
        description = "无简介"

    try:
        # 图片地址
        img_element = driver.find_element(By.CSS_SELECTOR, "img.img-responsive")
        img_url = img_element.get_attribute("src")
        sanitized_name = sanitize_filename(name)
        img_filename = f"{sanitized_name}.jpg"
        img_path = os.path.join("images", img_filename)

        # 下载图片
        response = requests.get(img_url)
        if response.status_code == 200:
            with open(img_path, "wb") as f:
                f.write(response.content)
        else:
            print(f"图片下载失败: {img_url}")
    except Exception as e:
        print(f"图片获取失败: {e}")
        img_url = None

    # 保存游戏信息
    game_info = {
        "name": name,
        "players": players,
        "playtime": playtime,
        "description": description,
        "link": link,
        "image": img_url
    }

    games_data.append(game_info)

# 保存为 JSON 文件
with open("boardgames.json", "w", encoding="utf-8") as f:
    json.dump(games_data, f, ensure_ascii=False, indent=2)

driver.quit()
print("数据抓取完成，信息已保存到 boardgames.json，图片已保存到 images 文件夹。")
