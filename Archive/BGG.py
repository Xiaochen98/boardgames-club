import requests
from bs4 import BeautifulSoup
import time

headers = {
    "User-Agent": "Mozilla/5.0"
}

def get_game_list():
    url = "https://boardgamegeek.com/trends/mostplayed"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    game_links = []
    for link in soup.select("a.bgg-link-primary"):
        href = link.get("href")
        if href and "/boardgame/" in href:
            game_links.append("https://boardgamegeek.com" + href)
    return game_links

def get_game_details(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    name = soup.select_one("h1 span.name").text.strip() if soup.select_one("h1 span.name") else "N/A"

    # 玩家人数
    player_info = soup.select_one('div.gameplay .gameplay-item-primary span')
    players = player_info.text.strip() if player_info else "N/A"

    # 游戏时间
    time_info = soup.select('div.gameplay .gameplay-item-primary span')
    playtime = time_info[1].text.strip() if len(time_info) > 1 else "N/A"

    # 简介
    desc_tag = soup.select_one("meta[name='description']")
    description = desc_tag['content'] if desc_tag else "无简介"

    return {
        "name": name,
        "players": players,
        "playtime": playtime,
        "description": description
    }

if __name__ == "__main__":
    games = []
    game_urls = get_game_list()
    print(f"共找到 {len(game_urls)} 款游戏，正在爬取详细信息...")

    for i, url in enumerate(game_urls[:10]):  # 为避免过多请求，这里只爬前10个
        print(f"[{i+1}] 正在抓取: {url}")
        try:
            details = get_game_details(url)
            games.append(details)
            time.sleep(1)  # 避免请求过快被封
        except Exception as e:
            print(f"爬取失败: {e}")
    
    for g in games:
        print("-" * 40)
        print(f"名称: {g['name']}")
        print(f"人数: {g['players']}")
        print(f"时间: {g['playtime']}")
        print(f"简介: {g['description']}")
