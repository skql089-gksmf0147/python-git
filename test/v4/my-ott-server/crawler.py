import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://mvking.net"

CATEGORIES = {
    "movie": "/video/영화/한국/시간순",
    "drama": "/video/드라마/한국/시간순",
    "variety": "/video/예능/한국/시간순"
}

result = {}

for category, path in CATEGORIES.items():

    print("수집중:", category)

    r = requests.get(BASE_URL + path)
    soup = BeautifulSoup(r.text, "html.parser")

    items = []

    title_containers = soup.find_all("div", class_="video-title")

    for container in title_containers:

        a_tag = container.find("a")

        if a_tag:

            title = a_tag.get_text(strip=True)

            href = a_tag["href"]

            full_link = BASE_URL + href if href.startswith("/") else href

            # 이미지 찾기
            img_tag = container.find_previous("img", class_="vi")

            thumb = ""

            if img_tag and img_tag.get("src"):
                thumb = img_tag["src"]

            items.append({
                "title": title,
                "thumb": thumb,
                "video": full_link
            })

        if len(items) >= 20:
            break

    result[category] = items


with open("web/media.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("media.json 생성 완료")