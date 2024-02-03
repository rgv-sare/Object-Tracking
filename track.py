import cv2

def drawBox(img, bbox):
    x, y, w, h = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
    print(f"x: {x}, y: {y}, w: {w}, h: {h}")
    cv2.rectangle(img, (x, y), ((x+w), (y+h)), (255, 0, 255), 3, 1)
    cv2.putText(img, "Tracking", (75, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)


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