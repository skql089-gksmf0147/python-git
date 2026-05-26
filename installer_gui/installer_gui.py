import tkinter as tk
from tkinter import messagebox
import subprocess

# 프로그램 목록 (이름: winget ID)
APPS = {
    "Bandizip":  "Bandizip.Bandizip",
    "KakaoTalk": "Kakao.KakaoTalk",
    "Chrome":    "Google.Chrome",
    "ocenaudio": "ocenaudio.ocenaudio",
    "Python 3.12": "Python.Python.3.12",
    "VS Code": "Microsoft.VisualStudioCode",
    # ↓ 여기에 추가로 설치하고 싶은 프로그램을 자유롭게 추가 가능
    # "PotPlayer": "Daum.PotPlayer",
    # "Discord": "Discord.Discord",
    # "7-Zip": "7zip.7zip"
}

def install_selected():
    selected = [app_id for name, app_id in APPS.items() if var_dict[name].get()]
    if not selected:
        messagebox.showwarning("경고", "설치할 프로그램을 선택하세요.")
        return

    for app in selected:
        try:
            subprocess.run(
                f"winget install --id {app} -e --accept-source-agreements --accept-package-agreements",
                shell=True,
                check=True
            )
        except subprocess.CalledProcessError:
            messagebox.showerror("오류", f"{app} 설치 중 오류가 발생했습니다.")

    messagebox.showinfo("완료", "선택한 프로그램의 설치가 완료되었습니다!")

# GUI 설정
root = tk.Tk()
root.title("프로그램 일괄 설치기")
root.geometry("350x400")
root.resizable(False, False)

title = tk.Label(root, text="🧩 원하는 프로그램을 선택하세요", font=("맑은 고딕", 12, "bold"))
title.pack(pady=10)

frame = tk.Frame(root)
frame.pack()

# 체크박스 변수 저장용 딕셔너리
var_dict = {}
for name in APPS:
    var_dict[name] = tk.BooleanVar(value=True)  # 기본값: 모두 선택됨
    tk.Checkbutton(frame, text=name, variable=var_dict[name], font=("맑은 고딕", 10)).pack(anchor="w", padx=30)

tk.Button(root, text="설치 시작", command=install_selected, bg="#4CAF50", fg="white",
          font=("맑은 고딕", 11, "bold"), width=15).pack(pady=20)

tk.Label(root, text="※ winget이 설치되어 있어야 합니다.", fg="gray", font=("맑은 고딕", 9)).pack()

root.mainloop()
