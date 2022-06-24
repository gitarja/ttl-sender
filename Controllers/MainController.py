import sys

from Views.Dialog import Ui_MainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread
import serial
from Libs.Sender import TTLSender, SendReadUDP
from Libs.Conf import Tobii
import datetime


class MainController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.view = Ui_MainWindow()

        # ttl sender

        self.ttl_sender = TTLSender()
        # set serial for TTL sender
        self.ser = serial.Serial(
            port=Tobii.port_name,  # please make sure the port name is correct
            baudrate=115200,  # maximum baud rate 115200
            bytesize=serial.EIGHTBITS,  # set this to the amount of data you want to send
            stopbits=serial.STOPBITS_ONE,
            timeout=0
        )
        self.ttl_sender.setSerial(self.ser)

        # vicon
        self.udp_send_read = SendReadUDP()
        self.udp_send_read.is_started.connect(self.sync)
        self.udp_send_read.start(priority=QThread.HighestPriority)

    def sync(self):
        self.ttl_sender.start(priority=QThread.HighestPriority) # send ttl
        self.ttl_sender.stop() # stop




    def run(self):
        self.view.show()
        return self.app.exec_()
