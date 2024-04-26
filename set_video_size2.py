"""
版权声明：本文为博主原创文章，遵循
CC
4.0
BY - SA
版权协议，转载请附上原文出处链接和本声明。

原文链接：https: // blog.csdn.net / zhiweihongyan1 / article / details / 121887259
"""
import subprocess
import json
import os
from ffmpy import FFmpeg


# 获取视频分辨率和像素宽高比
def get_video_properties(video_path):
    command = fr'.\ffmpeg\ffprobe.exe -v error -show_entries stream=width,height,sample_aspect_ratio -of json "{video_path}"'
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding='gbk')

    if result.returncode == 0:
        data = json.loads(result.stdout)
        print(data)
        width = int(data['streams'][0]['width'])
        height = int(data['streams'][0]['height'])
        sar_ratio = data['streams'][0]['sample_aspect_ratio']
        sar_numerator, sar_denominator = map(int, sar_ratio.split(':'))
        return width, height, sar_numerator, sar_denominator
    else:
        raise Exception(f"获取视频属性出错: {result.stderr}")


# 调整视频大小并保持宽高比
def set_video_size(video_path, output_dir, width, height, bit_rate=20000):
    ext = os.path.splitext(video_path)[1].lower()
    if ext != '.mp4':
        raise ValueError('不支持的视频格式。仅支持 MP4 格式。')

    original_width, original_height, sar_numerator, sar_denominator = get_video_properties(video_path)

    # 计算新的高度，保持原始宽高比
    new_height = int(height * (original_height / original_width) * (sar_numerator / sar_denominator))

    output_filename = f"b_{os.path.basename(video_path)}"
    output_path = os.path.join(output_dir, output_filename)

    ff = FFmpeg(inputs={video_path: None}, outputs={
        output_path: f'-vf "scale={width}:{new_height}" -b:v {bit_rate}k -c:a aac'},
                executable=r".\ffmpeg\ffmpeg.exe")
    # ff = FFmpeg(inputs={video_path: None}, outputs={
    #     output_path: f'-vf "scale={width}:{new_height}" -c:v h264 -b:v {bit_rate}k -c:a aac'},
    #             executable=r".\ffmpeg\ffmpeg.exe")

    print(ff.cmd)
    ff.run()

    return output_path


# 示例用法
# set_video_size(r"D:\project\壁纸管理\wallpapers\video\4.mp4", r"D:\project\壁纸管理\wallpapers\video", 1920, 1080)
# .\ffmpeg\ffmpeg.exe -i D:\project\壁纸管理\wallpapers\video\4.mp4 -s 1920*1080 -b 20000k D:\project\壁纸管理\wallpapers\video\b_4.mp4
