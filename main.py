import cv2
import time
import movement
import copy
import matplotlib.pyplot as plt
import numpy as np
import PySimpleGUI as sg
import io
import serial
import setparam
import pandas as pd

SLEEPTIME = 0.2
CAMERA = 0  # 使用するカメラの割り当て番号（端末に依存）
ARDUINO = "COM3"
frame_old = None
f_out = None
dif_out = None
outputval = None
graph_dpi = 75
outflag = 1

# 起動画面
print("<<<MouseDetectionOnline>>>")
print("Ver. 0.3 : 2022.03.31")
print("")

param = setparam.setparam() # パラメータ取得
CAMERA = param[0]
ARDUINO = param[1]

# 動画ファイル保存先
vid_path = sg.popup_get_file('Where will you save video file?', save_as=True, file_types=(("Video Files", "*.mp4"),))
csv_path = sg.popup_get_file('Where will you save csv file?', save_as=True, file_types=(("CSV Files", "*.csv"),))
# カメラを設定
capture = cv2.VideoCapture(CAMERA)
initialtime = time.time()
times = np.empty(0)
moves = np.empty(0)
times2 = np.empty(0)
maxvals = np.empty(0)

# 動画ファイル保存用の設定
fps = 5                    # カメラのFPSを取得
w = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))              # カメラの横幅を取得
h = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))             # カメラの縦幅を取得
fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')         # 動画保存時のfourcc設定
video = cv2.VideoWriter(vid_path, fourcc, fps, (w, h))      # 動画の仕様

print(fps, w, h)

# シリアルポート設定
if ARDUINO != "None":
    ser = serial.Serial()
    ser.port = ARDUINO
    ser.bandrate = 9600
    ser.setDTR(False)
    ser.open()

# グラフ用
plt.style.use('dark_background')
plt.subplots_adjust(left=0.4, right=0.5, bottom=0, top=1)
fig, ax = plt.subplots(1, 1)
lines, = ax.plot(times, moves)
lines2, = ax.plot(times2, maxvals, linestyle=":")

# pysompleGUIの設定
sg.theme('Black')
## GUI用の要素定義
bgcolor = '#000000'
txtcolor = '#FFFFFF'
txt1 = sg.Text('Output Maximum [px]', justification='center', size=(15, 1), background_color=bgcolor, text_color=txtcolor)
txt2 = sg.Text('Output Voltage[V]'      , justification='center', size=(15, 1), background_color=bgcolor, text_color=txtcolor)
txt3 = sg.Text("Stop"               , justification='center', size=( 5, 1), background_color=bgcolor, text_color="#ff4500", font=('Terminal',12,"bold"),key = "outvalue")
spn1 = sg.Spin([x*1000 for x in range(1000)], 30000, key='outputmax', font='Helvetica 12')
btn1 = sg.Button('Exit', size=(10, 1), font='Helvetica 14')
btn2 = sg.Button('ON', size=(6, 1), font='Helvetica 10', disabled=True, key='ON')
btn3 = sg.Button('OFF', size=(6, 1), font='Helvetica 10', disabled=False, key='OFF')
img1 = sg.Image(filename='', key='graph')
img2 = sg.Image(filename='', key='image')
txt4 = sg.Text('Frame Per Second', justification='center', size=(15, 1), background_color=bgcolor, text_color=txtcolor)
txt5 = sg.Text('', justification='center', size=(15, 1), background_color=bgcolor, text_color="#ff4500", font=('System',12,"bold"),key='overflow')
txt6 = sg.Text('Time Range', justification='center', size=(15, 1), background_color=bgcolor, text_color=txtcolor)
spn3 = sg.Spin([x*100 for x in range(100)], "", key='trange', font='Helvetica 12')
txt7 = sg.Text('Movement Range', justification='center', size=(15, 1), background_color=bgcolor, text_color=txtcolor)
spn4 = sg.Spin([x*1000 for x in range(100)], "", key='mrange', font='Helvetica 12')
spn2 = sg.Spin([5], 5, key='FPS', font='Helvetica 12', readonly=True)

frame1 = sg.Frame("Output", layout = [[txt1, spn1], [txt2, txt3], [btn2, btn3]])
frame2 = sg.Frame("Graph",layout = [[txt6, spn3, txt7, spn4],[img1]])
frame3 = sg.Frame("Image",layout = [[img2]])
frame4 = sg.Frame("",layout = [[btn1]])
frame5 = sg.Frame("Camera Setting",layout = [[txt4, spn2], [txt5]])
column1 = sg.Column([[frame1, frame5],[frame2]])
column2 = sg.Column([[frame3],[frame4]])
layout = [[column1, column2]]
window = sg.Window('MouseDitectionOnline',layout, no_titlebar=False, location=(0, 0), resizable=True)
img_elem = window["image"]
grp_elem = window["graph"]
outval_elem = window["outvalue"]
window.read(timeout=0)

while(True):
    # 時間計測の起点
    starttime = time.time()
    # カメラからフレーム取得
    ret, frame = capture.read()
    # フレームを動画ファイルに保存
    video.write(frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # 差分を取るためにひとつ前のフレームを保存
    if frame_old is None:   # 一番最初に取得したフレームをframe_oldとして保存
        frame_old = copy.copy(frame)
    else:
        # 2回目以降はframe, frame_oldの２つを処理プログラムに投げる
        f_out, dif_out = movement.proc(frame_old, frame, param[2], param[3])
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        frame_old = copy.copy(frame)

        # 画面上に移動量を記載
        txt = "Movement : " + str(dif_out) + " [px]"
        cv2.putText(f_out,
            text=txt,
            org=(20, 40),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1.0,
            color=(0, 0, 0),
            thickness=2,
            lineType=cv2.LINE_4)

        ## dif_outを出力値0-255に変換
        if values["outputmax"] is not None and values["outputmax"] != "":
            if int(values["outputmax"]) > 0:
                outputval = int(( dif_out / int(values["outputmax"] )) * 255)
                if outputval > 255:
                    outputval = 255
                # シリアル出力
                if outflag == 1 and ARDUINO != "None":
                    ser.write(outputval.to_bytes(1, 'big'))
                # プロット
                times2 = np.append(times2, passtime)
                maxvals = np.append(maxvals, values["outputmax"])
                lines2.set_data(times2, maxvals)

    # movement - time グラフ作成
    passtime = time.time() - initialtime
    if dif_out is not None:
        times = np.append(times, passtime)
        moves = np.append(moves, dif_out)
        lines.set_data(times, moves)
        if values["trange"] == "":
            xmin = times.min()
            xmax = times.max()
        else:
            try:
                xmax = times.max()
                xmin = times.max() - int(values["trange"])
            except:
                ValueError
        if values["mrange"] == "":
            ymax = moves.max()
        else:
            try:
                ymax = int(values["mrange"])
            except:
                ValueError
        ax.set_xlim((xmin, xmax))
        ax.set_ylim((moves.min(), ymax))
        plt.xlabel("Time [s]")
        plt.ylabel("Movement [px]")
    # GUI描画
    event, values = window.read(timeout=0)

    ## 出力ON
    if event == 'ON':
        window['ON'].update(disabled=True)
        window['OFF'].update(disabled=False)
        outflag = 1
    if event == 'OFF':
        window['ON'].update(disabled=False)
        window['OFF'].update(disabled=True)
        outflag = 0
    ## 終了ボタン
    if event in ('Exit', None):
        data = np.stack([times, moves])
        data_T = data.T
        np.savetxt(csv_path, data_T, delimiter=",") 
        break

    ## グラフの更新
    item = io.BytesIO()
    fig.savefig(item, format='png',dpi=graph_dpi)
    grp_elem.update(data=item.getvalue())

    ## 画像の更新
    if f_out is not None:
        _f_out = copy.copy(f_out)
        _f_out = cv2.resize(_f_out, dsize=None, fx=0.75, fy=0.75)
        imgbytes = cv2.imencode('.png', _f_out)[1].tobytes()
        img_elem.update(data=imgbytes)

    ## 出力値を表示
    if outputval is not None and outflag == 1:
        outputvol = (outputval / 255) * 5
        outputvol = round(outputvol,2)
        outval_elem.update(str(outputvol))
    else:
        outval_elem.update("STOP")
    # 適宜sleepで時間を合わせる
    try:
        SLEEPTIME = 1 / int(values["FPS"])
    except:
        ValueError
    waittime = SLEEPTIME - ( time.time() - starttime )
    if waittime > 0:
       time.sleep(waittime)
       window['overflow'].update("")
    else:
        interval = time.time() - starttime 
        window['overflow'].update("Time Over")
capture.release()
video.release()
cv2.destroyAllWindows()