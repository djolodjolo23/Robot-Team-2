import time
import robomaster
from robomaster import conn
from MyQR import myqr
from PIL import Image


QRCODE_NAME = "qrcode.png"

if __name__ == '__main__':

    helper = conn.ConnectionHelper()
    info = helper.build_qrcode_string(ssid="OnePlus Anton", password="robocoff")
    myqr.run(words=info)
    time.sleep(1)
    img = Image.open(QRCODE_NAME)
    img.show()
    print("Please scan the QR code to connect to the robot's WiFi.")
    if helper.wait_for_connection():
        print("Connected!")
    else:
        print("Connect failed!")