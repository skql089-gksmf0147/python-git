import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

def play_video_and_fullscreen(driver, wait):
    """개선된 DPlayer 재생 및 전체화면 로직"""
    try:
        # 1. iframe이 완전히 로드될 때까지 대기
        time.sleep(3) 
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        target_iframe = None
        
        for f in iframes:
            src = f.get_attribute("src") or ""
            if "player" in src:
                target_iframe = f
                break
        
        if target_iframe:
            driver.switch_to.frame(target_iframe)
            print("✅ 플레이어 iframe 진입")
            
            # 2. 비디오 및 재생 버튼 요소 대기
            video = wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
            play_btn = driver.find_element(By.CSS_SELECTOR, ".dplayer-play-icon")
            
            # 3. 음소거 상태에서 재생 시작 (자동재생 차단 방지)
            print("▶️ 재생 시작 시도...")
            driver.execute_script("arguments[0].muted = true;", video)
            
            try:
                play_btn.click()
            except:
                driver.execute_script("arguments[0].click();", play_btn)
            
            driver.execute_script("if(arguments[0].paused) { arguments[0].play(); }", video)
            
            # 4. 재생 안정화 후 전체화면 전환
            time.sleep(1.5)
            print("⛶ 전체화면 전환 시도 중...")
            driver.execute_script("""
                if(window.dp) {
                    window.dp.play();
                    window.dp.fullScreen.request('browser');
                } else {
                    const fullBtn = document.querySelector('.dplayer-full-icon');
                    if(fullBtn) fullBtn.click();
                }
            """)
            
            # 5. 소리 켜기
            time.sleep(1)
            driver.execute_script("arguments[0].muted = false;", video)
            
            print("✅ 재생 및 전체화면 설정 완료")
            driver.switch_to.default_content() 
            
    except Exception as e:
        print(f"⚠️ 재생 실행 중 오류: {e}")
        driver.switch_to.default_content()

# --- 메인 실행 ---
url = sys.argv[1] if len(sys.argv) > 1 else ""

# 크롬 옵션 설정
chrome_options = Options()
#chrome_options.add_argument("--headless")  # 화면 안 띄우기
chrome_options.add_argument("--disable-gpu")
        
# ────────── 여기서부터 기존 옵션을 지우고 새로 교체해 주세요! ──────────
        
# 1. 사이트가 우리를 로봇으로 의심하지 않도록 실제 최신 크롬 브라우저 정보로 위장합니다.
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)
        
# 2. "나 자동화 프로그램(웹드라이버)이에요~" 하고 사이트에 고백하는 비밀 표식을 강제로 지워버립니다. (매우 중요!)
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
# 3. 브라우저 언어 설정을 한국어(ko-KR)로 고정하여 일반 한국 유저처럼 보이게 합니다.
chrome_options.add_argument("lang=ko_KR")
        
# 4. 사이트 접속 시 보안/인증서 관련 문제로 연결이 끊기는 것을 방지합니다.
chrome_options.add_argument("--ignore-certificate-errors")

# 5. 크롬 창이 화면에 꽉 차게 제일 큰 화면(전체화면)으로 뜨도록 만듭니다.
chrome_options.add_argument("--start-maximized")

# 6. 불필요한 알림 창들이 뜨는 걸 차단해서 깔끔하게 영상만 보이게 합니다.
chrome_options.add_argument("--disable-notifications")
   
# ──────────────────────────────────────────────────────────────────────────

# 드라이버 및 서비스 설정 (버전 자동 관리)
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 20)

driver.get(url)

# 1️⃣ 재생 및 전체화면 실행
play_video_and_fullscreen(driver, wait)

# 2️⃣ 자동 다음 회차 루프
while True:
    try:
        time.sleep(5)
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        player_found = False
        
        for f in iframes:
            if "player" in (f.get_attribute("src") or ""):
                player_found = True
                driver.switch_to.frame(f)
                
                # 영상 종료 여부 확인
                is_ended = driver.execute_script("return document.querySelector('video') ? document.querySelector('video').ended : false;")
                driver.switch_to.default_content()
                
                if is_ended:
                    print("🏁 영상 종료! 다음 회차를 확인합니다.")
                    try:
                        # 다음 회차 버튼 찾기
                        next_ep_xpath = "//div[contains(@class, 'active')]/preceding-sibling::div[1]//a"
                        next_ep_elements = driver.find_elements(By.XPATH, next_ep_xpath)
                        
                        if next_ep_elements:
                            next_ep = next_ep_elements[0]
                            print("➡️ 다음 회차가 발견되었습니다. 이동합니다.")
                            driver.execute_script("arguments[0].click();", next_ep)
                            time.sleep(5)
                            play_video_and_fullscreen(driver, wait)
                        else:
                            print("🛑 다음 회차가 없습니다. 브라우저를 종료합니다.")
                            driver.quit()
                            sys.exit()
                            
                    except Exception as e:
                        print(f"⚠️ 다음 회차 이동 오류: {e}")
                        driver.quit()
                        sys.exit()
                break
        
        if not player_found:
            pass # 플레이어를 찾을 때까지 대기
            
    except Exception as e:
        print(f"⚠️ 사이트 강제 종료 또는 오류: {e}")
        driver.quit()
        sys.exit()