#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import random

import ctypes
import win32api
import win32con
# import win32gui

from PIL import Image, ImageOps


# Set wallpaper in windows
def set_wallpaper(pic_path):
    ctypes.windll.user32.SystemParametersInfoW(20, 0, pic_path, 0)
    # key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, 'Control Panel\\Desktop', 0, win32con.KEY_SET_VALUE)
    # win32api.RegSetValueEx(key, 'WallpaperStyle', 0, win32con.REG_SZ, '22')
    # win32api.RegSetValueEx(key, 'TileWallpaper', 0, win32con.REG_SZ, '0')
    # win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER, pic_path, 1+2)


# Convert jpg to bmp
def image_to_bmp(pic_path):
    bmp = Image.open(pic_path)
    bmp_path = pic_path.replace('.jpg', '.bmp')
    bmp.save(bmp_path, 'BMP')


# Get image list in path
def image_list(path):
    # Check path
    if not os.path.exists(path):
        os.makedirs(path)
        return []
    # List
    img_list = []
    for files in os.listdir(path):
        if files.endswith(('.jpg', '.png')):
            img_list.append(os.path.join(path, files))
    return img_list


def image_random(img_list):
    return random.choice(img_list)


def full_size(windows, offsets):
    width = 0
    height = 0
    for (index, resolutions) in enumerate(windows):
        width = width+resolutions[0]
        height = max(height, resolutions[1]+offsets[index])
    return width, height  # 3200*1080


def image_mix(windows, offsets, img_list, save_path):
    entire_image = Image.new('RGB', full_size(windows, offsets))
    entire_width = 0
    for (index, resolutions) in enumerate(windows):
        cur_img_path = image_random(img_list)
        try:
            cur_img = Image.open(cur_img_path)
            # cur_img = Image.open(cur_img_path).convert('RGB')
        except IOError:
            print('Image open fail {}'.format(cur_img_path))
            return False
        new_img = ImageOps.fit(cur_img, resolutions)
        cur_img.close()
        print('Screen{} {}'.format(index, os.path.basename(cur_img_path)))
        # Paste to entire image
        entire_image.paste(new_img, (entire_width, offsets[index]))
        entire_width = entire_width+resolutions[0]
    # entire_image.show()
    entire_image.save(save_path)
    entire_image.close()
    return True


if __name__ == '__main__':
    # Configuration
    screens = ((1920, 1080), (1280, 1024))
    shifts = (0, 0)
    # image_dir = os.path.join(os.getcwd(), 'Images')
    image_dir = 'D:\project\壁纸管理\wallpapers'
    out_dir = os.path.join(os.getcwd(), 'Output.jpg')

    # Check param
    if len(screens) != len(shifts):
        print('Config wrong')
        exit()
    # Get all images
    images = image_list(image_dir)
    if not images:
        print('Empty images path')
        exit()
    # Mix a full images
    if not image_mix(screens, shifts, images, out_dir):
        print('Mix image fail')
        exit()
    # Set wallpaper
    reg_key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, "Control Panel\\Desktop", 0, win32con.KEY_SET_VALUE)
    win32api.RegSetValueEx(reg_key, "WallpaperStyle", 0, win32con.REG_SZ, "22")
    set_wallpaper(out_dir)
    print('Success')