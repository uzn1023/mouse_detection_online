import cv2
import time
import movement
import copy
import matplotlib.pyplot as plt
import numpy as np

SLEEPTIME = 0.1
CAMERA = 0  # 使用するカメラの割り当て番号（端末に依存）
frame_old = None
dif_out = None
# カメラを設定
capture = cv2.VideoCapture(CAMERA)
initialtime = time.time()
times = np.empty(0)
moves = np.empty(0)

fig, ax = plt.subplots(1, 1)
lines, = ax.plot(times, moves)
while(True):
    starttime = time.time()
    ret, frame = capture.read()
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if frame_old is None:
        frame_old = copy.copy(frame)
    else:
        f_out, dif_out = movement.proc(frame_old, frame)
        cv2.imshow("out",f_out)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        frame_old = copy.copy(frame)
    waittime = SLEEPTIME - ( time.time() - starttime )
    # print (time.time() - starttime)

    passtime = time.time() - initialtime
    if dif_out is not None:
        times = np.append(times, passtime)
        moves = np.append(moves, dif_out)
        lines.set_data(times, moves)
        ax.set_xlim((times.min(), times.max()))
        ax.set_ylim((moves.min(), moves.max()))
        plt.pause(0.01)


    if waittime > 0:
       time.sleep(waittime)
    else:
        interval = time.time() - starttime 
        print("Warning: Time Over Flow")
capture.release()
cv2.destroyAllWindows()