#СЕРВЕР

from kivy.app import App
from kivy.uix.image import Image as Image1
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.config import Config
from kivy.lang import Builder
import cv2
#import serial
from vidgear.gears import NetGear
#from picamera import PiCamera
#from picamera.array import PiRGBArray библиотеки для RaspberryPi
import sys
from threading import Thread as thread

# UX
kv = '''
main:
        BoxLayout:
                id: bx
                orientation: 'vertical'
                padding: root.width * 0.05, root.height * .05
                spacing: '5dp'
                BoxLayout:
                        size_hint: [1,.7]
                        id: box
                BoxLayout:
                        size_hint: [1,.15]
                        id: box2
                        GridLayout:
                                cols: 3
                                spacing: '10dp'
                                Button:
                                        id: btn1
                                        text:'Подключиться'
                                        on_press: root.Connect()
                                        bold: True
                                Button:
                                        id: btn2
                                        text: 'Настройки'
                                        on_press: root.Settings()
                                        bold: True
'''
# класс "камеры"
class Camera(Image1):
    def __init__(self, temp, fps, resolution, **kwargs):
        super(Camera, self).__init__(**kwargs)
        self.temp = temp
        self.port = None
        self.ip = None
        self.thread1 = None
        self.serversocket = None
        self.webc = cv2.VideoCapture(0)
        self.options = {"flag": 0, "copy": False, "track": False, "max_retries": 0, "bidirectional_mode": True}
        Clock.schedule_interval(self.update, 1.0 / (fps * 1.0))
    
    #установка ip и порта
    def Ip(self, ip, port):
        self.ip = ip
        self.port = int(port)
        
    #изменение локального флага temp и запуск/остановка потока
    def TEMP(self):
        if self.thread1 == None:
            self.thread1 = thread(target=self.Thread, args=())
        if self.temp==True:
            self.temp = False
            try:
                self.thread1.join(1)
                self.thread1 = None
                self.serversocket.close()
                self.serversocket = None
            except: pass
        elif self.temp==False:
            self.temp = True
            try:
                self.serversocket = NetGear(
                address=self.ip,
                port=str(self.port),
                protocol="tcp",
                pattern=1,
                logging=True,
                **self.options
                )
                self.thread1.start()
            except: pass
        
    # поток, передача изображений через сокеты
    def Thread(self):
        if not(self.port == None and self.ip == None):
            while(True):
                            res, frame = self.webc.read()
                            if(res):
                                if(self.temp == True):
                                    text = "coordinations" #вместо координат с GPS датчика
                                    self.serversocket.send(frame, message=text)
                                else:
                                    break;
    # обновление кадров с вебкамеры            
    def update(self, dt):
            res, frame = self.webc.read()
            if res:
                buf1 = cv2.flip(frame, 0)
                #buf2 = cv2.flip(buf1, 1)
                buf = buf1.tostring()
                image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.texture = image_texture
            
            
class main(BoxLayout):
    temp = False
    port = '7777'
    #ip = socket.gethostbyname(socket.gethostname()) #это для взятия ip адреса платы
    ip = '77.37.246.140'
    # кнопка Подключиться/Отключиться (начало получения видеопотока и завершение получения)    
    def Connect(self):
        if not self.ip == None and not self.port == None:
            if(self.temp == True):
                self.temp = False
                self.ids.btn1.text = 'Подключиться'
            else: 
                self.temp = True
                self.ids.btn1.text = 'Отключиться'
                self.camera.Ip(self.ip, self.port)
            self.camera.TEMP()
        else:
            box = GridLayout(cols=1)
            box.add_widget(Label(text="IP или Порт не установлен"))
            btn = Button(text="OK")
            btn.bind(on_press=self.closePopup)
            box.add_widget(btn)
            self.popup1 = Popup(title='Ошибка',content=box,size_hint=(.8,.3))
            self.popup1.open()
            
    #закрытие окна настроек      
    def closePopup(self,btn):
        self.popup1.dismiss()

    #открытие окна настроек
    def Settings(self):
        if(self.temp == False):
            box = GridLayout(cols = 2)
            box.add_widget(Label(text="IP адрес сервера: ", bold = True))
            self.st = TextInput(text= "serverText")
            if not (self.ip == None): self.st.text = self.ip
            box.add_widget(self.st)
            box.add_widget(Label(text="Порт: ", bold = True))#для соединения по интернету нужно открыть порт
            self.pt = TextInput(text= "portText")
            if not (self.port == None): self.pt.text = self.port
            box.add_widget(self.pt)
            btn = Button(text="Установить")
            btn.bind(on_press=self.settingProcess)
            box.add_widget(btn)
            self.popup = Popup(title='Настройки',content=box,size_hint=(.6,.4))
            self.popup.open()
        
    #устанавливаются ip и порт
    def settingProcess(self, btn):
        try:
            self.ip = self.st.text
            self.port = self.pt.text
            self.camera.Ip(self.ip, self.port)
        except:
            pass
        self.popup.dismiss()
          
     
class DroneApp(App):
    def build(self):
        #создание "камеры" куда будут приходить фото с сервера
        x = Builder.load_string(kv)
        #x.capture = cv2.VideoCapture(0)
        x.camera = Camera(temp = False, fps=40, resolution = (640,480), pos_hint= {'center_x': .5, 'center_y': .5})
        x.ids.box.add_widget(x.camera)
        return x

#print ("\nServer started at " + str(socket.gethostbyname(socket.gethostname())) + " at port " + str(port))

Config.set('graphics','resizable',0)
DroneApp().run()
if DroneApp().on_stop() == True:
        sys.exit(0)


