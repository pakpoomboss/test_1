import cv2
import datetime
import face_recognition
import glob
import numpy as np
import os
import PIL.Image, PIL.ImageTk
import qrcode
import sqlite3 as sq
import sys
import time
import tkFont as tkfont
import Tkinter as tk
import tkMessageBox as messagebox

from scipy.spatial import distance as dist

path = '/home/ubuntu/Kub_Dee/Python2_7/01_db/'
con = sq.connect(path + 'Data.conf')
c = con.cursor()

class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.winfo_toplevel().title("Detect Face")
        self.resizable(width=False, height=False)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.pathDB = path
        self.num_face = 0
        self.left_eye = []
        self.right_eye = []
        self.top_lip = []
        self.bottom_lip = []

        for F in (StartPage, PageOne, PageTwo):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

    def quit_(self):
        self.destroy()

    def combine_funcs(*funcs):
        def combined_func(*args, **kwargs):
            for f in funcs:
                f(*args, **kwargs)
        return combined_func

    def clear_(self, name, phone ,id, mail):

        name.set('')
        phone.set('')
        id.set('')
        mail.set('')

    def get_it(self, name, phone ,id, mail):

        global c
        last_row = 0

        if name.get() and phone.get() and id.get() and mail.get() != "":

            print("You have submitted a record")

            c.execute("CREATE TABLE IF NOT EXISTS tb_result (DataCount INT, Name TEXT, Telephone TEXT, ID TEXT, Email TEXT, count TEXT, datetime TEXT, p_head TEXT, p_leye TEXT, p_reye TEXT, p_tlip TEXT, p_blip TEXT, EAR TEXT, PRIMARY KEY(`ID`))") #SQL syntax

            #Find row
            cursor = con.execute('SELECT * FROM tb_result ORDER BY DataCount DESC LIMIT 1')
            for row in cursor:
                last_row = row[0]
            last_row += 1

            try:
                c.execute("INSERT INTO tb_result (DataCount, Name, Telephone, ID, Email) VALUES (?, ?, ?, ?, ?)",
                        (last_row, name.get(), phone.get(), id.get(), mail.get()))
                con.commit()
			
                self.num2 = last_row
                self.QR_code(id.get())
		

                name.set('')
                phone.set('')
                id.set('')
                mail.set('')

                self.show_frame("PageOne")
            except:
                messagebox.showerror("ERROR", "This ID is duplicated")
                self.show_frame("StartPage")

        else:
            messagebox.showerror("ERROR", "Please fill in every fields")
            self.show_frame("StartPage")

    def SaveResult(self, count, datetime, p_head, p_leye, p_reye, p_tlip, p_blip, EAR):

        global c

        data0 = self.num2
        # data1 = self.name2
        # data2 = self.phone2
        # data3 = self.id2
        # data4 = self.mail2

        print("You have submitted a video")
        #Update by DataCount(row)
        c.execute('Update tb_result Set count=?, datetime=?, p_head=?, p_leye=?, p_reye=?, p_tlip=?, p_blip=?, EAR=? WHERE DataCount=?;'
                  , (str(count), str(datetime), p_head, p_leye, p_reye, p_tlip, p_blip, EAR, data0))
        con.commit()

        #Update by profile
        # c.execute('Update tb_result Set count=?, datetime=?, p_head=?, p_leye=?, p_reye=?, p_tlip=?, p_blip=? WHERE Name=? AND Telephone=? AND ID=? AND Email=?;'
        #           , (str(count), str(datetime), p_head, p_leye, p_reye, p_tlip, p_blip, data1, data2, data3, data4))
        # con.commit()


        # Update every time but next row(not use)
        # print("You have submitted a video")
        #
        # c.execute("INSERT INTO tb_result (count, datetime, p_head, p_leye, p_reye, p_tlip, p_blip) VALUES (?, ?, ?, ?, ?, ?, ?)" ,(str(count), str(datetime), p_head, p_leye, p_reye, p_tlip, p_blip))
        #
        # con.commit()

    def FaceDetect(self,imCheck):
        small_frame = cv2.resize(imCheck, (0, 0), fx=0.5, fy=0.5)
        face_locations = face_recognition.face_locations(small_frame)
        self.num_face = 0
        if len(face_locations) != 0:
            del self.left_eye[:]
            del self.right_eye[:]
            del self.top_lip[:]
            del self.bottom_lip[:]

            for (top, right, bottom, left) in face_locations:
                self.num_face += 1
                self.left,self.top,self.right,self.bottom = left,top,right,bottom

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

    def EAR_Calculation(self, p_leye, p_reye):
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

    def Process(self):
        self.cap           = cv2.VideoCapture(1)
        face_locations     = []
        face_encodings     = []
        process_this_frame = True
        count              = 0
        count_save         = 0
        start              = time.time()
        avg_EAR            = 0
        COUNT_EAR          = 0
        EAR                = 0
        while True:

            # Grab a single frame of video
            ret, frame = self.cap.read()
            #No drawing line
            ret, frame2 = self.cap.read()
            cv2.imwrite('D:\Programs\Pycharm\SCG_GUI\iminput.png',frame)
            status = self.FaceDetect(frame)
            #print status
            if status:
                p_head = ([self.left*2,self.top*2],[self.right*2,self.bottom*2])

                cv2.rectangle(frame,(self.left*2,self.top*2),(self.right*2,self.bottom*2),(255,0,0),1)
                p_head = ([self.left*2,self.top*2],[self.right*2,self.bottom*2])

                count = 0
                for point in self.left_eye:
                    if count == 5:
                        cv2.line(frame,(int(str(self.left_eye[count][0]).replace('L',''))*2,int(str(self.left_eye[count][1]).replace('L',''))*2),(int(str(self.left_eye[0][0]).replace('L',''))*2,int(str(self.left_eye[0][1]).replace('L',''))*2),(0,255,0),1)
                        cv2.line(frame,(int(str(self.right_eye[count][0]).replace('L',''))*2,int(str(self.right_eye[count][1]).replace('L',''))*2),(int(str(self.right_eye[0][0]).replace('L',''))*2,int(str(self.right_eye[0][1]).replace('L',''))*2),(0,255,0),1)
                    else:
                        cv2.line(frame,(int(str(self.left_eye[count][0]).replace('L',''))*2,int(str(self.left_eye[count][1]).replace('L',''))*2),(int(str(self.left_eye[count+1][0]).replace('L',''))*2,int(str(self.left_eye[count+1][1]).replace('L',''))*2),(0,255,0),1)
                        cv2.line(frame,(int(str(self.right_eye[count][0]).replace('L',''))*2,int(str(self.right_eye[count][1]).replace('L',''))*2),(int(str(self.right_eye[count+1][0]).replace('L',''))*2,int(str(self.right_eye[count+1][1]).replace('L',''))*2),(0,255,0),1)
                    count += 1
                count = 0
                for point in self.top_lip:
                    if count == 11:
                        cv2.line(frame,(int(str(self.top_lip[count][0]).replace('L',''))*2,int(str(self.top_lip[count][1]).replace('L',''))*2),(int(str(self.top_lip[0][0]).replace('L',''))*2,int(str(self.top_lip[0][1]).replace('L',''))*2),(0,0,255),1)
                        cv2.line(frame,(int(str(self.bottom_lip[count][0]).replace('L',''))*2,int(str(self.bottom_lip[count][1]).replace('L',''))*2),(int(str(self.bottom_lip[0][0]).replace('L',''))*2,int(str(self.bottom_lip[0][1]).replace('L',''))*2),(0,0,255),1)
                    else:
                        cv2.line(frame,(int(str(self.top_lip[count][0]).replace('L',''))*2,int(str(self.top_lip[count][1]).replace('L',''))*2),(int(str(self.top_lip[count+1][0]).replace('L',''))*2,int(str(self.top_lip[count+1][1]).replace('L',''))*2),(0,0,255),1)
                        cv2.line(frame,(int(str(self.bottom_lip[count][0]).replace('L',''))*2,int(str(self.bottom_lip[count][1]).replace('L',''))*2),(int(str(self.bottom_lip[count+1][0]).replace('L',''))*2,int(str(self.bottom_lip[count+1][1]).replace('L',''))*2),(0,0,255),1)
                    count += 1

                count_save += 1
                if count_save == 101:
                    count_save = 1

                cv2.imwrite(path+ '/temp/' + '/imface'+str(count_save)+'.png',frame)

                today = str(datetime.date.today())
                timenow = time.ctime()
                timenow = str(timenow[11:19])
                date_time = today+' '+timenow

                EAR = self.EAR_Calculation(self.left_eye, self.right_eye)

                p_head = str(p_head)
                p_head = p_head.replace('L','')

                left_eye = str(self.left_eye)
                left_eye = left_eye.replace('L','')

                right_eye = str(self.right_eye)
                right_eye = right_eye.replace('L','')

                top_lip = str(self.top_lip)
                top_lip = top_lip.replace('L','')

                bottom_lip = str(self.bottom_lip)
                bottom_lip = bottom_lip.replace('L','')

                ##self.SaveResult(count_save,date_time,p_head,left_eye,right_eye,top_lip,bottom_lip)

            cv2.imshow('frame',frame)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
            end=time.time()
            elapsed = end - start

            avg_EAR = avg_EAR + EAR
            COUNT_EAR += 1

            #delay 5-6 s
            if elapsed > 6:
                avg_EAR = str(avg_EAR/COUNT_EAR)
                self.SaveResult(count_save, date_time, p_head, left_eye, right_eye, top_lip, bottom_lip, avg_EAR)
                break

        self.cap.release()
        cv2.destroyAllWindows()
        self.show_frame("PageTwo")

    def QR_code(self, ID):

        qr = qrcode.QRCode(
            version = 1,
            error_correction = qrcode.constants.ERROR_CORRECT_H,
            box_size = 10,
            border = 4,
            )

        qr.add_data(ID)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(path + '/QR_Code/' + ID+time.strftime("-%d-%m-%Y-%H-%M-%S")+".png")

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg='lemon chiffon')
        self.controller = controller

        # img = PIL.Image.open('C:\\Users\\Anan\\Desktop\\29313207_1849606191738398_2753293758672928768_n.jpg')
        # back = PIL.ImageTk.PhotoImage(img)

        label = tk.Label(self, text="Please insert your profile", font=controller.title_font, bg="lemon chiffon")
        label.pack(side="top", fill="x", pady=10)

        name_label = tk.Label(self, text= "Name: ", bg="deep sky blue")
        name_label.pack()
        name_text  = tk.StringVar()
        name_entry = tk.Entry(self, textvariable=name_text)
        name_entry.pack(pady=5)

        phone_label = tk.Label(self, text= "Telephone: ", bg="cyan")
        phone_label.pack()
        phone_text  = tk.StringVar()
        phone_entry = tk.Entry(self, textvariable=phone_text)
        phone_entry.pack(pady=5)

        id_label = tk.Label(self, text= "ID: ", bg="pale turquoise")
        id_label.pack()
        id_text  = tk.StringVar()
        id_entry = tk.Entry(self, textvariable=id_text)
        id_entry.pack(pady=5)

        mail_label = tk.Label(self, text= "E-mail: ", bg="light sky blue")
        mail_label.pack()
        mail_text  = tk.StringVar()
        mail_entry = tk.Entry(self, textvariable=mail_text)
        mail_entry.pack(pady=5)

        button1 = tk.Button(self, text="Next page", bg="lawn green",
                            command=lambda: controller.get_it(name_text, phone_text, id_text, mail_text))
        # button1 = tk.Button(self, text="Go to next page",
        #                     command=lambda: controller.show_frame("PageOne"))

        button2 = tk.Button(self, text="Clear", bg="thistle1",
                            command=lambda: controller.clear_(name_text, phone_text, id_text, mail_text))

        #button3 = tk.Button(self, text="Exit", bg="orange red", fg="white",
                            #command=lambda: controller.quit_())

        button1.pack(side='right', padx=5, pady=5)
        button2.pack(side='left', padx=5, pady=5)
        #button3.pack(side='right', padx=150, pady=5)

class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='lemon chiffon')
        label = tk.Label(self, text="This is page 1", font=controller.title_font, bg="lemon chiffon")
        label.pack(side="top", fill="x", pady=10)

        for i in glob.glob(path + '/temp/' + "*.png"):
            os.remove(i)

        button3 = tk.Button(self, text="Snap!", bg="RoyalBlue",font=controller.title_font, fg="white",
                            command=lambda: controller.Process())

        #button5 = tk.Button(self, text="Next page", bg="lawn green",
                            #command=lambda: controller.show_frame("PageTwo"))

        #button6 = tk.Button(self, text="Start page", bg="light goldenrod",
                            #command=lambda: controller.show_frame("StartPage"))

        #button7 = tk.Button(self, text="Exit", bg="orange red", fg="white",
                            #command=lambda: controller.quit_())

        button3.pack(pady=30)
        #button5.pack(side='right', padx=5, pady=5)
        #button6.pack(side='left', padx=5 , pady=5)
        #button7.pack(side='right', padx=58, pady=5)

        self.delay = 15
        self.update()

class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='lemon chiffon')
        label = tk.Label(self, text="Your registration is complete.", font=controller.title_font, bg="lemon chiffon")
        label_1 = tk.Label(self, text="Kub-Dee will always be there for you.", font=controller.title_font,
                         bg="lemon chiffon")
        label_2 = tk.Label(self, text="Have a safe drive!!", font=controller.title_font,
                         bg="lemon chiffon")
        label.pack(side="top", fill="x", pady=10)
        label_1.pack(side="top", fill="x", pady=10)
        label_2.pack(side="top", fill="x", pady=10)
        button4 = tk.Button(self, text="Done", bg="light goldenrod", font=controller.title_font,
                           command=lambda: controller.show_frame("StartPage"))
        button4.pack(pady=5)

if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
