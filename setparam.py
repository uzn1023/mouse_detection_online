##!/usr/bin/env python
import cv2
import numpy as np
import PySimpleGUI as sg
from serial.tools import list_ports
import serial
import copy
import movement

def setparam():
    param = []
    cameras = []
    mouse_low = [0,0,0]
    mouse_high = [0,0,0]
    for i1 in range(0, 20): 
        cap1 = cv2.VideoCapture( i1, cv2.CAP_DSHOW )
        if cap1.isOpened(): 
            cameras.append(i1)
        cap1.release()
    
    # Arduino ポートリスト取得
    ports = list_ports.comports()    # ポートデータを取得
    devices = [info.device for info in ports]
    devices.append("None")
    print("Found cameras: " + str(cameras))
    print ("Founds devides: " + str(devices))
    # GUI preparation
    sg.theme('Black')
    txt_cmr = sg.Text('Selected Camera',size=(15,1))
    cmb_cmr = sg.Combo(cameras, default_value=cameras[0],size=(10, 1), readonly=True, key="cmr_select")
    txt_ald = sg.Text('Selected Arduino',size=(15,1))
    cmb_ald = sg.Combo(devices, default_value=devices[0],size=(10, 1), readonly=True, key="ald_select")
    txt_H = sg.Text('Mouse color range',size=(15,1))
    txt_Hmin = sg.Text('H min',size=(5,1))
    sld_Hmin = sg.Slider(range=(0, 255),size=(20, 10), orientation='h', key='-Hmin-', default_value = 0)
    txt_Hmax = sg.Text('H max',size=(5,1))
    sld_Hmax = sg.Slider(range=(0, 255),size=(20, 10), orientation='h', key='-Hmax-', default_value = 255)
    txt_Smin = sg.Text('S min',size=(5,1))
    sld_Smin = sg.Slider(range=(0, 255),size=(20, 10), orientation='h', key='-Smin-', default_value = 0)
    txt_Smax = sg.Text('S max',size=(5,1))
    sld_Smax = sg.Slider(range=(0, 255),size=(20, 10), orientation='h', key='-Smax-', default_value = 255)
    txt_Vmin = sg.Text('V min',size=(5,1))
    sld_Vmin = sg.Slider(range=(0, 255),size=(20, 10), orientation='h', key='-Vmin-', default_value = 0)
    txt_Vmax = sg.Text('V max',size=(5,1))
    sld_Vmax = sg.Slider(range=(0, 255),size=(20, 10), orientation='h', key='-Vmax-', default_value = 30)
    column = [txt_cmr, cmb_cmr],\
             [txt_ald, cmb_ald],\
             [txt_H],\
             [txt_Hmin, sld_Hmin, txt_Hmax, sld_Hmax],\
             [txt_Smin, sld_Smin, txt_Smax, sld_Smax],\
             [txt_Vmin, sld_Vmin, txt_Vmax, sld_Vmax]
    layout = [[sg.Column(column)], [sg.Image(filename='', key='frame'), sg.Image(filename='', key='image')],[sg.Button('Done', size=(10, 1), font='Helvetica 14')]]
    window = sg.Window('SelectDevices', layout, no_titlebar=False, location=(0, 0), resizable=True)
    CAMERA = cameras[0]
    capture = cv2.VideoCapture(CAMERA)

    DEVICE = devices[0]
    ser = serial.Serial()
    ser.port = str(DEVICE)
    ser.bandrate = 9600
    ser.setDTR(False)
    ser.open()
    outputval = 0
    frame_old = None
    while(1):
        event, values = window.read(timeout=0)
        if CAMERA != int(values["cmr_select"]):
            CAMERA = int(values["cmr_select"])
            capture = cv2.VideoCapture(CAMERA)
        ret, frame = capture.read()
        f = copy.copy(frame)
        f = cv2.resize(f, dsize=None, fx=0.5, fy=0.5)
        framebytes = cv2.imencode('.png', f)[1].tobytes()
        window['frame'].update(data=framebytes)
        if values["ald_select"] != "None":
            if DEVICE != values["ald_select"]:
                ser.close()
                DEVICE = str(values["ald_select"])
                ser.port = DEVICE
                ser.bandrate = 9600
                ser.setDTR(False)
                ser.open()
            outputval += 25
            if outputval > 255:
                outputval = 0
            ser.write(outputval.to_bytes(1, 'big'))
        else:
            DEVICE = str(values["ald_select"])

        if frame_old is None:   # 一番最初に取得したフレームをframe_oldとして保存
            frame_old = copy.copy(frame)
        else:
            mouse_low = [values["-Hmin-"],values["-Smin-"],values["-Vmin-"]]
            mouse_high = [values["-Hmax-"],values["-Smax-"],values["-Vmax-"]]
            # 2回目以降はframe, frame_oldの２つを処理プログラムに投げる
            f_out, dif_out = movement.proc(frame_old, frame, mouse_low, mouse_high)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            frame_old = copy.copy(frame)
            f_o = copy.copy(f_out)
            f_o = cv2.resize(f_o, dsize=None, fx=0.5, fy=0.5)
            imagebytes = cv2.imencode('.png', f_o)[1].tobytes()
            window['image'].update(data=imagebytes)
        # 最小値が最大値を超えないようにする
        if values["-Hmin-"] > values["-Hmax-"]:
            window["-Hmax-"].update(values["-Hmin-"])
        if values["-Smin-"] > values["-Smax-"]:
            window["-Smax-"].update(values["-Smin-"])
        if values["-Vmin-"] > values["-Vmax-"]:
            window["-Vmax-"].update(values["-Vmin-"])
        # Done > 次の画面に遷移
        if event in ('Done', None):
            param.append(CAMERA)
            print("Selected camera: " + str(CAMERA))
            param.append(DEVICE)
            print("Selected Arduino: " + str(DEVICE))
            param.append(mouse_low)
            param.append(mouse_high)
            break
    window.close()
    ser.close()
    return param

if __name__ == "__main__" :
    setparam()



