import cv2
import serial
import os
import time

# to give jetson permission for Arduino USB port
os.system('echo mule123 | sudo -S chmod a+rw /dev/ttyUSB0')

def drawBox(img, bbox):
    x, y, w, h = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
    print(bbox)
    cv2.rectangle(img, (x, y), ((x+w), (y+h)), (255, 0, 255), 3, 1)
    cv2.putText(img, "Tracking", (75, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    send_data(bbox)
    
def send_data(data):
    '''Convert the 4-tuple into a comma-sep string'''
    data_str = ','.join(map(str, data)) + '\n'  # Convert tuple to comma-separated string
    ser.write(data_str.encode())  # Send data as bytes
   
# open serial port
ser = serial.Serial('/dev/ttyUSB0', 9600)
# reset camera to default pos. before capture
time.sleep(4)
# keep width and height at 640, 480, for faster response
cap = cv2.VideoCapture('''nvarguscamerasrc ! video/x-raw(memory:NVMM), 
width=640, height=480, format=(string)NV12, framerate=(fraction)21/1 
! nvvidconv ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw,
 format=(string)BGR ! appsink''', cv2.CAP_GSTREAMER)
 # MOSSE is fast, but less accurate
tracker = cv2.legacy.TrackerMOSSE_create()
# csrt is more accurate
# tracker = cv2.legacy.TrackerCSRT_create()
success, img = cap.read()
bbox = cv2.selectROI("Tracking", img, False)
tracker.init(img, bbox)


while True:
    timer = cv2.getTickCount()
    success, img = cap.read()

    success, bbox = tracker.update(img)

    if success:
        drawBox(img, bbox)
    else:
        cv2.putText(img, "Lost", (75, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)


    fps = cv2.getTickFrequency()/(cv2.getTickCount()-timer)
    cv2.putText(img, str(int(fps)), (75, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.imshow("Tracking", img)

    # press'q' to close the camera window when running
    if cv2.waitKey(1) & 0xff == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()