import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os

# 配置 Selenium，无头浏览器
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=options)

# 创建目录来保存图片
if not os.path.exists('images'):
    os.makedirs('images')

# 打开趋势页面
url = "https://boardgamegeek.com/trends/mostplayed"
driver.get(url)

# 等待页面上至少有一个游戏链接加载出来
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a[href^='/boardgame/']"))
    )
except:
    print("❌ 等待超时，页面未加载完成")
    driver.quit()
    exit()

# 获取游戏链接和标题（去重）
game_elements = driver.find_elements(By.CSS_SELECTOR, "a[href^='/boardgame/']")
game_links = []
game_titles = []
seen = set()

for g in game_elements:
    href = g.get_attribute('href')
    title = g.get_attribute('title')
    if href and "/boardgame/" in href and href not in seen:
        game_links.append(href)
        game_titles.append(title)
        seen.add(href)

print(f"✅ 共找到 {len(game_links)} 款游戏，正在爬取详细信息...")

# 遍历每个游戏链接抓取详细信息
games = []

for i, link in enumerate(game_links[:3]):  # 可调整数量
    print(f"[{i+1}] 抓取: {link}")
    driver.get(link)
    time.sleep(3)

    # 获取游戏名称
    try:
        name = driver.find_element(By.CSS_SELECTOR, "span[itemprop='name']").text.strip()
    except Exception as e:
        print(f"获取游戏名称失败: {e}")
        name = "未知名称"

    # 获取适合人数
    try:
        min_players_element = driver.find_element(By.CSS_SELECTOR, "span[ng-if*='minplayers']")
        max_players_element = driver.find_element(By.CSS_SELECTOR, "span[ng-if*='maxplayers']")
        min_players = min_players_element.text.strip() if min_players_element else "N/A"
        max_players = max_players_element.text.strip() if max_players_element else "N/A"
        players = f"{min_players}–{max_players}" if min_players != max_players else min_players
    except Exception as e:
        print(f"获取适合人数失败: {e}")
        players = "N/A"

    # 获取游玩时间
    try:
        min_time_element = driver.find_element(By.CSS_SELECTOR, "span[ng-if*='minplaytime']")
        max_time_element = driver.find_element(By.CSS_SELECTOR, "span[ng-if*='maxplaytime']")
        min_time = min_time_element.text.strip() if min_time_element else "N/A"
        max_time = max_time_element.text.strip() if max_time_element else "N/A"
        playtime = f"{min_time}–{max_time}" if min_time != max_time else min_time
    except Exception as e:
        print(f"获取游玩时间失败: {e}")
        playtime = "N/A"

    # 获取完整游戏简介
    try:
        # 这里更新了 CSS 选择器，直接抓取 <p> 标签中的文本内容
        description_element = driver.find_element(By.CSS_SELECTOR, "p[itemprop='description']")
        description = description_element.text.strip()
        if not description:
            description = "无简介"
    except Exception as e:
        print(f"获取完整游戏简介失败: {e}")
        description = "无简介"

    # 获取游戏封面图片URL
    try:
        image_url = driver.find_element(By.CSS_SELECTOR, "img[itemprop='image']").get_attribute('src')
        image_name = name.replace(" ", "_") + ".png"  # 生成图片文件名
        image_path = os.path.join('images', image_name)

        # 下载图片
        img_data = requests.get(image_url).content
        with open(image_path, 'wb') as handler:
            handler.write(img_data)
        print(f"✅ 下载图片: {image_name}")
    except Exception as e:
        print(f"获取图片失败: {e}")
        image_path = None

    games.append({
        "name": name,
        "players": players,
        "playtime": playtime,
        "description": description,
        "link": link,
        "image": image_path  # 保存图片路径
    })

# 关闭浏览器
driver.quit()

# 保存到 JSON 文件
with open("boardgames_with_images.json", "w", encoding="utf-8") as f:
    json.dump(games, f, ensure_ascii=False, indent=2)

print("✅ 爬取完成，数据已保存到 boardgames_with_images.json")
