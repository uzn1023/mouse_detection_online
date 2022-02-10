##!/usr/bin/env python
import cv2
import numpy as np
import PySimpleGUI as sg
from serial.tools import list_ports
import serial

def setparam():
    param = []
    cameras = []
    for i1 in range(0, 20): 
        cap1 = cv2.VideoCapture( i1, cv2.CAP_DSHOW )
        if cap1.isOpened(): 
            cameras.append(i1)
        cap1.release()

    # Arduino ポートリスト取得
    ports = list_ports.comports()    # ポートデータを取得
    devices = [info.device for info in ports]
    print("Found cameras: " + str(cameras))
    print ("Founds devides: " + str(devices))
    # GUI preparation
    sg.theme('Black')
    txt_cmr = sg.Text('Select Camera',size=(15,1), background_color='#F7F3EC', text_color='#000')
    cmb_cmr = sg.Combo(cameras, default_value=cameras[0],size=(10, 1), readonly=True, key="cmr_select")
    txt_ald = sg.Text('Select Arduino',size=(15,1), background_color='#F7F3EC', text_color='#000')
    cmb_ald = sg.Combo(devices, default_value=devices[0],size=(10, 1), readonly=True, key="ald_select")
    column = [txt_cmr, cmb_cmr],\
             [txt_ald, cmb_ald]
    layout = [[sg.Column(column, background_color='#F7F3EC')], [sg.Image(filename='', key='frame'), sg.Image(filename='', key='image')],[sg.Button('Done', size=(10, 1), font='Helvetica 14')]]
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
    while(1):
        event, values = window.read(timeout=0)
        if CAMERA != int(values["cmr_select"]):
            CAMERA = int(values["cmr_select"])
            capture = cv2.VideoCapture(CAMERA)
        ret, frame = capture.read()
        framebytes = cv2.imencode('.png', frame)[1].tobytes()
        window['frame'].update(data=framebytes)
        if DEVICE != values["ald_select"]:
            DEVICE = str(values["ald_select"])
            ser.port = DEVICE
            ser.bandrate = 9600
            ser.setDTR(False)
            ser.open()
        outputval += 25
        if outputval > 255:
            outputval = 0
        ser.write(outputval.to_bytes(1, 'big'))

        if event in ('Done', None):
            param.append(CAMERA)
            print("Selected camera: " + str(CAMERA))
            param.append(DEVICE)
            print("Selected Arduino: " + str(DEVICE))
            break
    window.close()
    ser.close()
    return param

if __name__ == "__main__" :
    setparam()



