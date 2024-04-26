import ctypes
import os
import random
import time
import tkinter as tk
import webbrowser
from threading import Thread

import keyboard
import psutil
import pystray
from PIL import Image, ImageTk
from pystray import MenuItem

import config
from typing import List


class Utils:

    @classmethod
    def set_img(cls, path: str):
        path = os.path.abspath(path)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 0)

    @classmethod
    def get_key(cls, elem: str) -> int:
        return int(elem[4:].removesuffix(f'.{config.IMGS_FORMAT}'))

    @classmethod
    def click(cls, window: 'Window'):
        def inner(_):
            if window.mouse_leave:
                return
            webbrowser.open(WALLPAPERS_URL)

        return inner

    @classmethod
    def enter(cls, window: 'Window'):
        def inner(_):
            nonlocal window
            window.mouse_leave = False
            window.url_label['fg'] = config.LABEL_ENTER_COLOR

        return inner

    @classmethod
    def leave(cls, window: 'Window'):
        def inner(_):
            nonlocal window
            window.mouse_leave = True
            window.url_label['fg'] = config.LABEL_LEAVE_COLOR

        return inner

    @classmethod
    def system_sleep(cls):
        # os.system('shutdown.exe -h')
        print("睡眠")


class Window:

    def __init__(self, wallpaper: 'Wallpaper'):
        self.wintk = tk.Tk()
        self.wallpaper: Wallpaper = wallpaper
        self.mouse_leave: bool = True
        self.selected_img = tk.StringVar()
        self.is_wallpaper_locked = tk.BooleanVar()
        self.model = 0
        self.lock_text = ["锁定壁纸", "锁定视频"]
        self.set_model_text = ["视频模式", "壁纸模式"]
        self.preview = ["图片预览：","视频预览："]

    def set_window(self):
        self.wintk.title(config.TITLE)
        self.wintk.geometry(config.GEOMETRY)
        self.wintk.protocol('WM_DELETE_WINDOW', self.wintk.withdraw)
        self.set_widgets()

    def set_widgets(self):
        tk.Label(self.wintk, text='选择:').place(x=0, y=50)
        tk.Label(self.wintk, text=self.preview[self.model]).place(x=10, y=80)
        self.preview_label = tk.Label(self.wintk, image=self.wallpaper.wallpapers[0])  # 图片预览
        self.preview_label.place(x=10, y=100)
        self.url_label = tk.Text(self.wintk, width=35, height=1, relief='flat', bg='gray94', fg='navyblue', wrap='word',
                                 font=('consolas', 9, 'underline'))
        self.url_label.insert(1.0, config.WALLPAPERS_URL)
        self.url_label.configure(state='disabled')
        self.url_label.bind('<ButtonRelease-2>', Utils.click(self))
        self.url_label.bind('<Enter>', Utils.enter(self))
        self.url_label.bind('<Leave>', Utils.leave(self))
        self.url_label.place(x=10, y=200)
        self.cpu_label = tk.Label(self.wintk, text='CPU: ', font=('consolas', 12))
        self.cpu_label.place(x=10, y=220)
        self.mem_label = tk.Label(self.wintk, text='Mem: ', font=('consolas', 12))
        self.mem_label.place(x=10, y=240)

        tk.Button(self.wintk, text='退出', command=lambda: os._exit(0), background='red', foreground='white').place(x=0,y=0)
        tk.Button(self.wintk, text='切换', command=self.change_whether_use_defalut).place(x=50, y=0)
        tk.Button(self.wintk, text=' 强制休眠 ', command=Utils.system_sleep).place(x=100, y=0)
        tk.Button(self.wintk, text='+', command=self.add, width=3).place(x=110, y=50)
        tk.Button(self.wintk, text='-', command=self.minus, width=3).place(x=40, y=50)
        tk.Button(self.wintk, text='选定', command=self.select_img).place(x=150, y=50)
        tk.Button(self.wintk, text=self.set_model_text[self.model], command=lambda: self.set_model()).place(x=190, y=0)

        self.entry = tk.Entry(self.wintk, width=3, textvariable=self.selected_img)
        self.entry.place(x=80, y=50)
        self.selected_img.set('0')

        tk.Checkbutton(self.wintk, text=self.lock_text[self.model], variable=self.is_wallpaper_locked).place(x=195, y=50)

    def change_whether_use_defalut(self):
        if self.wallpaper.use_default_img:
            Utils.set_img(self.wallpaper.wallpapers_path[self.wallpaper.displaying_wallpapers_num])
        else:
            Utils.set_img(self.wallpaper.defalut_path)
        self.wallpaper.use_default_img = not self.wallpaper.use_default_img

    def set_model(self):
        if self.model == 0:
            self.model = 1
        elif self.model == 1:
            self.model = 0
        self.set_window()

    def select_img(self):
        self.wallpaper.selected_num_temp = int(self.entry.get())

    def add(self):
        selected_img_num = int(self.selected_img.get())
        if selected_img_num == len(self.wallpaper.wallpapers_path) - 1:
            self.preview_label['image'] = self.wallpaper.wallpapers[0]
            return self.selected_img.set('0')
        self.selected_img.set(str(selected_img_num + 1))
        self.preview_label['image'] = self.wallpaper.wallpapers[selected_img_num + 1]

    def minus(self):
        selected_img_num = int(self.selected_img.get())
        if selected_img_num == 0:
            self.preview_label['image'] = self.wallpaper.wallpapers[len(self.wallpaper.wallpapers_path) - 1]
            return self.selected_img.set(str(len(self.wallpaper.wallpapers_path) - 1))
        self.selected_img.set(str(selected_img_num - 1))
        self.preview_label['image'] = self.wallpaper.wallpapers[selected_img_num - 1]

    def animate(self):
        pass


class Wallpaper:

    def __init__(self):
        self.window = Window(self)
        self.menu_content = (MenuItem('管理', self.window.wintk.deiconify), MenuItem('退出', lambda: self.quit_all()))
        self.taskbar_menu = pystray.Icon("none", Image.open("icon.png"), "manager", self.menu_content)

        self.wallpapers_path: List[str] = self.get_all_path()
        self.defalut_path: str = f'{config.IMGS_PATH}/{config.DEFUALT_NAME}.{config.IMGS_FORMAT}'
        self.wallpapers = self.open_all()

        self.displaying_wallpapers_num: None | int = None
        self.use_default_img: bool = False
        self.selected_num_temp: None | int = None

    def get_all_path(self) -> List[str]:
        wallpapers_path = os.listdir(config.IMGS_PATH)
        wallpapers_path.remove(f'{config.DEFUALT_NAME}.{config.IMGS_FORMAT}')
        wallpapers_path.sort(key=Utils.get_key)
        wallpapers_path = [f'{config.IMGS_PATH}/{path}' for path in wallpapers_path]
        return wallpapers_path

    def open_all(self) -> List[ImageTk.PhotoImage]:
        wallpapers = []
        for path in self.wallpapers_path:
            wallpaper = ImageTk.PhotoImage(Image.open(path).resize((192, 108)))
            wallpapers.append(wallpaper)
        return wallpapers

    def change_img(self):
        while True:
            next_img_num_temp = random.randint(0, len(self.wallpapers_path) - 1)
            self.selected_num_temp = None
            flag = False
            for _ in range(config.AUTO_CHANGE_TIME):
                if (not self.use_default_img) and (not self.window.is_wallpaper_locked.get()):
                    if self.selected_num_temp:
                        next_img_num_temp = self.selected_num_temp
                        self.selected_num_temp = None
                        break
                    time.sleep(1)
                else:
                    while self.use_default_img or self.window.is_wallpaper_locked.get():
                        if self.selected_num_temp is not None:
                            next_img_num_temp = self.selected_num_temp
                            self.selected_num_temp = None
                            flag = True
                            break
                        time.sleep(0.5)
                if flag: break
            next_img_num_temp %= len(self.wallpapers_path)
            self.displaying_wallpapers_num = next_img_num_temp
            Utils.set_img(self.wallpapers_path[self.displaying_wallpapers_num])

    def quit_all(self):
        self.taskbar_menu.stop()
        self.window.wintk.destroy()
        os._exit(0)

    def info_get(self):
        while True:
            cpu = psutil.cpu_percent(interval=3)
            mem = psutil.virtual_memory()
            self.window.cpu_label['text'] = f'CPU: {cpu}%'
            self.window.cpu_label['fg'] = 'black' if cpu < 80 else 'red'
            self.window.mem_label[
                'text'] = f'Mem: {round(mem.used / config.GB, 2)}GB/{round(mem[0] / config.GB, 2)}GB {round((round(mem.used / config.GB, 2) / round(mem[0] / config.GB, 2)) * 100, 2)}%'
            self.window.mem_label['fg'] = 'black' if round(mem.used / config.GB, 2) < 28 else 'red'

    def run(self):
        self.window.animate()
        self.window.set_window()
        self.displaying_wallpapers_num = random.randint(0, len(self.wallpapers_path) - 1)
        keyboard.add_hotkey('ctrl+alt+s', self.window.change_whether_use_defalut)
        keyboard.add_hotkey('ctrl+alt+a', Utils.system_sleep)
        Utils.set_img(self.wallpapers_path[self.displaying_wallpapers_num])

        Thread(target=self.change_img, daemon=True).start()
        Thread(target=self.taskbar_menu.run, daemon=True).start()
        Thread(target=self.info_get, daemon=True).start()
        self.window.wintk.protocol('WM_DELETE_WINDOW', self.window.wintk.withdraw)
        self.window.wintk.mainloop()


def main():
    wallpaper = Wallpaper()
    wallpaper.run()


if __name__ == '__main__':
    main()
