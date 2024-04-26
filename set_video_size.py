"""
版权声明：本文为博主原创文章，遵循
CC
4.0
BY - SA
版权协议，转载请附上原文出处链接和本声明。

原文链接：https: // blog.csdn.net / zhiweihongyan1 / article / details / 121887259
"""
import os
import uuid
from ffmpy import FFmpeg


# 调整视频大小
def set_video_size(video_path: str, output_dir: str, width: int, height: int, bit_rate=20000):
    """
    调整视频大小
    :param video_path: 视频地址
    :param output_dir: 输出目录
    :param width: 宽度
    :param height: 高度
    :param bit_rate: 码率
    :return:
    """
    ext = os.path.basename(video_path).strip().split('.')[-1]
    if ext not in ['mp4']:
        raise Exception('format error')
    filename_with_extension = os.path.basename(video_path)
    filename_without_extension = os.path.splitext(filename_with_extension)[0]
    _result_path = os.path.join(output_dir, '{}.{}'.format(f"b_{filename_without_extension}", ext))
    ff = FFmpeg(inputs={'{}'.format(video_path): None}, outputs={
        _result_path: '-s {}*{} -b {}k'.format(width, height, bit_rate)}, executable=r".\ffmpeg\ffmpeg.exe")
    print(ff.cmd)
    ff.run()
    return _result_path


# set_video_size(r"D:\project\壁纸管理\wallpapers\video\4.mp4", r"D:\project\壁纸管理\wallpapers\video", 1920, 1080)
