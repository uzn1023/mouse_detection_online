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

SLEEPTIME = 0.2
CAMERA = 0  # 使用するカメラの割り当て番号（端末に依存）
ARDUINO = "COM3"
frame_old = None
f_out = None
dif_out = None
outputval = None
sendstate = "OFF"
graph_dpi = 75

param = setparam.setparam() # パラメータ取得
CAMERA = param[0]
ARDUINO = param[1]

# カメラを設定
capture = cv2.VideoCapture(CAMERA)
initialtime = time.time()
times = np.empty(0)
moves = np.empty(0)

# シリアルポート設定
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

# pysompleGUIの設定
sg.theme('Black')
## GUI用の要素定義
bgcolor = '#000000'
txtcolor = '#FFFFFF'
txt1 = sg.Text('Output Maximum [px]', justification='center', size=(15, 1), background_color=bgcolor, text_color=txtcolor)
txt2 = sg.Text('Output Voltage[V]'      , justification='center', size=(15, 1), background_color=bgcolor, text_color=txtcolor)
txt3 = sg.Text("Stop"               , justification='center', size=( 5, 1), background_color=bgcolor, text_color="#ff4500", font=('Terminal',12,"bold"),key = "outvalue")
spn1 = sg.Spin([x*1000 for x in range(100)], 30000, key='outputmax')
btn1 = sg.Button('Exit', size=(10, 1), font='Helvetica 14')
btn2 = sg.Button(sendstate, size=(10, 1), font='Helvetica 14')
img1 = sg.Image(filename='', key='graph')
img2 = sg.Image(filename='', key='image')

frame1 = sg.Frame("Output", layout = [[txt1, spn1], [txt2, txt3]])
frame2 = sg.Frame("Graph",layout = [[img1]])
frame3 = sg.Frame("Image",layout = [[img2]])
frame4 = sg.Frame("",layout = [[btn1, btn2]])
column1 = sg.Column([[frame1],[frame2]])
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
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # 差分を取るためにひとつ前のフレームを保存
    if frame_old is None:   # 一番最初に取得したフレームをframe_oldとして保存
        frame_old = copy.copy(frame)
    else:
        # 2回目以降はframe, frame_oldの２つを処理プログラムに投げる
        f_out, dif_out = movement.proc(frame_old, frame)
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
                ser.write(outputval.to_bytes(1, 'big'))
    
    # movement - time グラフ作成
    passtime = time.time() - initialtime
    if dif_out is not None:
        times = np.append(times, passtime)
        moves = np.append(moves, dif_out)
        lines.set_data(times, moves)
        ax.set_xlim((times.min(), times.max()))
        ax.set_ylim((moves.min(), moves.max()))
        plt.xlabel("Time [s]")
        plt.ylabel("Movement [px]")
    # GUI描画
    event, values = window.read(timeout=0)
    
    ## 終了ボタン
    if event in ('Exit', None):     
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
    if outputval is not None:
        outputvol = (outputval / 255)*5
        outputvol = round(outputvol,2)
        outval_elem.update(str(outputvol))

    # 適宜sleepで時間を合わせる
    waittime = SLEEPTIME - ( time.time() - starttime )
    if waittime > 0:
       time.sleep(waittime)
    else:
        interval = time.time() - starttime 
        print("Warning: Time Over Flow")
capture.release()
cv2.destroyAllWindows()