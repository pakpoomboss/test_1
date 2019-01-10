import argparse
import cv2
import datetime
import face_recognition
import imutils
import numpy as np
import pygame
import sqlite3 as sq
import time
import Tkinter as tk
import tkFont as tkfont
import tkMessageBox
import webbrowser

from ast import literal_eval
from imutils.video import VideoStream
from pygame import mixer
from pyzbar import pyzbar
from scipy.spatial import distance as dist
