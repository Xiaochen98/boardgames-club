from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

# 配置 Selenium，无头浏览器
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=options)

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

# 获取游戏链接（去重）
game_elements = driver.find_elements(By.CSS_SELECTOR, "a[href^='/boardgame/']")
game_links = []
seen = set()

for g in game_elements:
    href = g.get_attribute('href')
    if href and "/boardgame/" in href and href not in seen:
        game_links.append(href)
        seen.add(href)

print(f"✅ 共找到 {len(game_links)} 款游戏，正在爬取详细信息...")

# 遍历每个游戏链接抓取详细信息
games = []

for i, link in enumerate(game_links[:26]):  # 可调整数量
    print(f"[{i+1}] 抓取: {link}")
    driver.get(link)
    time.sleep(3)

    try:
        name = driver.find_element(By.CSS_SELECTOR, "h1 span.name").text.strip()
    except:
        name = "N/A"

    try:
        gameplay_items = driver.find_elements(By.CSS_SELECTOR, "div.gameplay .gameplay-item-primary span")
        players = gameplay_items[0].text.strip() if len(gameplay_items) > 0 else "N/A"
        playtime = gameplay_items[1].text.strip() if len(gameplay_items) > 1 else "N/A"
    except:
        players = playtime = "N/A"

    try:
        description = driver.find_element(By.CSS_SELECTOR, "meta[name='description']").get_attribute("content")
    except:
        description = "无简介"

    games.append({
        "name": name,
        "players": players,
        "playtime": playtime,
        "description": description,
        "link": link
    })

# 关闭浏览器
driver.quit()

# 保存到 JSON 文件
with open("boardgames.json", "w", encoding="utf-8") as f:
    json.dump(games, f, ensure_ascii=False, indent=2)

print("✅ 爬取完成，数据已保存到 boardgames.json")

