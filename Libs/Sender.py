import time
from threading import Event
import socket
import datetime
from PyQt5.QtCore import QThread, pyqtSignal
from Libs.Conf import VICON
import datetime
import winsound
import serial
import RPi.GPIO as GPIO

HIGH = 255
LOW = 0




# HIGH = b'1'
# LOW = b'Q'
def timeNow():
    timenow = datetime.datetime.now().time().strftime("%H:%M:%S.%f")
    return timenow


class TTLSender(QThread):
    run_output = pyqtSignal(int)
    time = Event()

    def __init__(self):
        QThread.__init__(self)
        self._isRunning = False

    def setSerial(self, ser: serial.Serial):
        self.ser = ser

    def run(self) -> None:
        # send the information we want to send
        # to start, we need A rising edge (or positive edge) is the low-to-high transition

        print("sending ttl at: " + timeNow())
        self.ser.write(HIGH)
        self.time.wait(100. / 1000)
        self.ser.write(LOW)
        self.playNotification()

    def stop(self):
        self._isRunning = False
        self.time.set()
        self.time.clear()
        self.run_output.emit(0)

    # def playNotification(self):
    #     frequency = 2500  # Set Frequency To 2500 Hertz
    #     duration = 1000  # Set Duration To 1000 ms == 1 second
    #     winsound.Beep(frequency, duration)

    def playNotification(self):
        BuzzerPin = 23

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BuzzerPin, GPIO.OUT, initial=GPIO.LOW)

        GPIO.output(BuzzerPin, GPIO.HIGH)
        time.sleep(0.5)
        print("Beep")
        GPIO.output(BuzzerPin, GPIO.LOW)


class SendReadUDP(QThread):
    is_started = pyqtSignal(int)

    def __init__(self, is_read: bool = True):
        QThread.__init__(self)
        print("Init socket binding")
        self.is_read = is_read
        self.sock = socket.socket(socket.AF_INET,  # Internet
                                  socket.SOCK_DGRAM)  # UDP

    def send(self):

        print("Start sending UDP Message: ")
        # Let's send data through UDP protocol
        packet_ID = 0
        while True:
            packet_ID += 1
            #### get current time in format HHMMSS
            timenow = datetime.datetime.now().time().strftime("%H%M%S")
            #### simple message, please note the variables. Using the current time allows
            #### having unique ID for the trial. If the recording exist with the current
            #### file name, the recording won't start unless in Nexus the "Permit overwrite
            #### existing files" is ticked.
            test_message = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>" \
                           "<CaptureStart>" \
                           "<Name VALUE=\"" + VICON.TRIAL_NAME + "" + str(timenow) + "\"/>" \
                                                                                     "<Notes VALUE=\"\"/>" \
                                                                                     "<Description VALUE=\"\"/>" \
                                                                                     "<DatabasePath VALUE=\"\"/>" \
                                                                                     "<Delay VALUE = \"-20\"/>" \
                                                                                     "<PacketID VALUE=\"" + str(
                packet_ID) + "\"/>" \
                             "</CaptureStart>"

            try:
                self.sock.sendto(test_message.encode(), (VICON.UDP_IP, VICON.UDP_PORT))
                self.is_started.emit(1)
                break

            except socket.error:

                pass
            time.sleep(10)

    def read(self):

        self.sock.bind(("", VICON.UDP_PORT))
        self.sock.setblocking(0)
        while True:
            try:
                # Attempt to receive up to 1024 bytes of data
                data, addr = self.sock.recvfrom(300)
                # print(data)
                # Echo the data back to the sender
                if "CaptureStart" in data.decode("utf-8"):
                    print("Nexus is started at: " + timeNow())
                    self.is_started.emit(1)
                    # break
                elif "CaptureStop" in data.decode("utf-8"):
                    print("Nexus is stop at: " + timeNow())
                    self.is_started.emit(1)

            except socket.error:
                # If no data is received, you get here, but it's not an error
                # Ignore and continue
                pass
            time.sleep(1. / 10000000)

    def run(self) -> None:
        if self.is_read:
            self.read()
        else:
            self.send()

    def stop(self):
        self.sock.detach()


if __name__ == "__main__":
    import serial
    from Libs.Sender import Sender, UDPSender
    from Libs.Conf import Tobii

    sender = Sender()
    ser = serial.Serial(
        port=Tobii.port_name,  # please make sure the port name is correct
        baudrate=115200,  # maximum baud rate 115200
        bytesize=serial.EIGHTBITS,  # set this to the amount of data you want to send
        stopbits=serial.STOPBITS_ONE,
        timeout=0
    )
    sender.setSerial(ser)
    sender.start(priority=QThread.HighestPriority)
    # udpSender = UDPSender()
    # udpSender.start()
