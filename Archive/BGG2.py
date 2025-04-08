from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

options = Options()
options.add_argument('--headless')  # 无头模式
options.add_argument('--disable-gpu')

driver = webdriver.Chrome(options=options)  # 如果 chromedriver 不在系统 PATH，请传入 executable_path="路径"

url = "https://boardgamegeek.com/trends/mostplayed"
driver.get(url)
time.sleep(5)  # 等待页面动态加载

game_elements = driver.find_elements(By.CSS_SELECTOR, "a.bgg-link-primary")
game_links = [g.get_attribute('href') for g in game_elements if "/boardgame/" in g.get_attribute('href')]

print(f"共找到 {len(game_links)} 款游戏，正在爬取详细信息...")

games = []

for i, link in enumerate(game_links[:10]):
    print(f"[{i+1}] {link}")
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
        "description": description
    })

driver.quit()

# 输出
for g in games:
    print("-" * 40)
    print(f"名称: {g['name']}")
    print(f"人数: {g['players']}")
    print(f"时间: {g['playtime']}")
    print(f"简介: {g['description']}")
