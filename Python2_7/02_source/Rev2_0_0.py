import argparse
import cv2
import datetime
import face_recognition
import imutils
import numpy as np
import pygame
import os
import sqlite3 as sq
import subprocess
import time
import tkFont as tkfont
import Tkinter as tk
import tkMessageBox

from ast import literal_eval
from pygame import mixer
from pyzbar import pyzbar
from scipy.spatial import distance as dist
from sysfs.gpio import Controller, OUTPUT, INPUT, RISING

Cap = cv2.VideoCapture(1)

path = '/home/ubuntu/Kub_Dee/Python2_7'
con  = sq.connect(path + '/01_db/' + 'db_driver.conf')
c    = con.cursor()

db_path = '/home/ubuntu/Kub_Dee/Python2_7/01_db'
db_con  = sq.connect(db_path + '/Data.conf')
db_c    = db_con.cursor()

media_path = '/home/ubuntu/Kub_Dee/Python2_7/03_media'

Controller.available_pins = [37, 186, 219]
Vibra_pin    = Controller.alloc_pin(37, OUTPUT)
Button_pin   = Controller.alloc_pin(186, INPUT)
Shutdown_pin = Controller.alloc_pin(219, INPUT)
Vibra_pin.set()


_per_threshold_        = 0.9
_max_mar_threshold_    = 0.2
_min_mar_threshold_    = 0.15
_time_window_size_     = datetime.timedelta(seconds=3)
_close_time_threshold_ = datetime.timedelta(seconds=2)
_alarm_time_threshold_ = datetime.timedelta(seconds=3)

_url_ = "https://meet.jit.si/Kub-Dee"

class KubDeeApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.winfo_toplevel().title("Kub-Dee System")
        self.resizable(width=False, height=False)
	self.attributes("-fullscreen", True)

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, PageOne, WarningPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")
        self.update()

        self.qr_read()

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

    def qr_read(self):
        # construct the argument parser and parse the arguments
        ap = argparse.ArgumentParser()
        ap.add_argument("-o", "--output", type=str, default="barcodes.csv",
                        help="path to output CSV file containing barcodes")
        args = vars(ap.parse_args())

        # open the output CSV file for writing and initialize the set of
        # barcodes found thus far
        csv = open(args["output"], "w")
        found = set()


        qr_status = True

        while qr_status:
            # grab the frame from the threaded video stream and resize it to
            # have a maximum width of 400 pixels
	    ret, frame = Cap.read()
            frame = imutils.resize(frame, width=400)

            # find the barcodes in the frame and decode each of the barcodes
            barcodes = pyzbar.decode(frame)

            if barcodes != []:
                for barcode in barcodes:
                    # extract the bounding box location of the barcode and draw
                    # the bounding box surrounding the barcode on the image
                    (x, y, w, h) = barcode.rect
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 255), 2)

                    # the barcode data is a bytes object so if we want to draw it
                    # on our output image we need to convert it to a string first
                    barcodeData = barcode.data.decode("utf-8")
                    barcodeType = barcode.type
                    #print(barcodeData)

                try:
                    cursor = db_con.execute('SELECT Name, EAR FROM tb_result WHERE ID = ?', (barcodeData,))
                    for row in cursor:
                        user       = row[0]
                        EAR_Normal = row[1]
                    EAR_Normal = float(EAR_Normal)
                    print(user)
                    print(EAR_Normal)

                    qr_status = False

                    text = "{}".format("Welcome " + user)
                    cv2.putText(frame, text, (100, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                except:
                    # draw the barcode data and barcode type on the image
                    text = "{}".format("Invalid QR Code")
                    cv2.putText(frame, text, (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                    self.show_frame("WarningPage")

            # show the output frame
            cv2.imshow("Barcode Scanner", frame)
	    cv2.moveWindow("Barcode Scanner", 775, 400) 
            key = cv2.waitKey(1) & 0xFF

            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break

        # close the output CSV file do a bit of cleanup
        csv.close()
        cv2.destroyAllWindows()
        Cap.release()
	time.sleep(1)

        self.show_frame("PageOne")
        self.update()
        EAR_Cal = EARCalculate()
        EAR_Cal.Process(EAR_Normal)

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg='black')
        self.controller = controller

        label = tk.Label(self, text="Please Sign in using your QR code", font=controller.title_font, fg="white", bg="black")
        label.pack(side="top", fill="x", pady=50)

class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='black')
        label_1 = tk.Label(self, text="Please Drive Carefully", font=controller.title_font, fg="white", bg="black")
        label_1.pack(side="top", fill="x", pady=50)
        label_2 = tk.Label(self, text="We will be with you all the way!!", font=controller.title_font, fg="white", bg="black")
        label_2.pack(side="top", fill="x", pady=10)

        self.delay = 15
        self.update()

class WarningPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='black')
        label = tk.Label(self, text="Your QR code has not been registered", font=controller.title_font, fg="white", bg="black")
        label.pack(side="top", fill="x", pady=50)
        label_1 = tk.Label(self, text="Please try again or contact GA", font=controller.title_font, fg="white", bg="black")
        label_1.pack(side="top", fill="x", pady=0)

        self.delay = 15
        self.update()

class EARCalculate():

    def __init__(self):
        self.num_face = 0
        self.left_eye = []
        self.right_eye = []
        self.top_lip = []
        self.bottom_lip = []
        self.Alarm_Cal = AlarmCalculate()
	self.Shutdown = Shutdown_Handling()

    def save_result(self, count, datetime, p_head, p_leye, p_reye, p_tlip, p_blip, EAR_raw, MAR):
        data = (count, datetime, p_head, p_leye, p_reye, p_tlip, p_blip, EAR_raw, MAR)

        # Create table
        c.execute(
            'CREATE TABLE IF NOT EXISTS tb_result (count TEXT, datetime TEXT, p_head TEXT, '
            'p_leye TEXT, p_reye TEXT, p_tlip TEXT, p_blip TEXT, EAR_raw TEXT, MAR TEXT)')
        con.commit()

        # Insert data
        c.execute('INSERT INTO tb_result VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', data)
        con.commit()

    def face_detect(self, imCheck):
        small_frame = cv2.resize(imCheck, (160, 120))
        face_locations = face_recognition.face_locations(small_frame)
        self.num_face = 0
        if len(face_locations) != 0:
            del self.left_eye[:]
            del self.right_eye[:]
            del self.top_lip[:]
            del self.bottom_lip[:]

            for (top, right, bottom, left) in face_locations:
                self.num_face += 1
                self.left, self.top, self.right, self.bottom = left, top, right, bottom

                face_landmarks_list = face_recognition.face_landmarks(small_frame)

                for face_landmarks in face_landmarks_list:
                    facial_features = [
                        'left_eye',
                        'right_eye',
                        'top_lip',
                        'bottom_lip'
                    ]
                self.left_eye = face_landmarks[facial_features[0]]
                self.right_eye = face_landmarks[facial_features[1]]
                self.top_lip = face_landmarks[facial_features[2]]
                self.bottom_lip = face_landmarks[facial_features[3]]

        if self.num_face > 0:
            status = True
        else:
            status = False

        return status


    def ear_calculation(self, p_leye, p_reye):
        A = dist.euclidean(p_leye[1], p_leye[5])
        B = dist.euclidean(p_leye[2], p_leye[4])
        C = dist.euclidean(p_leye[0], p_leye[3])
        l_EAR = (A + B) / (2.0 * C)

        A = dist.euclidean(p_reye[1], p_reye[5])
        B = dist.euclidean(p_reye[2], p_reye[4])
        C = dist.euclidean(p_reye[0], p_reye[3])
        r_EAR = (A + B) / (2.0 * C)

        avg_EAR = (l_EAR + r_EAR)/2

        return avg_EAR

    def mar_calculation(self, p_mouth):
        A = dist.euclidean(p_mouth[1], p_mouth[5])
        B = dist.euclidean(p_mouth[2], p_mouth[4])
        C = dist.euclidean(p_mouth[0], p_mouth[3])
        MAR = (A + B) / (2.0 * C)

        return MAR

    def Process(self, EAR_Normal):
	global Cap

	Cap = cv2.VideoCapture(1)

        face_locations     = []
        time_window        = []
        EAR_window         = []
        MAR_window         = []
        count      = 0
        count_save = 0
	alarm_flag = False
        clear_flag = False
        status = True

        while True:
            start = time.time()

            # Grab a single frame of video
            ret, frame = Cap.read()
            status = self.face_detect(frame)

            if status:
		## head drawing ##
                p_head = ([self.left * 2, self.top * 2], [self.right * 2, self.bottom * 2])

                cv2.rectangle(frame, (self.left * 2, self.top * 2), (self.right * 2, self.bottom * 2), (255, 0, 0), 1)
                p_head = ([self.left * 2, self.top * 2], [self.right * 2, self.bottom * 2])

                cv2.circle(frame, (p_head[0][0], p_head[0][1]), 1, (0, 0, 255), -1)
                cv2.circle(frame, (p_head[1][0], p_head[1][1]), 1, (0, 0, 255), -1)

                count = 0

                # Eye section ## eye drawing ##
                for point in self.left_eye:
                    cv2.circle(frame, (self.left_eye[count][0] * 2, self.left_eye[count][1] * 2), 1, (0, 0, 255), -1)
                    cv2.circle(frame, (self.right_eye[count][0] * 2, self.right_eye[count][1] * 2), 1, (0, 0, 255), -1)
                    count += 1

                # Mouth section
                corner_l = ((self.bottom_lip[7][0] + self.top_lip[11][0])/2, (self.bottom_lip[7][1] + self.top_lip[11][1])/2)
                corner_r = ((self.bottom_lip[11][0] + self.top_lip[7][0])/2, (self.bottom_lip[11][1] + self.top_lip[7][1])/2)
                lip_point = (corner_l, [self.top_lip[8][0], self.top_lip[8][1]], [self.top_lip[10][0], self.top_lip[10][1]],
                             corner_r, [self.bottom_lip[8][0], self.bottom_lip[8][1]], [self.bottom_lip[10][0], self.bottom_lip[10][1]])

		## mouth drawing ##
                cv2.circle(frame, (int(corner_l[0]) * 2, int(corner_l[1]) * 2), 1, (0, 0, 255), -1)
                cv2.circle(frame, (self.top_lip[8][0] * 2, self.top_lip[8][1] * 2), 1, (0, 0, 255), -1)
                cv2.circle(frame, (self.top_lip[10][0] * 2, self.top_lip[10][1] * 2), 1, (0, 0, 255), -1)
                cv2.circle(frame, (int(corner_r[0]) * 2, int(corner_r[1]) * 2), 1, (0, 0, 255), -1)
                cv2.circle(frame, (self.bottom_lip[8][0] * 2, self.bottom_lip[8][1] * 2), 1, (0, 0, 255), -1)
                cv2.circle(frame, (self.bottom_lip[10][0] * 2, self.bottom_lip[10][1] * 2), 1, (0, 0, 255), -1)

		# Time section
                today = str(datetime.date.today())
                timenow = time.ctime()
                timenow = str(timenow[11:19])
                date_time = today + ' ' + timenow

                # Create ear_window
                EAR_raw = self.ear_calculation(self.left_eye, self.right_eye)
                EAR_window.append(EAR_raw)
                print('EAR: ', EAR_raw)

                # Create mar_window
                MAR = self.mar_calculation(lip_point)
                MAR_window.append(MAR)
                print('MAR: ', MAR)

                # Create time_window
                time_window.append(datetime.datetime.now())
                while (time_window[-1] - time_window[0]) > _time_window_size_:
                    del time_window[0]
                    del EAR_window[0]
                    del MAR_window[0]

		# Calculate & Handle Alarm
                clear_flag = self.Alarm_Cal.Drowsy_Detection(time_window, EAR_window, EAR_Normal, MAR_window)
                if clear_flag:
                    del time_window[:]
                    del EAR_window[:]
                    del MAR_window[:]

                # Save log
		count_save += 1
                self.save_result(str(count_save), str(date_time), str(p_head), str(self.left_eye), str(self.right_eye), str(self.top_lip), str(self.bottom_lip), str(EAR_raw), str(MAR))

            # Check for Shutdown
	    if(Shutdown_pin.read() == 1):
		self.Shutdown.Turn_Off(0)

	    #print 'process time',time.time() - start
            cv2.imshow('frame',frame)
	    cv2.moveWindow('frame', 650, 400)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        Cap.release()
        cv2.destroyAllWindows()

class AlarmCalculate():

    def __init__(self):
        self.clear_flag  = False
        self.mar_flag   = False

    def Drowsy_Detection(self, time_window, EAR_window, EAR_Normal, MAR_window):
        self.clear_flag = False

        self.mouth_analysis(MAR_window)
        self.close_eye_detection(time_window, EAR_window, EAR_Normal)

        return self.clear_flag

    def mouth_analysis(self, MAR_window):
        MAR_Avg = np.mean(MAR_window)
        self.mar_flag = False

        if max(MAR_window) > _max_mar_threshold_:
            self.mar_flag = True
        elif MAR_Avg > _min_mar_threshold_ and MAR_Avg < _max_mar_threshold_:
            self.mar_flag = True

    def close_eye_detection(self, time_window, EAR_window, EAR_Normal):
        EAR_threshold = (EAR_Normal * _per_threshold_)
        close_st_flag = 0

        print(self.mar_flag)
        if self.mar_flag == False:
            for i in range(len(EAR_window)):
                if EAR_window[i] < EAR_threshold and close_st_flag == 0:
                    close_st = time_window[i]
                    close_st_flag = 1
                elif EAR_window[i] < EAR_threshold:
                    if (time_window[i] - close_st) >= _close_time_threshold_:
                        print('Continuous close eye alarm')
                        AlarmHandle = AlarmHandling()
                        AlarmHandle.AlarmHandle()
                        self.clear_flag = True
                else:
                    close_st_flag = 0

    def avr_detection(self, time_window, EAR_window, EAR_Normal):
        EAR_threshold = (EAR_Normal * _per_threshold_)
        EAR_avg       = 0

        for i in EAR_window:
            EAR_avg = EAR_avg + EAR_window[0]
        EAR_avg = EAR_avg/len(EAR_window)
        if EAR_avg < EAR_threshold:
            alarm_level = 1
            print('Average close eye alarm')
            Alarm_Handle = AlarmHandling()
            Alarm_Handle.AlarmHandle(EAR_Normal)
            self.clear_flag = True

class AlarmHandling():

    def __init__(self):
        self.display_width = 800
        self.display_height = 600
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.red = (255, 0, 0)
        self.gameDisplay = pygame.display.set_mode((self.display_width, self.display_height))
	self.Shutdown = Shutdown_Handling()

        pygame.init()
        pygame.display.set_caption('Alarm!!')

    def message_display(self, text):
        largeText = pygame.font.Font('freesansbold.ttf', 50)
        TextSurf, TextRect = self.text_objects(text, largeText)
        TextRect.center = ((self.display_width / 2), (self.display_height / 2))
        self.gameDisplay.blit(TextSurf, TextRect)

    def text_objects(self, text, font):
        textSurface = font.render(text, True, self.black)
        return textSurface, textSurface.get_rect()

    def AlarmHandle(self):
        global Cap

        alarm_level = 1
        alarm_st    = datetime.datetime.now()
        clock       = pygame.time.Clock()

        Cap.release()

	
        self.gameDisplay.fill(self.red)
        self.message_display('Please Push the Button')
        pygame.display.update()
        mixer.music.load(media_path + '/a_1.mp3')
        mixer.music.play()
        Vibra_pin.reset()

        Driver_resp = False
        print('Alarm Level: %d' % alarm_level)

        while not Driver_resp:
            if (datetime.datetime.now() - alarm_st) >= _alarm_time_threshold_ and alarm_level < 4:
                alarm_level += 1
                alarm_st = datetime.datetime.now()
                if alarm_level == 2:
                    mixer.music.load(media_path + '/a_2.mp3')
		    mixer.music.play()
                elif alarm_level == 3:
                    mixer.music.load(media_path + '/a_3.mp3')
		    mixer.music.play()
                elif alarm_level == 4:
		    subprocess.Popen(['chromium-browser', _url_, '--no-sandbox'], stdout=subprocess.PIPE)    
                    mixer.music.stop()
                print('Alarm Level: %d' % alarm_level)

		# Check for Shutdown
		if(Shutdown_pin.read() == 1):
		    self.Shutdown.Turn_Off(0)

            #for event in pygame.event.get():
                #if event.type == pygame.MOUSEBUTTONDOWN:
                    #Driver_resp = True
	    if(Button_pin.read() == 0):
		subprocess.Popen(['pkill', 'chromium'], stdout=subprocess.PIPE)
		Driver_resp = True
	    if(Shutdown_pin.read() == 1):
		self.Shutdown.Turn_Off(1)
            clock.tick(60)

        pygame.quit()
        Cap = cv2.VideoCapture(1)

        Vibra_pin.set()

class Shutdown_Handling():

    def __init__(self):
        pass

    def Turn_Off(self, call_flag):
	global Cap
	
	if call_flag == 0:
	    Cap.release()
	    cv2.destroyAllWindows()
	else:
	    Vibra_pin.set()
	    subprocess.Popen(['pkill', 'chromium'], stdout=subprocess.PIPE)

	print 'Shutdown!!'
	os.system('kill $PPID')

if __name__ == "__main__":
    KubDeeApp()
