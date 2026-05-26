import json
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 1. 브라우저 및 크롤링 기본 설정
chrome_options = Options()
chrome_options.add_argument("--headless")  # 브라우저 창을 띄우지 않고 실행
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

base_url = "https://mvking.me/"

# 카테고리 정의 (JSON 내부에 들어갈 키 이름과 URL 경로)
categories = {
    "영화": "/video/영화/한국/시간순",
    "드라마": "/video/드라마/한국/시간순",
    "예능": "/video/예능/한국/시간순",
}

# 모든 데이터를 담을 하나의 딕셔너리 생성
combined_data = {"영화": [], "드라마": [], "예능": []}

# 드라이버 실행
driver = webdriver.Chrome(options=chrome_options)


def crawl_category(category_name, path):
    target_url = f"{base_url}{path}"
    print(f"🔄 [{category_name}] 크롤링 중: {target_url}")

    try:
        driver.get(target_url)
        time.sleep(4)  # 로딩 및 보안 우회 대기

        soup = BeautifulSoup(driver.page_source, "html.parser")
        video_items = soup.find_all("a", class_="v-item")

        for item in video_items:
            # 제목 추출
            footer = item.find("div", class_="v-item-footer")
            if footer and "data-title" in footer.attrs:
                title = footer["data-title"]
            else:
                title_tag = item.find("div", class_="v-item-title")
                title = title_tag.get_text(strip=True) if title_tag else "제목 없음"

            # 링크 추출 및 절대경로 변환
            link = item.get("href", "")
            if link and not link.startswith("http"):
                link = f"{base_url}{link}"

            # 통합 딕셔너리의 해당 카테고리 리스트에 추가
            combined_data[category_name].append({"title": title, "link": link})

        print(f"✅ [{category_name}] 완료! ({len(combined_data[category_name])}건)")

    except Exception as e:
        print(f"❌ 에러 발생 [{category_name}]: {e}")


# 2. 반복문을 통해 각 카테고리 순차적 크롤링 진행
for cat_name, path in categories.items():
    crawl_category(cat_name, path)
    time.sleep(2)  # 디레이 타임

# 드라이버 종료
driver.quit()

# 3. 하나의 JSON 파일('media.json')로 통합 저장
output_file = "media.json"
with open(output_file, "w", encoding="utf-8") as json_file:
    json.dump(combined_data, json_file, ensure_ascii=False, indent=4)

print(f"\n🎉 모든 데이터가 '{output_file}' 파일 하나로 통합되어 저장되었습니다!")