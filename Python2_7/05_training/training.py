import argparse
import cv2
import datetime
import face_recognition
import imutils
import numpy as np
import pygame
import os
import sqlite3 as sq
import time
import tkFont as tkfont
import Tkinter as tk
import tkMessageBox

from ast import literal_eval
from pygame import mixer
from pyzbar import pyzbar
from scipy.spatial import distance as dist

path = '/home/ubuntu/Kub_Dee/Python2_7'
con  = sq.connect(path + '/01_db/' + 'db_driver.conf')
c    = con.cursor()

db_path = '/home/ubuntu/Kub_Dee/Python2_7/01_db'
db_con  = sq.connect(db_path + '/Data.conf')
db_c    = db_con.cursor()

media_path = '/home/ubuntu/Kub_Dee/Python2_7/03_media'

if __name__ == "__main__":
    KubDeeApp()
