import ctypes
import os
import sys
import logging
import coloredlogs
import a
from threading import Thread

from PyQt5.QtCore import QRect, QCoreApplication, QMetaObject
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QMainWindow, QCheckBox

from video_paper2 import display

coloredlogs.install(level='DEBUG', fmt='[%(levelname)s] [%(asctime)s]: %(message)s')
logging.info("日志设置成功, Wallpaper开始运行")

path: str = os.path.split(os.path.abspath(__file__))[0]
logging.debug(f"当前工作目录{path}")


class Utils:

    @classmethod
    def set_img(cls, path: str):
        path = os.path.abspath(path)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 0)
        logging.info("设置壁纸成功")


class Wallpaper(object):
    def __init__(self, MainWindow):
        self.model = 0
        self.lock_text = ["锁定壁纸", "锁定视频"]
        self.set_model_text = ["视频模式", "壁纸模式"]
        self.model_text = ["main", "video"]
        self.preview = ["图片预览：", "视频封面："]
        self.format = ["png", "jpg"]
        self.num = 1
        self.is_run = True
        self.MainWindow = MainWindow
        self.path: str = os.path.split(os.path.abspath(__file__))[0]
        self.setupUi(MainWindow)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("wallpaper")
        MainWindow.resize(300, 400)

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.pushButton_quit = QPushButton(self.centralwidget)
        self.pushButton_quit.setGeometry(QRect(0, 0, 41, 23))
        self.pushButton_quit.setShortcut("")
        self.pushButton_quit.setObjectName("pushButton_quit")
        self.pushButton_quit.clicked.connect(self.quit)

        self.pushButton_set = QPushButton(self.centralwidget)
        self.pushButton_set.setGeometry(QRect(50, 0, 41, 23))
        self.pushButton_set.setObjectName("pushButton_set")
        self.pushButton_set.clicked.connect(self.set_wallpaper)

        self.pushButton_setModel = QPushButton(self.centralwidget)
        self.pushButton_setModel.setGeometry(QRect(220, 0, 75, 23))
        self.pushButton_setModel.setObjectName("pushButton_setModel")
        self.pushButton_setModel.clicked.connect(self.set_model)

        self.label = QLabel(self.centralwidget)
        self.label.setGeometry(QRect(0, 50, 54, 12))
        self.label.setObjectName("label")

        self.pushButton_jian = QPushButton(self.centralwidget)
        self.pushButton_jian.setGeometry(QRect(30, 50, 31, 23))
        self.pushButton_jian.setObjectName("pushButton_jian")
        self.pushButton_jian.clicked.connect(self.jian)

        self.lineEdit = QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QRect(70, 52, 61, 20))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setText(str(self.num))

        self.pushButton_jia = QPushButton(self.centralwidget)
        self.pushButton_jia.setGeometry(QRect(140, 50, 31, 23))
        self.pushButton_jia.setObjectName("pushButton_jia")
        self.pushButton_jia.clicked.connect(self.add)

        self.checkBox = QCheckBox(self.centralwidget)
        self.checkBox.setGeometry(QRect(180, 50, 101, 16))
        self.checkBox.setObjectName("checkBox")

        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setGeometry(QRect(0, 80, 54, 12))
        self.label_2.setObjectName("label_2")

        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setGeometry(QRect(0, 100, 240, 135))
        if self.model == 0:
            self.label_3.setStyleSheet(f"border-image: url(:/image/wallpapers/main{self.num}.png);")
        elif self.model == 1:
            self.label_3.setStyleSheet(f"border-image: url(:/image/wallpapers/video/video{self.num}.jpg);")
        self.label_3.setText("")
        self.label_3.setObjectName("label_3")

        # player = QMediaPlayer()
        # vw = QVideoWidget()  # 定义视频显示的widget
        # vw.show()
        # player.setVideoOutput(vw)  # 视频播放输出的widget，就是上面定义的
        # player.setMedia(QMediaContent(QFileDialog.getOpenFileUrl()[0]))  # 选取视频文件
        # player.play()

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

        logging.info("界面初始化完成")

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton_quit.setText(_translate("MainWindow", "退出"))
        self.pushButton_set.setText(_translate("MainWindow", "切换"))
        self.pushButton_setModel.setText(_translate("MainWindow", self.set_model_text[self.model]))
        self.label.setText(_translate("MainWindow", "选择:"))
        self.pushButton_jian.setText(_translate("MainWindow", "-"))
        self.pushButton_jia.setText(_translate("MainWindow", "+"))
        self.checkBox.setText(_translate("MainWindow", self.lock_text[self.model]))
        self.label_2.setText(_translate("MainWindow", self.preview[self.model]))

    def set_model(self):
        if self.model == 0:
            self.model = 1
            self.label_3.setEnabled(False)
        elif self.model == 1:
            self.model = 0
        self.setupUi(window)
        logging.info(f"切换模式成功,当前模式为{'视频'if self.model else '图片'}")

    def add(self):
        self.num += 1
        if self.num == 21:
            self.num = 0
        self.setupUi(window)

    def jian(self):
        self.num -= 1
        if self.num == -1:
            self.num = 20
        self.setupUi(window)

    def quit(self):
        self.is_run = False
        if not self.is_run:
            os.system("taskkill /f /im ffplay.exe")
        self.MainWindow.close()

    def set_wallpaper(self):
        if self.model == 0:
            os.system("taskkill /f /im ffplay.exe")
            Utils.set_img(f'{self.path}\\wallpapers\\main{self.num}.png')
        elif self.model == 1:
            os.system("taskkill /f /im ffplay.exe")
            self.t1 = Thread(target=self.play_wallpaper)
            self.t1.start()

    def play_wallpaper(self):
        display(f'{self.path}\\wallpapers\\video\\{self.num}.mp4')
        if not self.is_run:
            os.system("taskkill /f /im ffplay.exe")


if __name__ == "__main__":
    logging.info("开始启动程序")
    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = Wallpaper(window)
    window.show()
    sys.exit(app.exec_())
