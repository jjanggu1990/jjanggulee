# -*- coding: utf-8 -*-
from Tkinter import *
import cv2
import time
import MySQLdb
import  smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.header import Header
from email import Encoders
import RPi.GPIO as gp
import threading as th
app=Tk()
app.title("ubi-eye")
app.geometry('200x250+200+100')
value=StringVar()
value.set(None);
path = "/var/www/";
fps = 10.0;
resolution =(640,480)
home_ip = 'http://10.17.1.7/'
try :
    conn = MySQLdb.connect(host = 'localhost',user='root', passwd ='1111',db ='db')
    cursor = conn.cursor()
except:
    print("db 실패")
gp.setmode(gp.BCM)
#pir num_7
#detect 1
#non detect 0
gp.setup(7,gp.IN)
#switch num_2
#push 0
#non push 1
gp.setup(2,gp.IN)
switch_state =1
pir_statet =0

#웹캠 제어권 global
cap = None;
#웹캠 동작여부 , bool
ret = None;
#이미지
frame = None;
#프로그램 동작 여부 , bool , 기본값 False
condition = False;
ret, frame = None, None;

lb_text = StringVar()
lb_text.set("not running!")
lb_detect = StringVar()
lb_detect.set("");

def save_button():
    print("aaa");

def cancel_click():
    """
    app1 = Tk();
    
    c = Button(app1, text="click",width = 15, command = call_button);
    c.pack();
    app1.mainloop();
    """
    print(str(value))

record_thread = None;
def my_th():
    global condition
    global switch_state
    global pir_state
    global record_thread
    text_moving=["stand by","stand by.","stand by..","stand by...","stand by...."]
   
    #pir num_7
    #detect 1
    #non detect 0

    #switch num_2
    #push 0
    #non push 1

    #pir and switch
    '''
    while condition:
        switch_statet = gp.input(2)
        pir_state = gp.input(7)
        if switch_state ==1 && pir_state ==0:
            print "0"
            
        else :
            print "1"
            record_btn();
        time.sleep(0.1);
    '''
    #only switch
    moving_num =0;
    while True :
        if condition == True:
            while condition:
                switch_state = gp.input(2)
                #pir_state = gp.input(7)
                if switch_state ==1:
                    #print "0"
                    #sys.stdout.write("0")
                    lb_detect.set(text_moving[moving_num]);
                    moving_num += 1;
                    if moving_num ==5 :
                        moving_num=0;
                    
                else :
                    lb_detect.set("Motion Detect!!");
                    print "motion detect!!"
                    condition = False;
                    
                    #record_btn();
                    
                    
                    
                time.sleep(0.1);
        
        else :
            time.sleep(0.5);
        record_thread = th.Thread(target = record_btn);
        record_thread.start()
        record_thread.join();

mythread = None;


def toggle_text():
    #버튼 글자에 따른 실행 함수 변경
    global bt_start
    global cap;
    global condition;
    global bt_start;
    global ret,frame;
    
    if bt_start["text"] == "start":
        # start일때는 stop으로 변경
        start();

    else:
        # stop인 경우 start로 변
        bt_start["text"] = "start"
        stop();
        


def start():
    print("start");
    global cap;
    global condition;
    global bt_start;
    global ret,frame;
    global lb_text;   
    global mythread
    cap = cv2.VideoCapture(0)
    if cap.isOpened() == True:
        condition = True;
        lb_text.set("running!")
        bt_start["text"] = "stop"
        print("success");
        mythread = th.Thread(target = my_th)
        mythread.start()
        
    else :
        print("fail");
"""    
    while(cap.isOpened()):
        
        ret, frame = cap.read()
        
        if ret == True:
            #두번째 파라미터에 0을 입력하면 뒤집어서 출력됨
            frame = cv2.flip(frame, 1)

            #화면에 보여줌
            cv2.imshow('frame',frame)

            #종료 키 설정
            if condition == False:
                break
        else:
            print("error")
            break
 """   

    

def stop():
    global condition;
    global cap;
    global lb_text;
    global lb_detect
    lb_detect.set("");
    condition = False
    cap.release()
    cv2.destroyAllWindows()
    print(cap.isOpened())
    lb_text.set("not running!")
    print("stop");

def stream():
    global cap
    global ret, frame
    global condition
    condition = False;
    while(cap.isOpened()):
        
        ret, frame = cap.read()
        
        if ret == True:
            #두번째 파라미터에 0을 입력하면 뒤집어서 출력됨
            frame = cv2.flip(frame, 1)

            #cv2.imwrite(path+"test1.jpg",frame)
            #화면에 보여줌
            cv2.imshow('frame',frame)
            
            

            #종료 키 설정
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                condition = True
                
                break
            
            
            """
            if condition == False:
                break
            """
        else:
            print("error")
            break
    cv2.destroyAllWindows()

def record_btn():
    global cursor
    global cap
    global path
    global home_ip
    global condition
    
    
    print("record")
    
    #send_gmail();
    #웹캠의 핸들을 가져옴
#    cap = cv2.VideoCapture(0)
    #비디오 포맷 설정
    #fourcc = cv2.VideoWriter_fourcc(*'IYUV')
    fourcc = cv2.VideoWriter_fourcc(*'H264')
    #비디오 파일 생성
    filename = time.strftime("%y_%m_%d_%H_%M",time.localtime());
    out = cv2.VideoWriter(path+filename+'.avi',fourcc, fps, resolution)
    out2 = cv2.VideoWriter(path+'test1.avi',fourcc, fps, resolution)
    cursor.execute('''insert into test (list) values("'''+filename+'''.avi")''')
    cursor.execute('commit')
    #스트림 루프
    count=time.time()
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            time_count = time.time()-count
            #두번째 파라미터에 0을 입력하면 뒤집어서 출력됨
          #  out.write(frame)
          #  out2.write(frame)
          #  gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            frame = cv2.flip(frame, 1)
            #동영상저장
            out.write(frame)
            out2.write(frame)
            
            #화면에 보여줌
            #cv2.imshow('frame',frame)

            #종료 키 설정
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if (time_count) >= 10 :
                out.release()
                break
            if (time_count) >= 7:
                out2.release()
                pass
            
        else:
            print("error")
            break
        
#웹캠 제어권 해제
#    cap.release()
#동영상 저장 종료
    out.release()
    
    cv2.destroyAllWindows()
    #html 파일 수정 하는 코드
    u = open('/var/www/index.html','w')
    cursor.execute('select list from test order by list DESC')
    row = cursor.fetchall()
    #html 태그 추가
    u.write('<html>\n<body>\n')
    #스트리밍 동영상 태그 추가
    u.write('''<a href="'''+home_ip)
    #href 부분에 파일 이름
    u.write('test1.avi');
    u.write('">');
    #태그 안에 파일 이름
    u.write('test1.avi');
    u.write('''</a>\n''')
    u.write('''<br>''')

    for i in range (len(row)):
        tmp = str(row[i])[2:20];
        u.write('''<a href="'''+home_ip)
        u.write(tmp);
        u.write('">');
        u.write(tmp);
        u.write('''</a>\n''')
        u.write('''<br>''')
    u.write('</body>\n</html>\n')
        
    u.close()
    condition = True;

def send_gmail():
    gmail_username="ub-eye"
    gmail_user="fksh90@gmail.com"
    gmail_pwd="q131313!#"
    to = "jjanggu1990@gmail.com"
    #attach_file="첨부파일 있을 경우 파일명"
    msg=MIMEMultipart('alternative')
    msg['From']=gmail_username
    msg['To']=to
    msg['Subject']=Header("동작 감지!!제목",'utf-8') # 제목 인코딩
    msg.attach(MIMEText("동작 감지!!내용", 'plain', 'utf-8')) # 내용 인코딩
    #msg.attach(MIMEText(html, 'html', 'utf-8')) # 내용 인코딩 2
    
    # 아래 코드는 첨부파일이 있을 경우에만 주석처리 빼시면 됩니다.
    #part=MIMEBase('application','octet-stream')
    #part.set_payload(open(attach, 'rb').read())
    #Encoders.encode_base64(part)
    #part.add_header('Content-Disposition','attachment; filename="%s"' % os.path.basename(attach))
    #msg.attach(part)
    
    mailServer=smtplib.SMTP("smtp.gmail.com",587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmail_user,gmail_pwd)
    mailServer.sendmail(gmail_user, to, msg.as_string())
    mailServer.close()
    print 'mail send'
    


lb_condition = Label(app,textvariable=lb_text)
bt_start= Button(app,text="start", width=15, command=toggle_text)
bt_stream = Button(app, text="stream", width=15, command = stream)
bt_record= Button(app,text="record", width=15, command=record_btn)
#bt_option= Button(app,text="option", width=15, command=option_btn)
lb_detecting = Label(app,textvariable=lb_detect)
lb_condition.pack(padx=10,pady=10)
bt_start.pack(padx=10, pady=10)
bt_stream.pack(padx= 10, pady =10)
bt_record.pack(padx=10, pady=10)
lb_detecting.pack(padx=10,pady=10)
#bt_option.pack(padx=10, pady=10)
app.mainloop()
