import cv2
import time

SLEEPTIME = 0.1
# VideoCapture オブジェクトを取得します
capture = cv2.VideoCapture(1)

while(True):
    starttime = time.time()
    ret, frame = capture.read()
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    waittime = SLEEPTIME - ( time.time() - starttime )
    print (waittime)
    if waittime > 0:
       time.sleep(waittime)
    else:
        print("YABEE")
capture.release()
cv2.destroyAllWindows()