import json
import logging
import os
import subprocess
import sys
import threading
import time
from tkinter import messagebox
import customtkinter as ctk
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Selenium 라이브러리 탑재 (보안 우회용)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# =====================================================================
# 📺 [TV 전용 폰트 제어 설정]
# =====================================================================
class FontConfig:
    FONT_FAMILY = "NanumGothic"
    
    SIZE_MAIN_TITLE = 55  # 메인 화면 최상단 타이틀
    SIZE_PAGE_TITLE = 50  # 카테고리 페이지 상단 타이틀
    SIZE_LIST_ITEM  = 45  # 카테고리 목록 폰트
    SIZE_MAIN_MENU  = 40  # 메인 메뉴 버튼 폰트
    SIZE_BACK_BTN   = 35  # 뒤로가기 버튼 폰트

    @classmethod
    def get(cls, style_type):
        if style_type == "main_title":
            return (cls.FONT_FAMILY, cls.SIZE_MAIN_TITLE, "bold")
        elif style_type == "page_title":
            return (cls.FONT_FAMILY, cls.SIZE_PAGE_TITLE, "bold")
        elif style_type == "list_item":
            return (cls.FONT_FAMILY, cls.SIZE_LIST_ITEM, "bold")  
        elif style_type == "main_menu":
            return (cls.FONT_FAMILY, cls.SIZE_MAIN_MENU, "bold")
        elif style_type == "back_btn":
            return (cls.FONT_FAMILY, cls.SIZE_BACK_BTN, "bold")
        return (cls.FONT_FAMILY, 20)

# --- 전역 설정 및 로그 ---
log_path = os.path.join(
    os.path.dirname(sys.executable if getattr(sys, "frozen", False) else __file__),
    "app.log",
)
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class UltraMediaCenter(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("MOVIK 미디어 센터")
        
        # 📺 실행 시 윈도우 창을 전체 화면으로 고정
        self.after(0, lambda: self.wm_state('zoomed'))  

        self.current_buttons = []
        self.current_index = 0
        self.current_frame = None
        self.current_scroll = None
        self.frame_stack = []
        self.active_frame_name = "main"

        # 1. 데이터 로드
        self.data = self.load_data()

        # 각 카테고리 프레임 초기화
        self.frames = {}
        for name in ("main", "movie", "drama", "variety"):
            f = ctk.CTkFrame(self, fg_color="#1A1A1A")
            f.place(x=0, y=0, relwidth=1, relheight=1)
            self.frames[name] = f

        # 2. UI 구성
        self.setup_main_menu()
        self.setup_content_pages()

        # 키 바인딩
        self.bind("<Up>", self.on_key)
        self.bind("<Down>", self.on_key)
        self.bind("<Return>", self.on_key)
        self.bind("<space>", self.on_key)
        self.bind("<Escape>", lambda e: self.go_back())

        self.after(100, lambda: self.show_frame("main", self.main_buttons))

    # --- 데이터 처리 메서드 ---
    def get_data_path(self):
        if getattr(sys, "frozen", False):
            return os.path.join(os.path.dirname(sys.executable), "media.json")
        return os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "media.json"
        )

    def load_data(self):
        path = self.get_data_path()
        if not os.path.exists(path):
            return {"movie": [], "drama": [], "variety": []}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"데이터 로딩 실패: {e}")
            return {"movie": [], "drama": [], "variety": []}

    # 🔄 [핵심 수정한 부분] 무비킹 / 티비룸 스마트 자동 판단 크롤러
    def run_crawler_logic(self):
        # 내 깃허브 원격 주소 (만약 깃허브 저장소 이름이 다르면 이 부분 주소만 내가 쓰는 저장소명으로 고치면 됩니다!)
        CONFIG_URL = "https://raw.githubusercontent.com/skql089-gksmf0147/media-config/main/config.json"
        
        try:
            response = requests.get(CONFIG_URL, timeout=5)
            rules = response.json()
            
            base_url = rules.get("base_url", "https://mvking.vip/")
            target_class = rules.get("target_class", "video-card")       
            title_selector = rules.get("title_selector", ".video-title a")   
            wait_time = rules.get("wait_time", 5)             
            
            targets = {
                "movie": rules.get("path_movie", "/video/영화/한국/시간순"),
                "drama": rules.get("path_drama", "/video/드라마/한국/시간순"),
                "variety": rules.get("path_variety", "/video/예능/한국/시간순")
            }
            logging.info(f"🌐 깃허브 최신 규칙 로드 완료! 대상 주소: {base_url}")
        except Exception as e:
            logging.error(f"깃허브 규칙 로드 실패 (안전 기본값 적용): {e}")
            base_url = "https://mvking.vip/"
            target_class = "video-card"
            title_selector = ".video-title a"
            wait_time = 5
            targets = {"movie": "/video/영화/한국/시간순", "drama": "/video/드라마/한국/시간순", "variety": "/video/예능/한국/시간순"}

        # 사이트 형태 진단 (티비룸인가 무비킹인가?)
        is_tvroom = "tvroom" in base_url
        logging.info(f"현재 접속 모드 판정 -> 티비룸인가요?: {is_tvroom}")

        chrome_options = Options()
        chrome_options.add_argument("--headless")  
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("lang=ko_KR")
        chrome_options.add_argument("--ignore-certificate-errors")
        
        final_data = {"movie": [], "drama": [], "variety": []}
        driver = None
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            for key, path in targets.items():
                target_url = f"{base_url.rstrip('/')}{path}"
                logging.info(f"크롤링 수집 진행 중 [{key}]: {target_url}")
                driver.get(target_url)
                time.sleep(wait_time) 
                
                soup = BeautifulSoup(driver.page_source, "html.parser")
                category_items = []
                
                if is_tvroom:
                    # ─────────────── 1. 티비룸 수집 공식 ───────────────
                    video_items = soup.find_all("a", class_=target_class)
                    for item in video_items:
                        footer = item.find("div", class_="v-item-footer")
                        if footer and "data-title" in footer.attrs:
                            title = footer["data-title"]
                        else:
                            title_tag = item.find("div", class_="v-item-title")
                            title = title_tag.get_text(strip=True) if title_tag else "제목 없음"
                        
                        link = item.get('href', '')
                        if link and not link.startswith('http'):
                            link = f"{base_url.rstrip('/')}{link}"
                        category_items.append({"title": title, "url": link})
                else:
                    # ─────────────── 2. 무비킹 수집 공식 ───────────────
                    cards = soup.find_all('div', class_=target_class)
                    for card in cards:
                        a_tag = card.select_one(title_selector)
                        if a_tag:
                            title = a_tag.get_text(strip=True)
                            link = a_tag.get('href', '')
                            if link and not link.startswith('http'):
                                link = f"{base_url.rstrip('/')}{link}"
                            category_items.append({"title": title, "url": link})
             
                final_data[key] = category_items
                logging.info(f"[{key}] 카테고리 {len(category_items)}건 수집 완료.")
                time.sleep(2)

            with open(self.get_data_path(), 'w', encoding='utf-8') as f:
                json.dump(final_data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            logging.error(f"통합 크롤링 처리 실패: {e}")
            return False
        finally:
            if driver:
                driver.quit()

    def update_data_event(self):
        def task():
            if self.run_crawler_logic():
                self.after(0, lambda: self.finish_update("✅ 모든 데이터 우회 갱신 완료!"))
            else:
                self.after(0, lambda: messagebox.showerror("에러", "데이터 우회 갱신 실패\n로그(app.log)를 확인하세요."))
        threading.Thread(target=task, daemon=True).start()

    def finish_update(self, msg):
        self.data = self.load_data()
        self.setup_content_pages()
        if self.active_frame_name == "movie":
            self.current_buttons = self.movie_btns
        elif self.active_frame_name == "drama":
            self.current_buttons = self.drama_btns
        elif self.active_frame_name == "variety":
            self.current_buttons = self.variety_btns
        else:
            self.current_buttons = self.main_buttons
        self.current_index = 0
        self.highlight()
        messagebox.showinfo("알림", msg)

    # --- UI 구성 로직 ---
    def setup_main_menu(self):
        frame = self.frames["main"]
        ctk.CTkLabel(
            frame,
            text="원하시는 콘텐츠를 선택하세요",
            font=FontConfig.get("main_title"), 
            text_color="white",
        ).pack(pady=(60, 40))

        self.main_buttons = []
        menu_items = [
            ("🎬 한국 영화", lambda: self.show_frame("movie", self.movie_btns, self.movie_scr)),
            ("📺 TV 드라마", lambda: self.show_frame("drama", self.drama_btns, self.drama_scr)),
            ("🎉 인기 예능", lambda: self.show_frame("variety", self.variety_btns, self.variety_scr)),
            ("🔄 데이터 갱신", self.update_data_event),
        ]
        for text, cmd in menu_items:
            btn = ctk.CTkButton(
                frame,
                text=text,
                width=850,
                height=105,
                font=FontConfig.get("main_menu"),
                corner_radius=18,
                fg_color="#2B2B2B",
                text_color="#FFFFFF",
                hover_color="#FF5722",
                command=cmd,
            )
            btn.pack(pady=12)
            self.main_buttons.append(btn)

    def setup_content_pages(self):
        self.movie_btns, self.movie_scr = self.create_list_page("movie", "🎬 한국 영화", self.data.get("movie", []))
        self.drama_btns, self.drama_scr = self.create_list_page("drama", "📺 TV 드라마", self.data.get("drama", []))
        self.variety_btns, self.variety_scr = self.create_list_page("variety", "🎉 인기 예능", self.data.get("variety", []))

    def create_list_page(self, name, title, items):
        frame = self.frames[name]
        for widget in frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            frame, 
            text=title, 
            font=FontConfig.get("page_title"), 
            text_color="#FF5722"
        ).pack(pady=(30, 15))

        scroll = ctk.CTkScrollableFrame(
            frame, 
            width=1200, 
            height=580, 
            fg_color="transparent"
        )
        scroll.pack(expand=True, fill="both", padx=60, pady=5)

        buttons = []
        for item in items:
            btn = ctk.CTkButton(
                scroll,
                text=item.get('title', '제목 없음'),
                height=110,
                font=FontConfig.get("list_item"),
                anchor="center",
                fg_color="#2B2B2B",
                command=lambda u=item.get('url', ''): self.watch_video(u),
            )
            btn.pack(fill="x", pady=8, padx=50)
            buttons.append(btn)

        back = ctk.CTkButton(
            frame,
            text="⬅ 뒤로가기 (ESC)",
            width=600,
            height=85,
            font=FontConfig.get("back_btn"),
            fg_color="#444444",
            command=self.go_back,
        )
        back.pack(pady=20)
        buttons.append(back)
        return buttons, scroll

    # --- 제어 로직 ---
    def show_frame(self, name, buttons, scroll=None):
        if self.current_frame and self.active_frame_name != name:
            self.frame_stack.append((self.current_frame, self.current_buttons, self.current_scroll, self.active_frame_name))
        self.current_frame = self.frames[name]
        self.current_buttons = buttons
        self.current_scroll = scroll
        self.active_frame_name = name
        self.current_index = 0
        self.current_frame.tkraise()
        self.highlight()

    def go_back(self):
        if self.frame_stack:
            frame, buttons, scroll, name = self.frame_stack.pop()
            self.current_frame = frame
            self.current_buttons = buttons
            self.current_scroll = scroll
            self.active_frame_name = name
            self.current_index = 0
            self.current_frame.tkraise()
            self.highlight()

    def highlight(self):
        for i, btn in enumerate(self.current_buttons):
            if i == self.current_index:
                btn.configure(fg_color="#FF5722")
                if self.current_scroll and i < len(self.current_buttons) - 1:
                    self.current_scroll._parent_canvas.yview_moveto(i / len(self.current_buttons))
            else:
                if btn == self.current_buttons[-1]:
                    btn.configure(fg_color="#444444")
                else:
                    btn.configure(fg_color="#2B2B2B")

    def on_key(self, event):
        if not self.current_buttons:
            return
        if event.keysym == "Up":
            self.current_index = max(0, self.current_index - 1)
        elif event.keysym == "Down":
            self.current_index = min(len(self.current_buttons) - 1, self.current_index + 1)
        elif event.keysym in ("Return", "space"):
            self.current_buttons[self.current_index].invoke()
        self.highlight()

    def watch_video(self, url):
        if not url:
            return
        def run():
            try:
                if getattr(sys, 'frozen', False):
                    base = sys._MEIPASS
                    player = os.path.join(base, "player.exe")
                    if not os.path.exists(player):
                        player = os.path.join(os.path.dirname(sys.executable), "player.exe")
                else:
                    base = os.path.dirname(os.path.abspath(__file__))
                    player = os.path.join(base, "player.py")

                if player.endswith(".exe"):
                    cmd = [player, url, "1"]
                else:
                    cmd = [sys.executable, player, url, "1"]

                logging.info(f"동영상 재생 시도 경로: {player}")
                subprocess.Popen(cmd)
            except Exception as e:
                logging.error(f"재생 에러: {e}")

        threading.Thread(target=run, daemon=True).start()


if __name__ == "__main__":
    app = UltraMediaCenter()
    app.mainloop()