##!/usr/bin/env python
import csv

import cv2
import matplotlib.pyplot as plt
import numpy as np
import copy

MORPHOVAL = 5
DILATEVAL = 20
def proc(frame_old,frame):
    f1 = copy.copy(frame_old)
    f2 = copy.copy(frame)

    lower_mouse = np.array([0, 0, 0], dtype=np.uint8)
    upper_mouse = np.array([255, 255, 30], dtype=np.uint8)

    lower_cable = np.array([0, 0, 0], dtype=np.uint8)
    upper_cable = np.array([0, 0, 0], dtype=np.uint8)
    def mousedetect(f):
        # マウスとケーブルを色によって領域判定
        f_mouse = cv2.inRange(f, lower_mouse, upper_mouse)
        f_cable = cv2.inRange(f, lower_cable, upper_cable)
        # OPEN/CLOSE処理によってノイズ除去
        f_mouse = cv2.morphologyEx(f_mouse,cv2.MORPH_OPEN, np.ones((MORPHOVAL,MORPHOVAL),np.uint8))
        f_mouse = cv2.morphologyEx(f_mouse,cv2.MORPH_CLOSE, np.ones((MORPHOVAL,MORPHOVAL),np.uint8))
        f_mouse = cv2.dilate(f_mouse,np.ones((DILATEVAL,DILATEVAL),np.uint8),iterations = 1)  # 胴体と体の分離、ケーブルによるマウス領域の分離を防ぐ
        # f_mouseを面積で分割、最大の領域をマウス領域とする
        nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(f_mouse, 4)
        if nlabels > 1:
            max_idx = np.argmax(stats[1:,:], axis=0)[4] + 1
            f_mouse[labels == max_idx,] = 255
            f_mouse[labels != max_idx,] = 0
        else:
            f_mouse *= 0
        f_mouse = cv2.erode(f_mouse,np.ones((DILATEVAL,DILATEVAL),np.uint8),iterations = 1)   # Close
        return f_mouse, f_cable
    
    def difference(f1_mouse, f1_cable, f2_mouse, f2_cable, f2):
        # 2フレームのマウス領域の差分をとる

        f_xor = cv2.bitwise_xor(f1_mouse, f2_mouse)
        # 差分領域からケーブル領域と重なっている部分を除去
        # f_xor[(f1_cable != 0) | (f2_cable != 0)] = 0
        dif_out = cv2.countNonZero(f_xor)
        f2[f2_mouse != 0] = f2[f2_mouse != 0] * 3/4 + [63, 0, 0]
        f2[f2_cable != 0] = f2[f2_cable != 0] * 3/4 + [0, 0, 63]
        f2[f_xor != 0]    = f2[f_xor    != 0] * 3/4 + [0, 63, 0]
        return f2, dif_out

    f1_mouse, f1_cable = mousedetect(f1)
    f2_mouse, f2_cable = mousedetect(f2)

    f_out, dif_out = difference(f1_mouse, f1_cable, f2_mouse, f2_cable, f2)
    return f_out, dif_out

