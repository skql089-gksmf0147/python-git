from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

#크롬 드라이버 자동 업데이트
from webdriver_manager.chrome import ChromeDriverManager

# 너무 빨리 입력되는것 방지하기 위한 시간 조절
import time 
#클립보드에 복사해넣었다가 다시 붙여넣기 하기 위한 명령
import pyautogui
import pyperclip

#브라우저 꺼짐 방지 및 전체화면
chrome_Options = Options()
chrome_Options.add_argument("--start-maximized")
chrome_Options.add_experimental_option("detach",True)

#불피룡한 에러 메세지 없애기
chrome_Options.add_experimental_option("excludeSwitches",["enable-logging"])

service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_Options)


driver.implicitly_wait(5)                 

url = 'https://accounts.google.com/v3/signin/identifier?continue=https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F&dsh=S-1005848562%3A1769045918709225&emr=1&followup=https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F&ifkv=AXbMIuATz8VB_EsgoWaXRMSXdBkBvrNT-UCfplYwxACE8XWosY716mhXyAmMhjeO8k5NCT_KGMESeg&osid=1&passive=1209600&service=mail&flowName=GlifWebSignIn&flowEntry=ServiceLogin'

driver.get(url)


# 아이디 입력창
id = driver.find_element(By.CSS_SELECTOR,"#id")
id.click()
#너무빨리 입력돼서 기계조작이라고 의심해서 먼저 클립보드에서 복사해서 넣는 방식입니다
pyperclip.copy("ybmm25@gmail.com")
pyautogui.hotkey("ctrl","v")
time.sleep(2)


# 비밀번호 입력창
pw = driver.find_element(By.CSS_SELECTOR,"#pw")
pw.click()
pyperclip.copy("ybmm25@gmail.com")
pyautogui.hotkey("ctrl","v")
time.sleep(2)


#로그인 버튼
login_btn = driver.find_element(By.CSS_SELECTOR,"#log\.login")
login_btn.click()



#driver.quit()
