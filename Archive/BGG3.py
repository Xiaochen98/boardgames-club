from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=options)

url = "https://boardgamegeek.com/trends/mostplayed"
driver.get(url)

# 等待最多10秒直到至少出现一个游戏链接
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a[href^='/boardgame/']"))
    )
except:
    print("等待超时，页面未加载完成")
    driver.quit()
    exit()

# 获取所有链接
game_elements = driver.find_elements(By.CSS_SELECTOR, "a[href^='/boardgame/']")
game_links = []
seen = set()

for g in game_elements:
    href = g.get_attribute('href')
    if href and "/boardgame/" in href and href not in seen:
        game_links.append(href)
        seen.add(href)

print(f"共找到 {len(game_links)} 款游戏，正在爬取详细信息...")

# 后续可按之前的流程获取详情页面内容
