"""
转载声明：
本代码基于 [SupJoN] 的作品 [wallpaper] 修改而来。
原始代码采用 GPL 版本 3.0 开源许可证。
原始代码来源：[github.com/SupJoN/wallpaper]
"""
# coding:utf-8
import json
import logging
import os
import subprocess
import time
import typing
import coloredlogs
import win32con
import win32gui
import win32print
from set_video_size import set_video_size

path: str = os.path.split(os.path.abspath(__file__))[0]


# 获取真实的分辨率
def get_real_size() -> tuple[int, int]:
    # 获取真实的分辨率
    hDC: int = win32gui.GetDC(0)
    # 横向分辨率
    w: int = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
    # 纵向分辨率
    h: int = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
    return w, h  # 1920*1080


# 获取视频的分辨率
def get_video_size(video: str) -> tuple[int, int]:
    # 使用ffprobe获取视频的分辨率
    process: subprocess.CompletedProcess = subprocess.run(
        f"\"{path}\\ffmpeg\\ffprobe.exe\" -v error -select_streams v:0 -show_entries stream=width,height -of json \"{video}\"",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # 错误处理
    if process.returncode != 0:
        logging.debug(f"ffprobe的终止代码为{process.returncode}")
        logging.error("请正确填写视频文件路径")
        exit()
    data = json.loads(process.stdout)
    logging.debug(f"视频文件信息为{data}")
    return data["streams"][0]["width"], data["streams"][0]["height"]


# 获取hide函数
def get_hide_func(process: subprocess.Popen) -> typing.Callable[[int, None], None]:
    def hide(hwnd: int, hwnds: None) -> None:
        hdef: int = win32gui.FindWindowEx(hwnd, 0, "SHELLDLL_DefView", None)  # 枚举窗口寻找特定类
        if hdef != 0:
            workerw: int = win32gui.FindWindowEx(0, hwnd, "WorkerW", None)  # 找到hdef后寻找WorkerW
            win32gui.ShowWindow(workerw, win32con.SW_HIDE)  # 隐藏WorkerW
            logging.debug("已对窗口进行隐藏操作")
            logging.info("窗口设置完成")
            logging.info("动态壁纸已设定完成")
            try:
                process.communicate()  # 阻塞主程序, 直到ffplay异常退出
                logging.error("ffplay异常终止")
                logging.debug(f"终止代码{process.returncode}")
            except KeyboardInterrupt:
                logging.info("程序退出")
                exit()

    return hide


# 使用ffplay播放视频
def ffplay(video) -> subprocess.Popen:
    vw, vh = get_video_size(video)
    ww, wh = get_real_size()
    if ww == vw and wh == vh:
        # 无边框, 一直持续播放, 取消控制台输出
        return subprocess.Popen(
            f"\"{path}\\ffmpeg\\ffplay.exe\" \"{video}\" -noborder -left 0 -top 0 -x {ww} -y {wh} -loop 0 -loglevel quiet -an",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        target_directory = f"{path}\\wallpapers\\video"
        target_filename = f"b_{os.path.basename(video)}"
        file_list = os.listdir(target_directory)
        if target_filename in file_list:
            vp = target_directory + "\\" + target_filename
            return subprocess.Popen(
                f"\"{path}\\ffmpeg\\ffplay.exe\" \"{vp}\" -noborder -left 0 -top 0 -x {ww} -y {wh} -loop 0 -loglevel quiet -an",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            vp = set_video_size(video, f"{path}\\wallpapers\\video", ww, wh)
            return subprocess.Popen(
                f"\"{path}\\ffmpeg\\ffplay.exe\" \"{vp}\" -noborder -left 0 -top 0 -x {ww} -y {wh} -loop 0 -loglevel quiet -an",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def display(video) -> None:
    logging.info("正在启动ffplay播放器播放视频...")
    process: subprocess.Popen = ffplay(video)
    while not win32gui.IsWindowVisible(win32gui.FindWindow("SDL_app", None)):
        time.sleep(0.1)
    logging.info("ffplay播放器启动成功")

    progman: int = win32gui.FindWindow("Progman", "Program Manager")  # 寻找Progman
    logging.debug(f"已寻找到Progman窗口, 窗口句柄为0x{progman:08X}")
    win32gui.SendMessageTimeout(progman, 0x52C, 0, 0, 0, 0)  # 发送0x52C消息
    logging.debug("已对Progman窗口发送0x52C消息")
    videowin: int = win32gui.FindWindow("SDL_app", None)  # 寻找ffplay播放窗口
    logging.debug(f"已寻找到ffplay播放器窗口, 窗口句柄为0x{videowin:08X}")
    win32gui.SetParent(videowin, progman)  # 设置子窗口
    logging.debug("已将ffplay播放器窗口设置为Progman窗口的子窗口")
    win32gui.EnumWindows(get_hide_func(process), None)  # 枚举窗口, 回调hide函数
