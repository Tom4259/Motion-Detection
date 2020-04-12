#import things to get terminal to run things:
import time
import datetime
import os
import sys
import threading
#import GPIO hardware:
import RPi.GPIO as GPIO
sys.path.append('/home/pi/lcd/')
import lcddriver
#import modules to send email:
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
#imports modules to give warnings/coloured outputs:
import logging
#imports module to take picture:
from picamera import PiCamera



camera = PiCamera()
#camera.rotation = 180
camera.framerate = 5

FILE = '<FILE_TO_STOP_SCRIPT>'
PAUSE_FILE = '<FILE_TO_PAUSE_SCRIPT_FOR_60_SECONDS>'

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)

display = lcddriver.lcd()
display.lcd_clear()

SENSOR = 23
BUZZER = 21
BUTTON = 26

RED = 17
GREEN = 18
BLUE = 27

GPIO.setup(RED, GPIO.OUT)
GPIO.setup(GREEN, GPIO.OUT)
GPIO.setup(BLUE, GPIO.OUT)
GPIO.output(RED, 1)
GPIO.output(GREEN, 1)
GPIO.output(BLUE, 1)

GPIO.setup(BUZZER, GPIO.OUT)

GPIO.setup(SENSOR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

logger = logging.getLogger()

def end():
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    
    #os.system(f"rm {FILE}")
    print("Motion detector disabled")
    
    GPIO.setup(RED, GPIO.OUT)
    GPIO.setup(GREEN, GPIO.OUT)
    GPIO.setup(BLUE, GPIO.OUT)
    
    GPIO.output(RED, 1)
    GPIO.output(GREEN, 1)
    GPIO.output(BLUE, 1)
    
    display.lcd_clear()
    
    sys.exit()
    
def warning():
    
    for _ in range(10):
        
        time.sleep(0.5)
        GPIO.output(RED, 0)
        time.sleep(0.5)
        GPIO.output(RED, 1)   
    
def lcd_wait(countdown):
    
    display.lcd_clear()
    display.lcd_display_string("Security System:", 1)
    
    for _ in range(60):
        
        countdown = countdown -1
        
        time.sleep(1)

        display.lcd_display_string(f"disabled for {countdown}s", 2)
        
        print(countdown)
    
def sendEmail(evidence):
    
    email_user = '<EMAIL_FROM>'
    email_password = '<PASSWORD>'
    email_send = '<EMAIL_TO>'

    subject = 'Movement detected from raspberryPi4'

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_send
    msg['Subject'] = subject
    
    today = datetime.datetime.today()
    
    if today.minute < 10:
        minute = f'0{today.minute}'
        time = f'{today.hour}:{minute}'
    else:
        time = f'{today.hour}:{today.minute}'
        
    print(time)
    
    day = today.strftime('%A')
    month = today.strftime('%B')
    date = today.day   
    final_date = f'{day} the {date} of {month}'
    print(final_date)
    
    body = f'Movement detected from raspberryPi4 at {time} on {final_date}'
    msg.attach(MIMEText(body,'plain'))

    filename = evidence
    attachment = open(filename,'rb')

    part = MIMEBase('application','octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',"attachment; filename= "+filename)

    msg.attach(part)
    text = msg.as_string()
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    server.login(email_user,email_password)


    server.sendmail(email_user,email_send,text)
    server.quit()

        
def motionSensor(channel):

    
    if GPIO.input(SENSOR):
        #when motion, takes a picture and buzzes
        GPIO.output(RED, 1)
        
        GPIO.output(BLUE, 0)
        #os.system("fswebcam -q --set brightness=80% /home/pi/Pictures/evidence.png")

        camera.capture('/home/pi/Pictures/evidence.png')

        
        logger.warning("Picture taken")
        time.sleep(0.5)
        
        display.lcd_display_string(" Hold button to ", 1)
        display.lcd_display_string("abort email send", 2)
                
        #for _ in range(2):
            #GPIO.output(BUZZER, True)
            
            #time.sleep(0.2)
           
            #GPIO.output(BUZZER, False)
        
            #time.sleep(0.2)
            
        time.sleep(3)
        
        if not GPIO.input(BUTTON):
            
            display.lcd_clear()
            
            display.lcd_display_string("Security System:", 1)
            display.lcd_display_string("    disabled", 2)
            
            logger.warning("Security System disabled")
            GPIO.output(BLUE, 1)
            
            GPIO.output(GREEN, 0)
            time.sleep(1)
            GPIO.output(GREEN, 1)
            
            GPIO.output(RED, 1)
            GPIO.output(GREEN, 1)
            GPIO.output(BLUE, 1)
            
            os.system(f"rm {FILE}")
            
            end()
            #sys.exit()
            
        display.lcd_clear()
        display.lcd_display_string("Security System:", 1)
        display.lcd_display_string("   email sent", 2)
        
        evidence = '/home/pi/Pictures/evidence.png'
        
        sendEmail(evidence)
        
               
        logger.warning("Email sent")
        
        GPIO.output(BLUE, 1)
        
        time.sleep(0.5)
        
        display.lcd_clear()
        display.lcd_display_string("Security System:", 1)
        display.lcd_display_string("going offline...", 2)
        
        print("Motion detector going offline...")
        
        time.sleep(30)
        
        display.lcd_clear()
        display.lcd_display_string("Security System:", 1)
        display.lcd_display_string("  back online!", 2)
        print("Motion detector back online")
        
        GPIO.output(RED, 0)
        
    else:
        print("")

try:
    if os.path.exists(FILE):
        
        logger.warning("Program already running")
        end()
    else:
        open(FILE,"a").close()
    
    warn = threading.Thread(target=warning, args=(), daemon=False)
    warn.start()
    
    display.lcd_display_string("Security System:", 1)
    display.lcd_display_string(" Exit premises!", 2)
    
    logger.warning("10 Seconds to leave premises")
    time.sleep(5)
    logger.warning("5 Seconds to leave premises")
    time.sleep(4.75)
    GPIO.output(BUZZER, True)
            
    time.sleep(0.25)
           
    GPIO.output(BUZZER, False)
    
    display.lcd_clear()
    display.lcd_display_string("Security System:", 1)
    display.lcd_display_string("    Enabled!", 2)
                                       
    
    GPIO.add_event_detect(SENSOR, GPIO.BOTH, callback=motionSensor, bouncetime=150)
        
    GPIO.output(RED, 0)
    
    while True:
        
        time.sleep(0.2)
        
        if not os.path.exists(FILE):
            end()
         
        if os.path.exists(PAUSE_FILE):
             
             os.system(f"rm {PAUSE_FILE}")
             
             GPIO.remove_event_detect(SENSOR)
             
             #print("pausing for 1 minute")
             countdown = 60
             
             t2 = threading.Thread(target=lcd_wait, args=(countdown,), daemon=False)
             t2.start()
             
             GPIO.output(RED, 1) 
             GPIO.output(GREEN, 0)
             
             time.sleep(60)
             
             GPIO.output(GREEN, 1)
             
             GPIO.add_event_detect(SENSOR, GPIO.BOTH, callback=motionSensor, bouncetime=150)

         
except KeyboardInterrupt:
    GPIO.cleanup()
    print("Motion detector disabled")
    os.system(f"rm {FILE}")
    

