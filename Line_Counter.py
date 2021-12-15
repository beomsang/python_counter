import re
import sys
import PyQt5.QtCore
import PyQt5.QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtCore import QTimer, QTime
import time
#import RPi.GPIO as GPIO
import datetime
import pymysql

#서버 주소
addr_db = ""
#서버 포트
port_db = 3306
#DB ID
id_db = ""
#DB PW
pw_db = ""

sum = 0
state = 0
current_time = ""
UPLOAD_TIME_ZONE = ["00", "05", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55"]

class MainWindow(QMainWindow) :
    def __init__(self):
        super(MainWindow, self).__init__()

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.timeout)

        #Layout
        #setting line layout
        layout_line_setting = QHBoxLayout()
        label_line = QLabel("생산 모델")
        self.combo_line = QComboBox()
        self.combo_line.addItem("Upper")
        self.combo_line.addItem("송수화기")
        layout_line_setting.addWidget(label_line)
        layout_line_setting.addWidget(self.combo_line)

        #setting flow layout
        layout_flow_setting = QHBoxLayout()
        label_flow = QLabel("생산 공정")
        self.combo_flow = QComboBox()
        self.combo_flow.addItem("포장")
        layout_flow_setting.addWidget(label_flow)
        layout_flow_setting.addWidget(self.combo_flow)

        #User Button Layout
        layout_user_button = QHBoxLayout()
        self.button_start = QPushButton("시작")
        self.button_start.clicked.connect(self.counter_start)
        self.button_stop = QPushButton("종료")
        self.button_stop.clicked.connect(self.counter_stop)
        self.button_reset = QPushButton("리셋")
        self.button_reset.clicked.connect(self.counter_reset)
        layout_user_button.addWidget(self.button_start)
        layout_user_button.addWidget(self.button_stop)
        layout_user_button.addWidget(self.button_reset)

        #User Layout
        layout_user_layout = QVBoxLayout()
        layout_user_layout.addLayout(layout_line_setting)
        layout_user_layout.addLayout(layout_flow_setting)
        layout_user_layout.addLayout(layout_user_button)

        #수량 보여주는 영역
        layout_counter = QVBoxLayout()
        self.lcd_qtty = QLCDNumber()
        self.lcd_qtty.display('')
        self.lcd_qtty.setDigitCount(8)
        layout_counter.addWidget(self.lcd_qtty)

        #Main Layout
        self.statusBar().showMessage("Ready")
        layout_main = QHBoxLayout()
        layout_main.addLayout(layout_user_layout)
        layout_main.addLayout(layout_counter)
        widget_main = QWidget()
        widget_main.setLayout(layout_main)
        self.setGeometry(200, 200, 400, 150)
        self.setWindowTitle("Nuriflex Line Counter")
        self.center()
        self.setCentralWidget(widget_main)
    #Layout end

    #어플리케이션 중앙 띄우기
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    #카운터기 동작 시작
    def counter_start(self):
        self.statusBar().showMessage("Running")
        self.timer.start()
        self.button_start.setDisabled(True)

    #카운터기 동작 중지
    def counter_stop(self):
        self.statusBar().showMessage("Ready")
        self.button_start.setDisabled(False)
        self.timer.stop()

    def counter_reset(self):
        global sum
        sum = 0
        return sum

    def timeout(self):
        global sum
        sender = self.sender()
        if id(sender) == id(self.timer) :
            self.lcd_qtty.display(sum)
            self.check_upload_time()

    def check_upload_time(self):
        now = datetime.datetime.now()
        now = now + datetime.timedelta(hours=9)
        date_string = now.strftime('%Y-%m-%d %H:%M:%S')
        current_time = date_string
        print("Currnet Time is : " + str(current_time) + "  Current Production qtty : " + str(sum))
        tmp_time = current_time[-5:]
        tmp_time_minute = tmp_time[:2]
        tmp_time_second = tmp_time[-2:]
        if (tmp_time_minute in UPLOAD_TIME_ZONE) and (tmp_time_second == "00") :
            self.upload_database(self, current_time)

    def upload_database(self, current_time) :
        global sum
        conn = pymysql.connect(host = addr_db, port = port_db, user = id_db, passwd = pw_db, db='production', charset='utf8', cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()
        tmp = "\"" + current_time + "\"," + "\"Upper\"," + str(sum) + ")"
        try :
            cur.execute('insert into production.automatic_product_info (`date`, `itm_nm`, `qtty`) values (' + tmp)
            conn.commit()
        except Exception as err :
            print(err)
        finally:
            sum = 0
            return sum


class thread_counter(QThread) :
    def run(self):
        while True :
            if GPIO.input(21) == GPIO.HIGH :
                if GPIO.input(21) == state :
                    continue
                else :
                    sum = sum + 1

                    state = 1
            elif GPIO.input(21) == GPIO.LOW :
                state = 0


if __name__ == "__main__" :
    app = QApplication(sys.argv);
    window = MainWindow()
    window.show()
    app.exec_()
