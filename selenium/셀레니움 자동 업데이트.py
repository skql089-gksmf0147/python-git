from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

print("셀레니움 현재버전",webdriver.__version__)

#크롬 드라이버 자동 업데이트
from webdriver_manager.chrome import ChromeDriverManager

print("셀레니움 업데이트후 버전",webdriver.__version__)

#브라우저 꺼짐 방지 및 전체화면
chrome_Options = Options()
chrome_Options.add_argument("--start-maximized")
chrome_Options.add_experimental_option("detach",True)

#불피룡한 에러 메세지 없애기
chrome_Options.add_experimental_option("excludeSwitches",["enable-logging"])

service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_Options)


url = 'https://naver.com'

driver.get(url)

#5초 쉰다
time.sleep(5)
#5초뒤에 창 꺼짐
driver.quit()
