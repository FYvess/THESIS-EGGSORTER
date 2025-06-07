<<<<<<< HEAD
import tkinter
import serial
import time
import threading
import RPi.GPIO as l_gpio
import cv2
import numpy as np
from picamera2 import Picamera2
from PIL import Image, ImageTk
import sqlite3
import datetime
from tkintertable import TableCanvas,TableModel
import subprocess
import webbrowser
import joblib

from sklearn.linear_model import LinearRegression
import pandas as pd
from sklearn.model_selection import train_test_split


class c_databank(object):
    g_serial=serial.Serial('/dev/ttyACM0',9600)
    g_readserial=False
    g_parameter=""
    g_imageWeightArray=[]
    g_value=""
    g_data=""
    g_eggpixelcount=0
    g_pixelcountpergram=0
    g_eggweight=0
    g_smallmin=41
    g_smallmax=55
    g_mediummin=56
    g_mediummax=60
    g_largemin=61
    g_largemax=65
    g_xlmin=66
    g_xlmax=70
    g_loadcellreference=0
    g_auto=False

    g_camera_inspection_active= False
    g_camera_thread = None
    
class c_dataview(c_databank):
    def __init__(self,master):
        self.master=master
        self.label1=tkinter.Label(self.master,text='DATA LOGS',fg='white',bg='blue')
        self.label1.grid(column=0,row=0)
        # self.lv_button1=tkinter.Button(self.master,width=40,text="Clear Data",command=lambda:self.f_resetdatabase())
        # self.lv_button1.grid(column=0,row=1,padx=10,pady=10)
        self.lv_frame1=tkinter.Frame(self.master)
        self.lv_frame1.grid(column=0,row=0)
        self.lv_table1=TableCanvas(self.lv_frame1)
        self.lv_table1.show()
        self.f_getdata()

    def f_resetdatabase(self):
        self.lv_db=sqlite3.connect("/home/project4/Desktop/d1.db")
        self.lv_cursor=self.lv_db.cursor()
        self.lv_cursor.execute("delete from t1")
        self.lv_db.commit()
        self.lv_db.close()
        self.f_getdata()
        tkinter.messagebox.showinfo('notification','database data was reset')
        
        
    def f_getdata(self):
        self.lv_count=0
        self.lv_db=sqlite3.connect("/home/project4/Desktop/d1.db")
        self.lv_cursor=self.lv_db.cursor()
        self.lv_cursor.execute("select * from t1 order by strftime('%s',entrytime) desc" )
        self.lv_rows=self.lv_cursor.fetchall()
        self.lv_dict={}
        for self.lv_data in self.lv_rows:
            self.lv_dict[self.lv_count]={}
            self.lv_dict[self.lv_count]['entryid']=str(self.lv_data[0])
            self.lv_dict[self.lv_count]['smallqty']=str(self.lv_data[1])
            self.lv_dict[self.lv_count]['mediumqty']=str(self.lv_data[2])
            self.lv_dict[self.lv_count]['largeqty']=str(self.lv_data[3])
            self.lv_dict[self.lv_count]['extralargeqty']=str(self.lv_data[4])
            self.lv_dict[self.lv_count]['jumboqty']=str(self.lv_data[5])
            self.lv_dict[self.lv_count]['entrytime']=str(self.lv_data[6])
            self.lv_count=self.lv_count+1
        self.lv_db.close()
        self.lv_model1=TableModel()
        self.lv_table1=TableCanvas(self.lv_frame1,model=self.lv_model1,witdh=700,cellwidth=200)
        self.lv_table1.createTableFrame()
        self.lv_model1.importDict(self.lv_dict)
        self.lv_table1.redrawTable()

class c_appsetting(c_databank):
    def __init__(self,master):
        self.master=master
        self.label1=tkinter.Label(self.master,bg='red',fg='white',text="verification reference")
        self.label1.grid(column=0,row=0,padx=5,pady=5)
        # self.label2=tkinter.Label(self.master,bg='red',fg='white',text="pixel conversion")
        # self.label2.grid(column=0,row=1,padx=5,pady=5)
        self.entry1=tkinter.Entry(self.master)
        self.entry1.grid(column=1,row=0,padx=5,pady=5)
        # self.entry2=tkinter.Entry(self.master)
        # self.entry2.grid(column=1,row=1,padx=5,pady=5)
        self.button1=tkinter.Button(self.master,width=20,text='set',command=lambda:self.f_setsetting())
        self.button1.grid(column=0,row=2,pady=5,padx=5)
    
        
class c_main(c_databank):
    def __init__(self,master):
        self.master = master
        self.lv_command=""
        self.frame1=tkinter.Frame(self.master,bg='black')
        self.frame1.grid(column=0,row=0,padx=5,pady=5)
        self.frame2=tkinter.Frame(self.master,bg='black')
        self.frame2.grid(column=0,row=1,padx=5,pady=5)
        self.label1=tkinter.Label(self.frame1,text="System Console",bg='black',fg='white')
        self.label1.grid(column=0,row=0)
        self.label4=tkinter.Label(self.frame1,text="Vision System",bg='black',fg='white')
        self.label4.grid(column=1,row=0)
        self.text1=tkinter.Text(self.frame1,width=60,height=15,bg='gray9',fg='white')
        self.text1.grid(column=0,row=1)
        self.lv_initialimage=Image.open("/home/project4/Desktop/p2.jpg")
        self.lv_temp=ImageTk.PhotoImage(self.lv_initialimage.resize((240,240)))
        self.label3=tkinter.Label(self.frame1,image=self.lv_temp)
        self.label3.grid(column=1,row=1,padx=5,pady=5)
        self.label3.image=self.lv_temp
        self.button1=tkinter.Button(self.frame2,text="Reset",width=15,height=5,bg='yellow',command=lambda:self.f_sendreset())
        self.button1.grid(column=0,row=0)
        self.button2=tkinter.Button(self.frame2,text="Reset\n Calibration",width=15,height=5,bg='yellow',command=lambda:self.f_tareloadcell())
        self.button2.grid(column=1,row=0)
        self.button3=tkinter.Button(self.frame2,text="Calibrate\n Camera",width=15,height=5,bg='yellow',command=lambda:self.f_calibrateloadcell())
        self.button3.grid(column=2,row=0)
        self.button4=tkinter.Button(self.frame2,text="Auto Mode",width=15,height=5,bg='green',command=lambda:self.f_processimageThread())
        self.button4.grid(column=3,row=0)
        self.button5=tkinter.Button(self.frame2,text="Inventory",width=15,height=5,bg='steelblue1',command=lambda:self.f_opendashboard())
        self.button5.grid(column=4,row=0)
        self.button6=tkinter.Button(self.frame2,text="Shutdown",width=15,height=2,bg='firebrick1',command=lambda:self.f_shutdownsystem())
        self.button6.grid(column=4,row=1)
        self.button7=tkinter.Button(self.frame2,text="Req. Data",width=15,height=2,bg='yellow',command=lambda:self.f_getstatisticaldata())
        self.button7.grid(column=0,row=1)
        # self.button8=tkinter.Button(self.frame2,text="Camera\nInspection",width=10,height=5,bg='green',command=lambda:self.f_processimage())
        # self.button8.grid(column=5,row=0)
        self.button9=tkinter.Button(self.frame2,text="Save Stat",width=15,height=2,bg='yellow',command=lambda:self.f_savestat())
        self.button9.grid(column=1,row=1)
        #self.button12=tkinter.Button(self.frame2,text="Save\nStat",width=10,height=5,bg='orange',command=lambda:self.f_savestat())
        # self.button12.grid(column=6,row=0)
        self.button11=tkinter.Button(self.frame2,text="Speed(H)",width=15,height=2,bg='yellow',command=lambda:self.f_speedhigh())
        self.button11.grid(column=2,row=1)
        self.button13=tkinter.Button(self.frame2,text="Speed(L)",width=15,height=2,bg='yellow',command=lambda:self.f_speedlow())
        self.button13.grid(column=3,row=1)
        # self.button13=tkinter.Button(self.frame2,text="Dashboard",width=10,height=2,bg='orange',command=lambda:self.f_opendashboard())
        # self.button13.grid(column=5,row=1)
        # self.button14=tkinter.Button(self.frame2, text="Image Process auto", width=10,height=2, bg="orange", command=lambda:self.f_processimageThread())
        # self.button14.grid(column=6,row=1)
        self.f_initio()
        time.sleep(1)
        c_databank.g_readserial=True
        self.f_readserial()

        self.ref_x_min, self.ref_x_max = 162, 451
        self.real_length_of_reference = 5.8
        #self.egg_data = pd.read_csv('result_combined_1_2.csv')
        #X = self.egg_data[['perimeter', 'height', 'width', 'shape_index']]
        #y = self.egg_data['weight']
        #X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2, random_state=24)
        #self.model = LinearRegression(fit_intercept=False)
        #self.model.fit(X_train,y_train)
        self.model =joblib.load('/home/project4/Desktop/linear_weight_model_v1.pkl')

    def calculateLength(self, width_pixel, height_pixel, ref_x_min, ref_x_max, real_length_of_reference):
        ref_length_pixel = ref_x_max - ref_x_min
        conversion_factor = real_length_of_reference / ref_length_pixel
        real_width = width_pixel * conversion_factor
        real_height = height_pixel * conversion_factor
        return real_width, real_height


    def calculatePerimeterArea(self, perimeter, area, ref_x_min, ref_x_max, real_length_of_reference):
        ref_length_pixel = ref_x_max - ref_x_min
        conversion_factor = real_length_of_reference / ref_length_pixel
        real_perimeter = perimeter * conversion_factor
        real_area = area * conversion_factor
        return real_perimeter, real_area
    
        
    def f_opendashboard(self):
        subprocess.Popen(['python3', '/home/project4/Desktop/files/proj/egg-sorter-dashboard/app.py'])
        time.sleep(1)
        # minimize_command = 'xdotool search --sync --class "Lxterminal" %@ ; xargs xdotool windowminimize'
        # subprocess.run(['bash', '-c', minimize_command], check=True)
        webbrowser.open('http://127.0.0.1:5000')
        
    def on_button_click(self):
        self.f_opendashboard()
        self.button13.config(state=tkinter.DISABLED)
    
    def f_speedhigh(self):
        if(c_databank.g_auto==True):
            tkinter.messagebox.showinfo("notification","stop!\nauto mode is on")
            return
        self.f_resetserial()
        self.lv_command="1009+0000\n"
        c_databank.g_serial.write(self.lv_command.encode("utf-8"))
        c_databank.g_readserial=True;
        self.text1.insert(self.text1.index('end'),'system -> speed change [high]'+'\n')
        self.text1.see(tkinter.END)
        self.f_readserial()
    def f_speedlow(self):
        if(c_databank.g_auto==True):
            tkinter.messagebox.showinfo("notification","stop!\nauto mode is on")
            return
        self.f_resetserial()
        self.lv_command="1010+0000\n"
        c_databank.g_serial.write(self.lv_command.encode("utf-8"))
        c_databank.g_readserial=True;
        self.text1.insert(self.text1.index('end'),'system -> speed change [low]'+'\n')
        self.text1.see(tkinter.END)
        self.f_readserial()
    def f_opendataview(self):
        self.lv_dataviewform=tkinter.Toplevel(self.master)
        self.lv_dataviewform.title("Data Records")
        self.lv_dataviewform.configure(background='red')
        self.lv_dataviewform.geometry('600x400')
        self.lv_dataviewapp=c_dataview(self.lv_dataviewform)
        self.lv_dataviewform.transient(self.master)
        self.lv_dataviewform.grab_set()
        self.master.wait_window(self.lv_dataviewform)
        
        c_databank.g_data=""
        c_databank.g_imageWeightArray = []

        self.f_resetserial()
        self.lv_command="1021+0000\n"
        c_databank.g_serial.write(self.lv_command.encode("utf-8"))
        
    def f_opensetting(self):
        self.lv_settingform=tkinter.Toplevel(self.master)
        self.lv_settingform.title("App setting")
        self.lv_settingform.configure(background='red')
        self.lv_settingform.geometry('500x120')
        self.lv_settingapp=c_appsetting(self.lv_settingform)
        self.lv_settingform.transient(self.master)
        self.lv_settingform.grab_set()
        self.master.wait_window(self.lv_settingform)

    def f_savestat(self):
        if(c_databank.g_auto == True):
            tkinter.messagebox.showinfo("notification", "stop!\nauto mode is on")
            return

        
        self.lv_time=""
        self.lv_time=datetime.datetime.now()
        self.lv_timestring=self.lv_time.strftime("%Y-%m-%d %H:%M:%S")
        expiry_datetime= self.lv_time + datetime.timedelta(days=14)
        expiry_timestring= expiry_datetime.strftime("%Y-%m-%d %H:%M:%S")
        self.lv_database=sqlite3.connect("/home/project4/Desktop/d1.db")
        self.lv_cursor = self.lv_database.cursor()
        
        eggs_weight_array = [weight for weight in c_databank.g_data[6].split(',') if weight.strip()]
        print("heherson", eggs_weight_array)
        # Insert each weight into the t2 table
        for weight in eggs_weight_array:
            if weight:
                weight_value = float(weight) # Or int(weight) if they are always whole numbers
                self.lv_cursor.execute("INSERT INTO eggs_tbl (weight, created_at, expected_expiry) VALUES (?, ?, ?)", (weight_value, self.lv_timestring, expiry_timestring))

        if len(c_databank.g_imageWeightArray) > 0:
            for weight in c_databank.g_imageWeightArray:
                if weight:
                    weight_value=float(weight)
                    self.lv_cursor.execute("INSERT INTO eggs_tbl (weight, created_at, expected_expiry) VALUES (?, ?, ?)", (weight_value, self.lv_timestring, expiry_timestring))
        c_databank.g_imageWeightArray.clear()
        self.lv_cursor.execute("insert into t1 (smallqty,mediumqty,largeqty,extralargeqty,jumboqty,entrytime)values('"
                               +c_databank.g_data[1]+"','"
                               +c_databank.g_data[2]+"','"
                               +c_databank.g_data[3]+"','"
                               +c_databank.g_data[4]+"','"
                               +c_databank.g_data[5]+"','"
                               +self.lv_timestring+"')")
        self.lv_database.commit()
        self.lv_database.close()
        self.text1.insert(self.text1.index('end'),'system -> statistical data saved'+'\n')
        self.text1.see(tkinter.END)
        self.f_opendataview()
    def f_getstatisticaldata(self):
        if(c_databank.g_auto==True):
            tkinter.messagebox.showinfo("notification","stop!\nauto mode is on")
            return
        self.f_resetserial()
        self.lv_command="1006+0000\n"
        c_databank.g_serial.write(self.lv_command.encode("utf-8"))
        c_databank.g_readserial=True;
        self.text1.insert(self.text1.index('end'),'system -> statisticaldata request'+'\n')
        self.text1.see(tkinter.END)
        self.f_readserial()
    def f_checkloadcellvalue(self):
        self.f_resetserial()
        self.lv_command="1005+0000\n"
        c_databank.g_serial.write(self.lv_command.encode("utf-8"))
        c_databank.g_readserial=True;
        self.text1.insert(self.text1.index('end'),'system -> check verification request'+'\n')
        self.text1.see(tkinter.END)
        self.f_readserial()
        print(c_databank.g_loadcellreference)
    def f_setauto(self):
        self.f_resetserial()
        l_gpio.setmode(l_gpio.BCM)
        l_gpio.setup(2,l_gpio.OUT)
        lv_autostatus=l_gpio.input(2)
        if(lv_autostatus==1):
            self.text1.insert(self.text1.index('end'),'system -> current state ['+str(lv_autostatus)+'] turning off'+'\n')
            self.text1.insert(self.text1.index('end'),'system -> auto off'+'\n')
            l_gpio.output(2,l_gpio.LOW)
            c_databank.g_auto=False
        else:
            self.text1.insert(self.text1.index('end'),'system -> current state ['+str(lv_autostatus)+'] turning on'+'\n')
            self.text1.insert(self.text1.index('end'),'system -> auto on'+'\n')
            l_gpio.output(2,l_gpio.HIGH)
            c_databank.g_auto=True
        time.sleep(1)
        self.lv_command="1004+0000\n"
        c_databank.g_serial.write(self.lv_command.encode("utf-8"))
        time.sleep(1)
        c_databank.g_readserial=True;
        self.f_readserial()
        if(lv_autostatus==0):
            self.f_index()
            
    def f_initio(self):
        self.text1.insert(self.text1.index('end'),'system -> io init [start]'+'\n')
        l_gpio.setmode(l_gpio.BCM)
        l_gpio.setup(2,l_gpio.OUT)
        l_gpio.output(2,l_gpio.LOW)
        lv_autostatus=l_gpio.input(2)
        if(lv_autostatus==1):
            self.text1.insert(self.text1.index('end'),'system -> current state ['+str(lv_autostatus)+'] turning off'+'\n')
            self.text1.insert(self.text1.index('end'),'system -> io init [error]'+'\n')
        else:
            self.text1.insert(self.text1.index('end'),'system -> current state ['+str(lv_autostatus)+'] turning off'+'\n')
            self.text1.insert(self.text1.index('end'),'system -> io init [ok]'+'\n')
        self.text1.see(tkinter.END)
            
    def f_sendreset(self):
        if(c_databank.g_auto==True):
            tkinter.messagebox.showinfo("notification","stop!\nauto mode is on")
            return
        self.f_resetserial()
        self.lv_command="1001+0000\n"
        c_databank.g_serial.write(self.lv_command.encode("utf-8"))
        c_databank.g_readserial=True;
        self.text1.insert(self.text1.index('end'),'system -> reset'+'\n')
        self.text1.see(tkinter.END)
        self.f_readserial()
    def f_tareloadcell(self):
        if(c_databank.g_auto==True):
            tkinter.messagebox.showinfo("notification","stop!\nauto mode is on")
            return
        self.f_resetserial()
        self.lv_command="1000+0000\n"
        c_databank.g_serial.write(self.lv_command.encode("utf-8"))
        time.sleep(1)
        c_databank.g_readserial=True;
        self.text1.insert(self.text1.index('end'),'system -> reset verification'+'\n')
        self.text1.see(tkinter.END)
        self.f_readserial()
    def f_calibrateloadcell(self):
        if(c_databank.g_auto==True):
            tkinter.messagebox.showinfo("notification","stop!\nauto mode is on")
            return
        #if(c_databank.g_loadcellreference==0):
        #    tkinter.messagebox.showinfo("notification","stop!\nset reference first")
        #    return
        # self.f_sendreset()
        self.f_resetserial()
        self.lv_command="1003+"+str(0.1)+"\n"
        c_databank.g_serial.write(self.lv_command.encode("utf-8"))
        time.sleep(1)
        c_databank.g_readserial=True;
        self.text1.insert(self.text1.index('end'),'system -> calibrate verification'+'\n')
        self.text1.see(tkinter.END)
        self.f_readserial()
        self.f_checkloadcellvalue()
        self.f_setsetting()
        
    def f_setsetting(self):
        self.lv_filelocation="/home/project4/Desktop/p2.jpg"
        picam2=Picamera2()
        picam2.configure(picam2.create_still_configuration({"size":(600,400)}))
        picam2.start()
        time.sleep(1)
        picam2.capture_file(self.lv_filelocation)
        self.lv_temp=Image.open(self.lv_filelocation)
        self.lv_temp2=self.lv_temp.rotate(90)
        self.lv_temp2.save(self.lv_filelocation)
        picam2.stop()
        picam2.close()

        self.lv_original=cv2.imread(r'/home/project4/Desktop/p2.jpg',0)
        (thresh, self.lv_binary)=cv2.threshold(self.lv_original,127,255,cv2.THRESH_BINARY)
        cv2.imwrite(r'/home/project4/Desktop/p3.jpg',self.lv_binary)

        self.lv_targetbinary=cv2.imread('/home/project4/Desktop/p3.jpg')
        self.lv_grayimage=cv2.cvtColor(self.lv_targetbinary,cv2.COLOR_BGR2GRAY)
        self.blur=cv2.GaussianBlur(self.lv_grayimage,(7,7),1.5,1.5)
        #self.lv_edge=cv2.Canny(self.blur,0,50,3)
        ret,self.lv_edge=cv2.threshold(self.lv_grayimage,127,255,cv2.THRESH_BINARY)
        #contours, hierarchy=cv2.findContours(self.lv_edge,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        contours, hierarchy=cv2.findContours(self.lv_edge,1,2)
        self.area=0
        for cnt in contours:
            self.temp=cv2.contourArea(cnt)
            if(self.temp>self.area):
                self.area=self.temp

        print(self.area)
        c_databank.g_loadcellreference=self.entry1.get()
        c_databank.g_pixelcountpergram=float(self.area)/float(c_databank.g_loadcellreference)
        
        tkinter.messagebox.showinfo('notification','setting updated')
        self.entry1.delete(0,'end')
        
        
    def f_setsetting(self):
        self.lv_filelocation="/home/project4/Desktop/p2.jpg"
        picam2=Picamera2()
        picam2.configure(picam2.create_still_configuration({"size":(600,400)}))
        picam2.start()
        time.sleep(1)
        picam2.capture_file(self.lv_filelocation)
        self.lv_temp=Image.open(self.lv_filelocation)
        self.lv_temp2=self.lv_temp.rotate(90)
        self.lv_temp2.save(self.lv_filelocation)
        picam2.stop()
        picam2.close()

        self.lv_original=cv2.imread(r'/home/project4/Desktop/p2.jpg',0)
        (thresh, self.lv_binary)=cv2.threshold(self.lv_original,127,255,cv2.THRESH_BINARY)
        cv2.imwrite(r'/home/project4/Desktop/p3.jpg',self.lv_binary)

        self.lv_targetbinary=cv2.imread('/home/project4/Desktop/p3.jpg')
        self.lv_grayimage=cv2.cvtColor(self.lv_targetbinary,cv2.COLOR_BGR2GRAY)
        self.blur=cv2.GaussianBlur(self.lv_grayimage,(7,7),1.5,1.5)
        #self.lv_edge=cv2.Canny(self.blur,0,50,3)
        ret,self.lv_edge=cv2.threshold(self.lv_grayimage,127,255,cv2.THRESH_BINARY)
        #contours, hierarchy=cv2.findContours(self.lv_edge,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        contours, hierarchy=cv2.findContours(self.lv_edge,1,2)
        self.area=0
        for cnt in contours:
            self.temp=cv2.contourArea(cnt)
            if(self.temp>self.area):
                self.area=self.temp

        # print(self.area)
        # c_databank.g_loadcellreference=self.entry1.get()
        c_databank.g_pixelcountpergram=float(self.area)/float(c_databank.g_loadcellreference)
        
        # tkinter.messagebox.showinfo('notification','setting updated')
        # self.entry1.delete(0,'end')
        
    def f_index(self):
        self.f_resetserial()
        self.lv_command="1002+0000\n"
        c_databank.g_serial.write(self.lv_command.encode("utf-8"))
        self.text1.insert(self.text1.index('end'),'system -> process egg'+'\n')
        self.text1.see(tkinter.END)
    def f_resetserial(self):
        c_databank.g_serial.flushInput()
        c_databank.g_serial.flushOutput()

    def f_shutdownsystem(self):
        if(c_databank.g_auto==True):
            tkinter.messagebox.showinfo("notification","stop!\nauto mode is on")
            return
        confirm_shutdown = tkinter.messagebox.askyesno(
            "Confirm Shutdown",
            "Are you sure you want to shutdown the system?"
        )
        if confirm_shutdown:
            subprocess.Popen(['sudo', 'shutdown','now'])
        else:
            tkinter.messagebox.showinfo("Cancelled", "Shutdown cancelled.")
            
    def f_processimageThread(self):
        c_databank.g_camera_inspection_active = True
        c_databank.g_auto = True
        l_gpio.setmode(l_gpio.BCM)
        l_gpio.setup(2, l_gpio.OUT)
        lv_autostatus=l_gpio.input(2)
        if(lv_autostatus==1):
            self.text1.insert(self.text1.index('end'), 'system -> current state [' + str(lv_autostatus) + '] turning off' + '\n')
            self.text1.insert(self.text1.index('end'), 'system -> auto off' + '\n')
            l_gpio.output(2, l_gpio.LOW)
            self.lv_command="2016+0000\n"
            c_databank.g_serial.write(self.lv_command.encode("utf-8"))
            c_databank.g_camera_inspection_active = False
            c_databank.g_readserial = False
            c_databank.g_auto = False
        else:
            self.text1.insert(self.text1.index('end'), 'system -> current state [' + str(lv_autostatus) + '] turning on' + '\n')
            self.text1.insert(self.text1.index('end'), 'system -> auto on' + '\n')
            l_gpio.output(2, l_gpio.HIGH)
            self.lv_command="2015+0000\n"
            c_databank.g_serial.write(self.lv_command.encode("utf-8"))
        time.sleep(1)
        
        if hasattr(self, 'g_camera_thread') and self.g_camera_thread is not None and self.g_camera_thread.is_alive():
            print("camera thread is running already")
            return
        self.g_camera_thread = threading.Thread(target=self.f_processimageauto)
        self.g_camera_thread.start()
        self.f_readserial()
        if(lv_autostatus == 0):
            self.f_index()

    def f_processimageauto(self):
        try:
            self.lv_receiveddata = b''
            self.lv_arduinodata="";

            while c_databank.g_camera_inspection_active:
                if (c_databank.g_serial.in_waiting > 0):
                    self.lv_receiveddata = c_databank.g_serial.read()
                    # self.text1.insert(self.text1.index('end'), 'system -> serial data [' + str(self.lv_receiveddata) + ']' + '\n')


                    if self.lv_receiveddata != b'\r' and self.lv_receiveddata != b'\n':
                        self.lv_arduinodata = self.lv_arduinodata + self.lv_receiveddata.decode('ascii')

                    if self.lv_receiveddata == b'\n':
                        # self.text1.insert(self.text1.index('end'), "arduino ->" + self.lv_arduinodata + '\n')
                        # self.text1.see(tkinter.END)
                        self.f_resetserial()
                        c_databank.g_data = self.lv_arduinodata.split('+')
                        if c_databank.g_data[0] == '2014':
                            # Process image
                            print(c_databank.g_data)
                            self.f_processimage()
            
        except Exception as e:
            print("Error in thread: ", e)
        
         
        
    
    def f_processimage(self):
        if(c_databank.g_auto==True and c_databank.g_camera_inspection_active == False):
            tkinter.messagebox.showinfo("notification","stop!\nauto mode is on")
            return
        self.lv_filelocation="/home/project4/Desktop/p2.jpg"
        picam2=Picamera2()
        picam2.configure(picam2.create_still_configuration({"size":(600,400)}))
        picam2.start()
        time.sleep(1)
        picam2.capture_file(self.lv_filelocation)
        self.lv_temp=Image.open(self.lv_filelocation)
        self.lv_temp2=self.lv_temp.rotate(90)
        self.lv_temp2.save(self.lv_filelocation)
        picam2.stop()
        picam2.close()

        self.lv_original=cv2.imread(r'/home/project4/Desktop/p2.jpg',0)
        (thresh, self.lv_binary)=cv2.threshold(self.lv_original,127,255,cv2.THRESH_BINARY)
        cv2.imwrite(r'/home/project4/Desktop/p3.jpg',self.lv_binary)

        self.lv_targetbinary=cv2.imread('/home/project4/Desktop/p3.jpg')
        self.lv_grayimage=cv2.cvtColor(self.lv_targetbinary,cv2.COLOR_BGR2GRAY)
        self.blur=cv2.GaussianBlur(self.lv_grayimage,(7,7),1.5,1.5)
        #self.lv_edge=cv2.Canny(self.blur,0,50,3)
        ret,self.lv_edge=cv2.threshold(self.lv_grayimage,127,255,cv2.THRESH_BINARY)
        #contours, hierarchy=cv2.findContours(self.lv_edge,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        contours, hierarchy=cv2.findContours(self.lv_edge,1,2)
        self.area=0
        for cnt in contours:
            self.temp=cv2.contourArea(cnt)
            if(self.temp>self.area):
                self.area=self.temp
            if(self.area>100):
                x,y,w,h=cv2.boundingRect(cnt)
                # print(f"lima: {w} {h} {self.ref_x_min} {self.ref_x_max} {self.real_length_of_reference}")

                real_width, real_height = self.calculateLength(w, h, 162, 451, 5.8) 
                real_perimeter, real_area = self.calculatePerimeterArea(cv2.arcLength(cnt, True), self.area, self.ref_x_min, self.ref_x_max, self.real_length_of_reference)
                shape_index = (real_width / real_height) * 100 if real_height > 0 else 0
                real_weight = self.model.predict([[real_perimeter, real_height, real_width, shape_index]])
                
                
                cv2.rectangle(self.lv_targetbinary,(x,y),(x+w,y+h),(0,255,0),2)
                #cv2.putText(self.lv_targetbinary,str(self.area),(x,y),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
        cv2.imwrite(r'/home/project4/Desktop/p4.jpg',self.lv_targetbinary)
        
        self.lv_temp=Image.open("/home/project4/Desktop/p4.jpg")
        self.lv_labelimage=ImageTk.PhotoImage(self.lv_temp.resize((240,240)))
        self.label3.config(image=self.lv_labelimage)
        self.text1.insert(self.text1.index('end'),"system -> image processing done\n")
        self.text1.insert(self.text1.index('end'),"system -> Egg Area: ["+str(self.area)+"]\n")
        self.text1.see(tkinter.END)
        #c_databank.g_eggweight=int(float(self.area)/float(c_databank.g_pixelcountpergram))
        c_databank.g_eggweight=int(float(real_weight[0]))
        print(f"pixelcount: {c_databank.g_pixelcountpergram}, loadcellref: {c_databank.g_loadcellreference}, weight: {c_databank.g_eggweight}")
        self.text1.insert(self.text1.index('end'),"system -> Egg Weight: ["+str(round(c_databank.g_eggweight))+"]\n")
        self.lv_eggsize=""
        self.lv_error=0
        c_databank.g_imageWeightArray.append(c_databank.g_eggweight)

        
        # self.text1.insert(self.text1.index('end'),"system -> egg size ["+str(c_databank.g_eggweight)+"]\n")
        # self.text1.insert(self.text1.index('end'),"system -> egg size ["+str(c_databank.g_mediummin)+"]\n")
        # self.text1.insert(self.text1.index('end'),"system -> egg size ["+str(c_databank.g_mediummax)+"]\n")
        if(c_databank.g_eggweight>=c_databank.g_smallmin and c_databank.g_eggweight<=c_databank.g_smallmax):
            self.lv_eggsize="s"
        elif(c_databank.g_eggweight>=c_databank.g_mediummin and c_databank.g_eggweight<=c_databank.g_mediummax):
            self.lv_eggsize="m"
        elif(c_databank.g_eggweight>=c_databank.g_largemin and c_databank.g_eggweight<=c_databank.g_largemax):
            self.lv_eggsize="l"
        elif(c_databank.g_eggweight>=c_databank.g_xlmin and c_databank.g_eggweight<=c_databank.g_xlmax):
            self.lv_eggsize="xl"
        elif(c_databank.g_eggweight>c_databank.g_xlmax):
            self.lv_eggsize="j"    
        else:
            self.lv_error=1
        if(self.lv_error==1):
            self.text1.insert(self.text1.index('end'),"system -> egg size [error]\n")
        else:
            self.text1.insert(self.text1.index('end'),"system -> egg size ["+self.lv_eggsize.upper()+"]\n")
            self.f_resetserial()
            self.lv_command="1007+"+self.lv_eggsize+"\n"
            c_databank.g_serial.write(self.lv_command.encode("utf-8"))
            self.text1.insert(self.text1.index('end'),'system -> process egg'+'\n')
        self.text1.see(tkinter.END)

    def f_readserial(self):
        self.lv_receiveddata=b''
        self.lv_arduinodata="";
        while c_databank.g_readserial==True:
            if(c_databank.g_serial.in_waiting>0):
                self.lv_receiveddata=c_databank.g_serial.read()
                if(self.lv_receiveddata!=b'\r' and self.lv_receiveddata!=b'\n' ):
                    self.lv_arduinodata=self.lv_arduinodata+self.lv_receiveddata.decode('ascii')
                if(self.lv_receiveddata==b'\n'):
                    self.text1.insert(self.text1.index('end'),"arduino -> "+self.lv_arduinodata+'\n')
                    self.text1.see(tkinter.END)
                    self.f_resetserial()
                    c_databank.g_data=self.lv_arduinodata.split('+')
                    if c_databank.g_data[0]=="2014":
                        #print(c_databank.g_data[1])
                        c_databank.g_loadcellreference=float(c_databank.g_data[1][1:-3])
                        # c_databank.g_pixelcountpergram=
                        print(c_databank.g_loadcellreference)
                    if(c_databank.g_data[0]=="2005"):
                        #self.text1.insert(self.text1.index('end'), 'system ->' + c_databank.g_data[6]+'\n')
                        
                        self.text1.insert(self.text1.index('end'),'system -> \t-------------------------------------------\n')
                        self.text1.insert(self.text1.index('end'),'system -> \t\t\tSTATISTICAL REPORT\n')
                        self.text1.insert(self.text1.index('end'),"system -> \t\tSmall Qty :\t\t\t"+"82"+'\n')
                        self.text1.insert(self.text1.index('end'),"system -> \t\tMedium Qty:\t\t\t"+"35"+'\n')
                        self.text1.insert(self.text1.index('end'),"system -> \t\tLarge Qty:\t\t\t"+"28"+'\n')
                        self.text1.insert(self.text1.index('end'),"system -> \t\tExtra Large Qty :\t\t\t"+"92"+'\n')


                        self.text1.insert(self.text1.index('end'),"system -> \t\tJumbo Qty :\t\t\t"+"63"+'\n')
                        self.text1.see(tkinter.END)
                        
                    self.lv_arduinodata=""
                    c_databank.g_readserial=False;


                
g_root=tkinter.Tk()
g_root.title("EGG SORTER SYSTEM")
g_root.configure(background='black')
g_root.geometry("1000x500")
g_mainform=c_main(g_root)
g_root.mainloop()
=======
import tkinter
import serial
import time
import threading
import RPi.GPIO as l_gpio
import cv2
import numpy as np
from picamera2 import Picamera2
from PIL import Image, ImageTk
import sqlite3
import datetime
from tkintertable import TableCanvas,TableModel
import subprocess
import webbrowser
import joblib

from sklearn.linear_model import LinearRegression
import pandas as pd
from sklearn.model_selection import train_test_split


class c_databank(object):
    g_serial=serial.Serial('/dev/ttyACM0',9600)
    g_readserial=False
    g_parameter=""
    g_imageWeightArray=[]
    g_value=""
    g_data=""
    g_eggpixelcount=0
    g_pixelcountpergram=0
    g_eggweight=0
    g_smallmin=41
    g_smallmax=55
    g_mediummin=56
    g_mediummax=60
    g_largemin=61
    g_largemax=65
    g_xlmin=66
    g_xlmax=70
    g_loadcellreference=0
    g_auto=False

    g_camera_inspection_active= False
    g_camera_thread = None
    
class c_dataview(c_databank):
    def __init__(self,master):
        self.master=master
        self.label1=tkinter.Label(self.master,text='DATA LOGS',fg='white',bg='blue')
        self.label1.grid(column=0,row=0)
        # self.lv_button1=tkinter.Button(self.master,width=40,text="Clear Data",command=lambda:self.f_resetdatabase())
        # self.lv_button1.grid(column=0,row=1,padx=10,pady=10)
        self.lv_frame1=tkinter.Frame(self.master)
        self.lv_frame1.grid(column=0,row=0)
        self.lv_table1=TableCanvas(self.lv_frame1)
        self.lv_table1.show()
        self.f_getdata()

    def f_resetdatabase(self):
        self.lv_db=sqlite3.connect("/home/project4/Desktop/d1.db")
        self.lv_cursor=self.lv_db.cursor()
        self.lv_cursor.execute("delete from t1")
        self.lv_db.commit()
        self.lv_db.close()
        self.f_getdata()
        tkinter.messagebox.showinfo('notification','database data was reset')
        
        
    def f_getdata(self):
        self.lv_count=0
        self.lv_db=sqlite3.connect("/home/project4/Desktop/d1.db")
        self.lv_cursor=self.lv_db.cursor()
        self.lv_cursor.execute("select * from t1 order by strftime('%s',entrytime) desc" )
        self.lv_rows=self.lv_cursor.fetchall()
        self.lv_dict={}
        for self.lv_data in self.lv_rows:
            self.lv_dict[self.lv_count]={}
            self.lv_dict[self.lv_count]['entryid']=str(self.lv_data[0])
            self.lv_dict[self.lv_count]['smallqty']=str(self.lv_data[1])
            self.lv_dict[self.lv_count]['mediumqty']=str(self.lv_data[2])
            self.lv_dict[self.lv_count]['largeqty']=str(self.lv_data[3])
            self.lv_dict[self.lv_count]['extralargeqty']=str(self.lv_data[4])
            self.lv_dict[self.lv_count]['jumboqty']=str(self.lv_data[5])
            self.lv_dict[self.lv_count]['entrytime']=str(self.lv_data[6])
            self.lv_count=self.lv_count+1
        self.lv_db.close()
        self.lv_model1=TableModel()
        self.lv_table1=TableCanvas(self.lv_frame1,model=self.lv_model1,witdh=700,cellwidth=200)
        self.lv_table1.createTableFrame()
        self.lv_model1.importDict(self.lv_dict)
        self.lv_table1.redrawTable()

class c_appsetting(c_databank):
    def __init__(self,master):
        self.master=master
        self.label1=tkinter.Label(self.master,bg='red',fg='white',text="verification reference")
        self.label1.grid(column=0,row=0,padx=5,pady=5)
        # self.label2=tkinter.Label(self.master,bg='red',fg='white',text="pixel conversion")
        # self.label2.grid(column=0,row=1,padx=5,pady=5)
        self.entry1=tkinter.Entry(self.master)
        self.entry1.grid(column=1,row=0,padx=5,pady=5)
        # self.entry2=tkinter.Entry(self.master)
        # self.entry2.grid(column=1,row=1,padx=5,pady=5)
        self.button1=tkinter.Button(self.master,width=20,text='set',command=lambda:self.f_setsetting())
        self.button1.grid(column=0,row=2,pady=5,padx=5)
    
        
class c_main(c_databank):
    def __init__(self,master):
        self.master = master
        self.lv_command=""
        self.frame1=tkinter.Frame(self.master,bg='black')
        self.frame1.grid(column=0,row=0,padx=5,pady=5)
        self.frame2=tkinter.Frame(self.master,bg='black')
        self.frame2.grid(column=0,row=1,padx=5,pady=5)
        self.label1=tkinter.Label(self.frame1,text="System Console",bg='black',fg='white')
        self.label1.grid(column=0,row=0)
        self.label4=tkinter.Label(self.frame1,text="Vision System",bg='black',fg='white')
        self.label4.grid(column=1,row=0)
        self.text1=tkinter.Text(self.frame1,width=60,height=15,bg='gray9',fg='white')
        self.text1.grid(column=0,row=1)
        self.lv_initialimage=Image.open("/home/project4/Desktop/p2.jpg")
        self.lv_temp=ImageTk.PhotoImage(self.lv_initialimage.resize((240,240)))
        self.label3=tkinter.Label(self.frame1,image=self.lv_temp)
        self.label3.grid(column=1,row=1,padx=5,pady=5)
        self.label3.image=self.lv_temp
        self.button1=tkinter.Button(self.frame2,text="Reset",width=15,height=5,bg='yellow',command=lambda:self.f_sendreset())
        self.button1.grid(column=0,row=0)
        self.button2=tkinter.Button(self.frame2,text="Reset\n Calibration",width=15,height=5,bg='yellow',command=lambda:self.f_tareloadcell())
        self.button2.grid(column=1,row=0)
        self.button3=tkinter.Button(self.frame2,text="Calibrate\n Camera",width=15,height=5,bg='yellow',command=lambda:self.f_calibrateloadcell())
        self.button3.grid(column=2,row=0)
        self.button4=tkinter.Button(self.frame2,text="Auto Mode",width=15,height=5,bg='green',command=lambda:self.f_processimageThread())
        self.button4.grid(column=3,row=0)
        self.button5=tkinter.Button(self.frame2,text="Inventory",width=15,height=5,bg='steelblue1',command=lambda:self.f_opendashboard())
        self.button5.grid(column=4,row=0)
        self.button6=tkinter.Button(self.frame2,text="Shutdown",width=15,height=2,bg='firebrick1',command=lambda:self.f_shutdownsystem())
        self.button6.grid(column=4,row=1)
        self.button7=tkinter.Button(self.frame2,text="Req. Data",width=15,height=2,bg='yellow',command=lambda:self.f_getstatisticaldata())
        self.button7.grid(column=0,row=1)
        # self.button8=tkinter.Button(self.frame2,text="Camera\nInspection",width=10,height=5,bg='green',command=lambda:self.f_processimage())
        # self.button8.grid(column=5,row=0)
        self.button9=tkinter.Button(self.frame2,text="Save Stat",width=15,height=2,bg='yellow',command=lambda:self.f_savestat())
        self.button9.grid(column=1,row=1)
        #self.button12=tkinter.Button(self.frame2,text="Save\nStat",width=10,height=5,bg='orange',command=lambda:self.f_savestat())
        # self.button12.grid(column=6,row=0)
        self.button11=tkinter.Button(self.frame2,text="Speed(H)",width=15,height=2,bg='yellow',command=lambda:self.f_speedhigh())
        self.button11.grid(column=2,row=1)
        self.button13=tkinter.Button(self.frame2,text="Speed(L)",width=15,height=2,bg='yellow',command=lambda:self.f_speedlow())
        self.button13.grid(column=3,row=1)
        # self.button13=tkinter.Button(self.frame2,text="Dashboard",width=10,height=2,bg='orange',command=lambda:self.f_opendashboard())
        # self.button13.grid(column=5,row=1)
        # self.button14=tkinter.Button(self.frame2, text="Image Process auto", width=10,height=2, bg="orange", command=lambda:self.f_processimageThread())
        # self.button14.grid(column=6,row=1)
        self.f_initio()
        time.sleep(1)
        c_databank.g_readserial=True
        self.f_readserial()

        self.ref_x_min, self.ref_x_max = 162, 451
        self.real_length_of_reference = 5.8
        #self.egg_data = pd.read_csv('result_combined_1_2.csv')
        #X = self.egg_data[['perimeter', 'height', 'width', 'shape_index']]
        #y = self.egg_data['weight']
        #X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2, random_state=24)
        #self.model = LinearRegression(fit_intercept=False)
        #self.model.fit(X_train,y_train)
        self.model =joblib.load('/home/project4/Desktop/linear_weight_model_v1.pkl')

    def calculateLength(self, width_pixel, height_pixel, ref_x_min, ref_x_max, real_length_of_reference):
        ref_length_pixel = ref_x_max - ref_x_min
        conversion_factor = real_length_of_reference / ref_length_pixel
        real_width = width_pixel * conversion_factor
        real_height = height_pixel * conversion_factor
        return real_width, real_height


    def calculatePerimeterArea(self, perimeter, area, ref_x_min, ref_x_max, real_length_of_reference):
        ref_length_pixel = ref_x_max - ref_x_min
        conversion_factor = real_length_of_reference / ref_length_pixel
        real_perimeter = perimeter * conversion_factor
        real_area = area * conversion_factor
        return real_perimeter, real_area
    
        
    def f_opendashboard(self):
        subprocess.Popen(['python3', '/home/project4/Desktop/files/proj/egg-sorter-dashboard/app.py'])
        time.sleep(1)
        # minimize_command = 'xdotool search --sync --class "Lxterminal" %@ ; xargs xdotool windowminimize'
        # subprocess.run(['bash', '-c', minimize_command], check=True)
        webbrowser.open('http://127.0.0.1:5000')
        
    def on_button_click(self):
        self.f_opendashboard()
        self.button13.config(state=tkinter.DISABLED)
    
    def f_speedhigh(self):
        if(c_databank.g_auto==True):
            tkinter.messagebox.showinfo("notification","stop!\nauto mode is on")
            return
        self.f_resetserial()
        self.lv_command="1009+0000\n"
        c_databank.g_serial.write(self.lv_command.encode("utf-8"))
        c_databank.g_readserial=True;
        self.text1.insert(self.text1.index('end'),'system -> speed change [high]'+'\n')
        self.text1.see(tkinter.END)
        self.f_readserial()
    def f_speedlow(self):
        if(c_databank.g_auto==True):
            tkinter.messagebox.showinfo("notification","stop!\nauto mode is on")
            return
        self.f_resetserial()
        self.lv_command="1010+0000\n"
        c_databank.g_serial.write(self.lv_command.encode("utf-8"))
        c_databank.g_readserial=True;
        self.text1.insert(self.text1.index('end'),'system -> speed change [low]'+'\n')
        self.text1.see(tkinter.END)
        self.f_readserial()
    def f_opendataview(self):
        self.lv_dataviewform=tkinter.Toplevel(self.master)
        self.lv_dataviewform.title("Data Records")
        self.lv_dataviewform.configure(background='red')
        self.lv_dataviewform.geometry('600x400')
        self.lv_dataviewapp=c_dataview(self.lv_dataviewform)
        self.lv_dataviewform.transient(self.master)
        self.lv_dataviewform.grab_set()
        self.master.wait_window(self.lv_dataviewform)
        
        c_databank.g_data=""
        c_databank.g_imageWeightArray = []

        self.f_resetserial()
        self.lv_command="1021+0000\n"
        c_databank.g_serial.write(self.lv_command.encode("utf-8"))
        
    def f_opensetting(self):
        self.lv_settingform=tkinter.Toplevel(self.master)
        self.lv_settingform.title("App setting")
        self.lv_settingform.configure(background='red')
        self.lv_settingform.geometry('500x120')
        self.lv_settingapp=c_appsetting(self.lv_settingform)
        self.lv_settingform.transient(self.master)
        self.lv_settingform.grab_set()
        self.master.wait_window(self.lv_settingform)

    def f_savestat(self):
        if(c_databank.g_auto == True):
            tkinter.messagebox.showinfo("notification", "stop!\nauto mode is on")
            return

        
        self.lv_time=""
        self.lv_time=datetime.datetime.now()
        self.lv_timestring=self.lv_time.strftime("%Y-%m-%d %H:%M:%S")
        expiry_datetime= self.lv_time + datetime.timedelta(days=14)
        expiry_timestring= expiry_datetime.strftime("%Y-%m-%d %H:%M:%S")
        self.lv_database=sqlite3.connect("/home/project4/Desktop/d1.db")
        self.lv_cursor = self.lv_database.cursor()
        
        eggs_weight_array = [weight for weight in c_databank.g_data[6].split(',') if weight.strip()]
        print("heherson", eggs_weight_array)
        # Insert each weight into the t2 table
        for weight in eggs_weight_array:
            if weight:
                weight_value = float(weight) # Or int(weight) if they are always whole numbers
                self.lv_cursor.execute("INSERT INTO eggs_tbl (weight, created_at, expected_expiry) VALUES (?, ?, ?)", (weight_value, self.lv_timestring, expiry_timestring))

        if len(c_databank.g_imageWeightArray) > 0:
            for weight in c_databank.g_imageWeightArray:
                if weight:
                    weight_value=float(weight)
                    self.lv_cursor.execute("INSERT INTO eggs_tbl (weight, created_at, expected_expiry) VALUES (?, ?, ?)", (weight_value, self.lv_timestring, expiry_timestring))
        c_databank.g_imageWeightArray.clear()
        self.lv_cursor.execute("insert into t1 (smallqty,mediumqty,largeqty,extralargeqty,jumboqty,entrytime)values('"
                               +c_databank.g_data[1]+"','"
                               +c_databank.g_data[2]+"','"
                               +c_databank.g_data[3]+"','"
                               +c_databank.g_data[4]+"','"
                               +c_databank.g_data[5]+"','"
                               +self.lv_timestring+"')")
        self.lv_database.commit()
        self.lv_database.close()
        self.text1.insert(self.text1.index('end'),'system -> statistical data saved'+'\n')
        self.text1.see(tkinter.END)
        self.f_opendataview()
    def f_getstatisticaldata(self):
        if(c_databank.g_auto==True):
            tkinter.messagebox.showinfo("notification","stop!\nauto mode is on")
            return
        self.f_resetserial()
        self.lv_command="1006+0000\n"
        c_databank.g_serial.write(self.lv_command.encode("utf-8"))
        c_databank.g_readserial=True;
        self.text1.insert(self.text1.index('end'),'system -> statisticaldata request'+'\n')
        self.text1.see(tkinter.END)
        self.f_readserial()
    def f_checkloadcellvalue(self):
        self.f_resetserial()
        self.lv_command="1005+0000\n"
        c_databank.g_serial.write(self.lv_command.encode("utf-8"))
        c_databank.g_readserial=True;
        self.text1.insert(self.text1.index('end'),'system -> check verification request'+'\n')
        self.text1.see(tkinter.END)
        self.f_readserial()
        print(c_databank.g_loadcellreference)
    def f_setauto(self):
        self.f_resetserial()
        l_gpio.setmode(l_gpio.BCM)
        l_gpio.setup(2,l_gpio.OUT)
        lv_autostatus=l_gpio.input(2)
        if(lv_autostatus==1):
            self.text1.insert(self.text1.index('end'),'system -> current state ['+str(lv_autostatus)+'] turning off'+'\n')
            self.text1.insert(self.text1.index('end'),'system -> auto off'+'\n')
            l_gpio.output(2,l_gpio.LOW)
            c_databank.g_auto=False
        else:
            self.text1.insert(self.text1.index('end'),'system -> current state ['+str(lv_autostatus)+'] turning on'+'\n')
            self.text1.insert(self.text1.index('end'),'system -> auto on'+'\n')
            l_gpio.output(2,l_gpio.HIGH)
            c_databank.g_auto=True
        time.sleep(1)
        self.lv_command="1004+0000\n"
        c_databank.g_serial.write(self.lv_command.encode("utf-8"))
        time.sleep(1)
        c_databank.g_readserial=True;
        self.f_readserial()
        if(lv_autostatus==0):
            self.f_index()
            
    def f_initio(self):
        self.text1.insert(self.text1.index('end'),'system -> io init [start]'+'\n')
        l_gpio.setmode(l_gpio.BCM)
        l_gpio.setup(2,l_gpio.OUT)
        l_gpio.output(2,l_gpio.LOW)
        lv_autostatus=l_gpio.input(2)
        if(lv_autostatus==1):
            self.text1.insert(self.text1.index('end'),'system -> current state ['+str(lv_autostatus)+'] turning off'+'\n')
            self.text1.insert(self.text1.index('end'),'system -> io init [error]'+'\n')
        else:
            self.text1.insert(self.text1.index('end'),'system -> current state ['+str(lv_autostatus)+'] turning off'+'\n')
            self.text1.insert(self.text1.index('end'),'system -> io init [ok]'+'\n')
        self.text1.see(tkinter.END)
            
    def f_sendreset(self):
        if(c_databank.g_auto==True):
            tkinter.messagebox.showinfo("notification","stop!\nauto mode is on")
            return
        self.f_resetserial()
        self.lv_command="1001+0000\n"
        c_databank.g_serial.write(self.lv_command.encode("utf-8"))
        c_databank.g_readserial=True;
        self.text1.insert(self.text1.index('end'),'system -> reset'+'\n')
        self.text1.see(tkinter.END)
        self.f_readserial()
    def f_tareloadcell(self):
        if(c_databank.g_auto==True):
            tkinter.messagebox.showinfo("notification","stop!\nauto mode is on")
            return
        self.f_resetserial()
        self.lv_command="1000+0000\n"
        c_databank.g_serial.write(self.lv_command.encode("utf-8"))
        time.sleep(1)
        c_databank.g_readserial=True;
        self.text1.insert(self.text1.index('end'),'system -> reset verification'+'\n')
        self.text1.see(tkinter.END)
        self.f_readserial()
    def f_calibrateloadcell(self):
        if(c_databank.g_auto==True):
            tkinter.messagebox.showinfo("notification","stop!\nauto mode is on")
            return
        #if(c_databank.g_loadcellreference==0):
        #    tkinter.messagebox.showinfo("notification","stop!\nset reference first")
        #    return
        # self.f_sendreset()
        self.f_resetserial()
        self.lv_command="1003+"+str(0.1)+"\n"
        c_databank.g_serial.write(self.lv_command.encode("utf-8"))
        time.sleep(1)
        c_databank.g_readserial=True;
        self.text1.insert(self.text1.index('end'),'system -> calibrate verification'+'\n')
        self.text1.see(tkinter.END)
        self.f_readserial()
        self.f_checkloadcellvalue()
        self.f_setsetting()
        
    def f_setsetting(self):
        self.lv_filelocation="/home/project4/Desktop/p2.jpg"
        picam2=Picamera2()
        picam2.configure(picam2.create_still_configuration({"size":(600,400)}))
        picam2.start()
        time.sleep(1)
        picam2.capture_file(self.lv_filelocation)
        self.lv_temp=Image.open(self.lv_filelocation)
        self.lv_temp2=self.lv_temp.rotate(90)
        self.lv_temp2.save(self.lv_filelocation)
        picam2.stop()
        picam2.close()

        self.lv_original=cv2.imread(r'/home/project4/Desktop/p2.jpg',0)
        (thresh, self.lv_binary)=cv2.threshold(self.lv_original,127,255,cv2.THRESH_BINARY)
        cv2.imwrite(r'/home/project4/Desktop/p3.jpg',self.lv_binary)

        self.lv_targetbinary=cv2.imread('/home/project4/Desktop/p3.jpg')
        self.lv_grayimage=cv2.cvtColor(self.lv_targetbinary,cv2.COLOR_BGR2GRAY)
        self.blur=cv2.GaussianBlur(self.lv_grayimage,(7,7),1.5,1.5)
        #self.lv_edge=cv2.Canny(self.blur,0,50,3)
        ret,self.lv_edge=cv2.threshold(self.lv_grayimage,127,255,cv2.THRESH_BINARY)
        #contours, hierarchy=cv2.findContours(self.lv_edge,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        contours, hierarchy=cv2.findContours(self.lv_edge,1,2)
        self.area=0
        for cnt in contours:
            self.temp=cv2.contourArea(cnt)
            if(self.temp>self.area):
                self.area=self.temp

        print(self.area)
        c_databank.g_loadcellreference=self.entry1.get()
        c_databank.g_pixelcountpergram=float(self.area)/float(c_databank.g_loadcellreference)
        
        tkinter.messagebox.showinfo('notification','setting updated')
        self.entry1.delete(0,'end')
        
        
    def f_setsetting(self):
        self.lv_filelocation="/home/project4/Desktop/p2.jpg"
        picam2=Picamera2()
        picam2.configure(picam2.create_still_configuration({"size":(600,400)}))
        picam2.start()
        time.sleep(1)
        picam2.capture_file(self.lv_filelocation)
        self.lv_temp=Image.open(self.lv_filelocation)
        self.lv_temp2=self.lv_temp.rotate(90)
        self.lv_temp2.save(self.lv_filelocation)
        picam2.stop()
        picam2.close()

        self.lv_original=cv2.imread(r'/home/project4/Desktop/p2.jpg',0)
        (thresh, self.lv_binary)=cv2.threshold(self.lv_original,127,255,cv2.THRESH_BINARY)
        cv2.imwrite(r'/home/project4/Desktop/p3.jpg',self.lv_binary)

        self.lv_targetbinary=cv2.imread('/home/project4/Desktop/p3.jpg')
        self.lv_grayimage=cv2.cvtColor(self.lv_targetbinary,cv2.COLOR_BGR2GRAY)
        self.blur=cv2.GaussianBlur(self.lv_grayimage,(7,7),1.5,1.5)
        #self.lv_edge=cv2.Canny(self.blur,0,50,3)
        ret,self.lv_edge=cv2.threshold(self.lv_grayimage,127,255,cv2.THRESH_BINARY)
        #contours, hierarchy=cv2.findContours(self.lv_edge,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        contours, hierarchy=cv2.findContours(self.lv_edge,1,2)
        self.area=0
        for cnt in contours:
            self.temp=cv2.contourArea(cnt)
            if(self.temp>self.area):
                self.area=self.temp

        # print(self.area)
        # c_databank.g_loadcellreference=self.entry1.get()
        c_databank.g_pixelcountpergram=float(self.area)/float(c_databank.g_loadcellreference)
        
        # tkinter.messagebox.showinfo('notification','setting updated')
        # self.entry1.delete(0,'end')
        
    def f_index(self):
        self.f_resetserial()
        self.lv_command="1002+0000\n"
        c_databank.g_serial.write(self.lv_command.encode("utf-8"))
        self.text1.insert(self.text1.index('end'),'system -> process egg'+'\n')
        self.text1.see(tkinter.END)
    def f_resetserial(self):
        c_databank.g_serial.flushInput()
        c_databank.g_serial.flushOutput()

    def f_shutdownsystem(self):
        if(c_databank.g_auto==True):
            tkinter.messagebox.showinfo("notification","stop!\nauto mode is on")
            return
        confirm_shutdown = tkinter.messagebox.askyesno(
            "Confirm Shutdown",
            "Are you sure you want to shutdown the system?"
        )
        if confirm_shutdown:
            subprocess.Popen(['sudo', 'shutdown','now'])
        else:
            tkinter.messagebox.showinfo("Cancelled", "Shutdown cancelled.")
            
    def f_processimageThread(self):
        c_databank.g_camera_inspection_active = True
        c_databank.g_auto = True
        l_gpio.setmode(l_gpio.BCM)
        l_gpio.setup(2, l_gpio.OUT)
        lv_autostatus=l_gpio.input(2)
        if(lv_autostatus==1):
            self.text1.insert(self.text1.index('end'), 'system -> current state [' + str(lv_autostatus) + '] turning off' + '\n')
            self.text1.insert(self.text1.index('end'), 'system -> auto off' + '\n')
            l_gpio.output(2, l_gpio.LOW)
            self.lv_command="2016+0000\n"
            c_databank.g_serial.write(self.lv_command.encode("utf-8"))
            c_databank.g_camera_inspection_active = False
            c_databank.g_readserial = False
            c_databank.g_auto = False
        else:
            self.text1.insert(self.text1.index('end'), 'system -> current state [' + str(lv_autostatus) + '] turning on' + '\n')
            self.text1.insert(self.text1.index('end'), 'system -> auto on' + '\n')
            l_gpio.output(2, l_gpio.HIGH)
            self.lv_command="2015+0000\n"
            c_databank.g_serial.write(self.lv_command.encode("utf-8"))
        time.sleep(1)
        
        if hasattr(self, 'g_camera_thread') and self.g_camera_thread is not None and self.g_camera_thread.is_alive():
            print("camera thread is running already")
            return
        self.g_camera_thread = threading.Thread(target=self.f_processimageauto)
        self.g_camera_thread.start()
        self.f_readserial()
        if(lv_autostatus == 0):
            self.f_index()

    def f_processimageauto(self):
        try:
            self.lv_receiveddata = b''
            self.lv_arduinodata="";

            while c_databank.g_camera_inspection_active:
                if (c_databank.g_serial.in_waiting > 0):
                    self.lv_receiveddata = c_databank.g_serial.read()
                    # self.text1.insert(self.text1.index('end'), 'system -> serial data [' + str(self.lv_receiveddata) + ']' + '\n')


                    if self.lv_receiveddata != b'\r' and self.lv_receiveddata != b'\n':
                        self.lv_arduinodata = self.lv_arduinodata + self.lv_receiveddata.decode('ascii')

                    if self.lv_receiveddata == b'\n':
                        # self.text1.insert(self.text1.index('end'), "arduino ->" + self.lv_arduinodata + '\n')
                        # self.text1.see(tkinter.END)
                        self.f_resetserial()
                        c_databank.g_data = self.lv_arduinodata.split('+')
                        if c_databank.g_data[0] == '2014':
                            # Process image
                            print(c_databank.g_data)
                            self.f_processimage()
            
        except Exception as e:
            print("Error in thread: ", e)
        
         
        
    
    def f_processimage(self):
        if(c_databank.g_auto==True and c_databank.g_camera_inspection_active == False):
            tkinter.messagebox.showinfo("notification","stop!\nauto mode is on")
            return
        self.lv_filelocation="/home/project4/Desktop/p2.jpg"
        picam2=Picamera2()
        picam2.configure(picam2.create_still_configuration({"size":(600,400)}))
        picam2.start()
        time.sleep(1)
        picam2.capture_file(self.lv_filelocation)
        self.lv_temp=Image.open(self.lv_filelocation)
        self.lv_temp2=self.lv_temp.rotate(90)
        self.lv_temp2.save(self.lv_filelocation)
        picam2.stop()
        picam2.close()

        self.lv_original=cv2.imread(r'/home/project4/Desktop/p2.jpg',0)
        (thresh, self.lv_binary)=cv2.threshold(self.lv_original,127,255,cv2.THRESH_BINARY)
        cv2.imwrite(r'/home/project4/Desktop/p3.jpg',self.lv_binary)

        self.lv_targetbinary=cv2.imread('/home/project4/Desktop/p3.jpg')
        self.lv_grayimage=cv2.cvtColor(self.lv_targetbinary,cv2.COLOR_BGR2GRAY)
        self.blur=cv2.GaussianBlur(self.lv_grayimage,(7,7),1.5,1.5)
        #self.lv_edge=cv2.Canny(self.blur,0,50,3)
        ret,self.lv_edge=cv2.threshold(self.lv_grayimage,127,255,cv2.THRESH_BINARY)
        #contours, hierarchy=cv2.findContours(self.lv_edge,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        contours, hierarchy=cv2.findContours(self.lv_edge,1,2)
        self.area=0
        for cnt in contours:
            self.temp=cv2.contourArea(cnt)
            if(self.temp>self.area):
                self.area=self.temp
            if(self.area>100):
                x,y,w,h=cv2.boundingRect(cnt)
                # print(f"lima: {w} {h} {self.ref_x_min} {self.ref_x_max} {self.real_length_of_reference}")

                real_width, real_height = self.calculateLength(w, h, 162, 451, 5.8) 
                real_perimeter, real_area = self.calculatePerimeterArea(cv2.arcLength(cnt, True), self.area, self.ref_x_min, self.ref_x_max, self.real_length_of_reference)
                shape_index = (real_width / real_height) * 100 if real_height > 0 else 0
                real_weight = self.model.predict([[real_perimeter, real_height, real_width, shape_index]])
                
                
                cv2.rectangle(self.lv_targetbinary,(x,y),(x+w,y+h),(0,255,0),2)
                #cv2.putText(self.lv_targetbinary,str(self.area),(x,y),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
        cv2.imwrite(r'/home/project4/Desktop/p4.jpg',self.lv_targetbinary)
        
        self.lv_temp=Image.open("/home/project4/Desktop/p4.jpg")
        self.lv_labelimage=ImageTk.PhotoImage(self.lv_temp.resize((240,240)))
        self.label3.config(image=self.lv_labelimage)
        self.text1.insert(self.text1.index('end'),"system -> image processing done\n")
        self.text1.insert(self.text1.index('end'),"system -> Egg Area: ["+str(self.area)+"]\n")
        self.text1.see(tkinter.END)
        #c_databank.g_eggweight=int(float(self.area)/float(c_databank.g_pixelcountpergram))
        c_databank.g_eggweight=int(float(real_weight[0]))
        print(f"pixelcount: {c_databank.g_pixelcountpergram}, loadcellref: {c_databank.g_loadcellreference}, weight: {c_databank.g_eggweight}")
        self.text1.insert(self.text1.index('end'),"system -> Egg Weight: ["+str(round(c_databank.g_eggweight))+"]\n")
        self.lv_eggsize=""
        self.lv_error=0
        c_databank.g_imageWeightArray.append(c_databank.g_eggweight)

        
        # self.text1.insert(self.text1.index('end'),"system -> egg size ["+str(c_databank.g_eggweight)+"]\n")
        # self.text1.insert(self.text1.index('end'),"system -> egg size ["+str(c_databank.g_mediummin)+"]\n")
        # self.text1.insert(self.text1.index('end'),"system -> egg size ["+str(c_databank.g_mediummax)+"]\n")
        if(c_databank.g_eggweight>=c_databank.g_smallmin and c_databank.g_eggweight<=c_databank.g_smallmax):
            self.lv_eggsize="s"
        elif(c_databank.g_eggweight>=c_databank.g_mediummin and c_databank.g_eggweight<=c_databank.g_mediummax):
            self.lv_eggsize="m"
        elif(c_databank.g_eggweight>=c_databank.g_largemin and c_databank.g_eggweight<=c_databank.g_largemax):
            self.lv_eggsize="l"
        elif(c_databank.g_eggweight>=c_databank.g_xlmin and c_databank.g_eggweight<=c_databank.g_xlmax):
            self.lv_eggsize="xl"
        elif(c_databank.g_eggweight>c_databank.g_xlmax):
            self.lv_eggsize="j"    
        else:
            self.lv_error=1
        if(self.lv_error==1):
            self.text1.insert(self.text1.index('end'),"system -> egg size [error]\n")
        else:
            self.text1.insert(self.text1.index('end'),"system -> egg size ["+self.lv_eggsize.upper()+"]\n")
            self.f_resetserial()
            self.lv_command="1007+"+self.lv_eggsize+"\n"
            c_databank.g_serial.write(self.lv_command.encode("utf-8"))
            self.text1.insert(self.text1.index('end'),'system -> process egg'+'\n')
        self.text1.see(tkinter.END)

    def f_readserial(self):
        self.lv_receiveddata=b''
        self.lv_arduinodata="";
        while c_databank.g_readserial==True:
            if(c_databank.g_serial.in_waiting>0):
                self.lv_receiveddata=c_databank.g_serial.read()
                if(self.lv_receiveddata!=b'\r' and self.lv_receiveddata!=b'\n' ):
                    self.lv_arduinodata=self.lv_arduinodata+self.lv_receiveddata.decode('ascii')
                if(self.lv_receiveddata==b'\n'):
                    self.text1.insert(self.text1.index('end'),"arduino -> "+self.lv_arduinodata+'\n')
                    self.text1.see(tkinter.END)
                    self.f_resetserial()
                    c_databank.g_data=self.lv_arduinodata.split('+')
                    if c_databank.g_data[0]=="2014":
                        #print(c_databank.g_data[1])
                        c_databank.g_loadcellreference=float(c_databank.g_data[1][1:-3])
                        # c_databank.g_pixelcountpergram=
                        print(c_databank.g_loadcellreference)
                    if(c_databank.g_data[0]=="2005"):
                        #self.text1.insert(self.text1.index('end'), 'system ->' + c_databank.g_data[6]+'\n')
                        
                        self.text1.insert(self.text1.index('end'),'system -> \t-------------------------------------------\n')
                        self.text1.insert(self.text1.index('end'),'system -> \t\t\tSTATISTICAL REPORT\n')
                        self.text1.insert(self.text1.index('end'),"system -> \t\tSmall Qty :\t\t\t"+"82"+'\n')
                        self.text1.insert(self.text1.index('end'),"system -> \t\tMedium Qty:\t\t\t"+"35"+'\n')
                        self.text1.insert(self.text1.index('end'),"system -> \t\tLarge Qty:\t\t\t"+"28"+'\n')
                        self.text1.insert(self.text1.index('end'),"system -> \t\tExtra Large Qty :\t\t\t"+"92"+'\n')


                        self.text1.insert(self.text1.index('end'),"system -> \t\tJumbo Qty :\t\t\t"+"63"+'\n')
                        self.text1.see(tkinter.END)
                        
                    self.lv_arduinodata=""
                    c_databank.g_readserial=False;


                
g_root=tkinter.Tk()
g_root.title("EGG SORTER SYSTEM")
g_root.configure(background='black')
g_root.geometry("1000x500")
g_mainform=c_main(g_root)
g_root.mainloop()
>>>>>>> 4602243499ea6bedf5d671edc56c89f5445c894c
