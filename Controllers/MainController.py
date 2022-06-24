import sys

from Views.Dialog import Ui_MainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread
import serial
from Libs.Sender import Sender, UDPSender
from Libs.Conf import Tobii
import datetime

class MainController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.view = Ui_MainWindow()

        self.sender = Sender()


        # action of start and stop button
        self.view.startButton.clicked.connect(self.startRecording)
        self.view.stopButton.clicked.connect(self.stopRecording)

        # action when sender is ready
        self.sender.run_output.connect(self.onProgress)
        self.ser = serial.Serial(
            port=Tobii.port_name,  # please make sure the port name is correct
            baudrate=115200,  # maximum baud rate 115200
            bytesize=serial.EIGHTBITS,  # set this to the amount of data you want to send
            stopbits=serial.STOPBITS_ONE,
            timeout=0
        )
        self.sender.setSerial(self.ser)

        # vicon
        self.udp_sender = UDPSender()
        self.udp_sender.is_started.connect(self.sync)
        self.udp_sender.start(priority=QThread.HighestPriority)

    def startRecording(self):
        self.view.startButton.setEnabled(False)



    def sync(self):
        self.sender.start(priority=QThread.HighestPriority)
        self.sender.stop()

    def stopRecording(self):
        self.view.stopButton.setEnabled(False)


    def onProgress(self, i):
        # print(i)
        if i == 1:
            self.view.stopButton.setEnabled(True)
        else:
            self.view.startButton.setEnabled(True)





    def run(self):
        self.view.show()
        return self.app.exec_()