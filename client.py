#КЛИЕНТ

from kivy.config import Config
import os
import sys
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
import ner 
from threading import Thread as thread
from kivy.uix.image import Image as Image1
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics.texture import Texture
from kivy.core.image import Image as CoreImage
from kivy.uix.checkbox import CheckBox
import cv2 
import numpy as np
from PIL import Image
from vidgear.gears import NetGear
#from PIL import ImageOps #библиотека для изменения изображений(пока не нужна)

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
                                cols: 4
                                spacing: '8dp'
                                Button:
                                        id: status
                                        text:'Старт'
                                        bold: True
                                        on_press: root.playPause()
                                Button:
                                        id: save
                                        text:'Сохранить'
                                        bold: True
                                        on_press: root.save()
                                Button:
                                        text: 'Настройки'
                                        bold: True
                                        on_press: root.setting()
                                Button:
                                        text: 'Тип нейросети'
                                        bold: True
                                        on_press: root.ney()

'''

#класс "камеры"
class KivyCamera(Image1):
    def __init__(self, fps, resolution, pos_hint, **kwargs):
            super(KivyCamera, self).__init__(**kwargs)
            self.clientsocket= None
            self.ip = None
            self.port = None
            self.thread1 = None
            self.IMAGE = None
            self.i = 0
            self.schot = 0
            self.options = {"flag": 0, "copy": False, "track": False, "max_retries": 0, "bidirectional_mode": True}
    #поток
    def Thread(self):
        global coord
        global temp
        if(temp == True):
            coord = ''
            self.IMAGE = None
            self.clientsocket
            Clock.schedule_interval(self.update, 0.033)
    
    #изменение локального флага temp и запуск/остановка потока
    def TEMP(self):
        global temp
        if(self.thread1 == None):
            self.thread1 = thread(target=self.Thread, args=())
        if temp==True:
            temp = False     
            self.clientsocket = None
            self.thread1.join(3)
            self.i = 0
            self.thread1 = None
        elif temp==False:
            temp = True
            self.IMAGE = None
            self.clientsocket= NetGear(
            address=self.ip,
            port=str(self.port),
            protocol="tcp",
            pattern=1,
            receive_mode=True,
            logging=True,
            **self.options
            )
            self.thread1.start()
        
    #установка ip и порта
    def Ip(self, ip, port):
        self.ip = ip
        self.port = int(port)

    #передача в главный класс фото, которое надо сохранить
    def Image_save(self):
        return self.IMAGE
    
    #получение кадров видеопотока и их отображение (скоро в проект будет добавлена нейросеть, которая будет обрабатывать кадры, и сохранять нужные(те, на которых изображены повреждения фасада))
    def update(self, dt):
        global temp
        global coord
        if not(self.port == None and self.ip == None):
            if temp==True:
                        try:
                            data = self.clientsocket.recv()
                            if data is None:
                                    self.clientsocket.close()
                                    self.TEMP()
                            self.i += 1
                            self.schot +=1
                            coord, frame = data
                            buf = cv2.flip(frame, 0)
                            arr = np.asarray(buf)
                            buf2 = cv2.flip(frame, 1)
                            buf3 = cv2.cvtColor(buf2, cv2.COLOR_BGR2RGB)
                            img = Image.fromarray(buf3)
                            self.IMAGE = img
                            if(self.i == 15):
                                img.save(os.path.dirname(__file__) + '\\temp\\' + coord + str(self.schot) + '.jpg')
                                self.i = 0
                            image_texture = Texture.create(size=(640, 480), colorfmt='bgr')
                            image_texture.blit_buffer(arr.tostring(), colorfmt='bgr', bufferfmt='ubyte')
                            self.texture = image_texture
                        except:
                            if not (self.clientsocket==None):
                                    self.clientsocket.close()
                                    self.TEMP()
            else:
                if not (self.clientsocket==None):
                    self.clientsocket.close()
                    self.TEMP()
            

class main(BoxLayout):
        ipAddress = '192.168.1.199'
        port = '7777'
        # temp - это проверкa, нажата ли кнопка запуска потока
        # кнопка старт/стоп (начало получения видеопотока и завершение получения)
        def playPause(self):
                if self.ipAddress == None or self.port == None:
                        box = GridLayout(cols=1)
                        box.add_widget(Label(text="IP или Порт не установлены"))
                        btn = Button(text="OK")
                        btn.bind(on_press=self.closePopup)
                        box.add_widget(btn)
                        self.popup1 = Popup(title='Error',content=box,size_hint=(.8,.3))
                        self.popup1.open()
                else:
                        if self.ids.status.text == "Стоп":
                                self.ids.status.text = "Старт"
                                im = CoreImage('foo.png').texture
                                self.camera.texture = im
                                self.camera.TEMP()
                        else:
                                self.ids.status.text = "Стоп"
                                self.camera.Ip(self.ipAddress, self.port)
                                self.camera.TEMP()
                Clock.schedule_interval(self.update, 0.1)
        
        # проверка изменения temp в классе Kivycamera
        def update(self, dt):
                global temp
                if (temp == False):
                    self.ids.status.text = "Старт"
                    im = CoreImage('foo.png').texture
                    self.camera.texture = im
                else:
                    self.ids.status.text = "Стоп"
                               
        #закрытие окна настроек
        def closePopup(self,btn):
                self.popup1.dismiss()

        def save(self):
            global temp
            global coord
            #сохранение изображений в папку, в которой лежит исполняемый код
            if (not coord == '') and (temp == True):
                image = self.camera.Image_save()
                image.save(os.path.dirname(__file__) + '\\saves\\' + coord + '_image_savedbyyou.jpg')
                image.save(os.path.dirname(__file__) + '\\temp\\' + coord + '_img_save.jpg')
                
        def ney(self):
            global temp
            global index
            if(temp == False):
                box = GridLayout(cols = 2)
                self.popup = Popup(title='Тип нейросети: ',content=box,size_hint=(.6,.4))
                box.add_widget(Label(text ='34_слоя'))
                ch0 = CheckBox(active = False)
                ch1 = CheckBox(active = False)
                ch2 = CheckBox(active = False)
                box.add_widget(ch0)
                box.add_widget(Label(text ='50_слоёв'))
                box.add_widget(ch1)
                box.add_widget(Label(text ='152_слоя'))
                box.add_widget(ch2)
                ch0.bind(active = self.on_ch0_Active)
                ch1.bind(active = self.on_ch1_Active)
                ch2.bind(active = self.on_ch2_Active)
                if(index == 0):
                    ch0.active = True
                    ch1.active = False
                    ch2.active = False
                elif(index == 1):
                    ch0.active = False
                    ch1.active = True
                    ch2.active = False
                else:
                    ch0.active = False
                    ch1.active = False
                    ch2.active = True
                self.popup.open()
                
        def on_ch0_Active(self, ch0, t):
                global index
                index = 0
                ch0.active = True
                self.popup.dismiss()
                
        def on_ch1_Active(self, ch1, t):
                global index
                index = 1
                ch1.active = True
                self.popup.dismiss()
                
        def on_ch2_Active(self, ch2, t):
                global index
                index = 2
                ch2.active = True
                self.popup.dismiss()
        
        #открытие окна настроек
        def setting(self):
            global temp
            if(temp == False):
                box = GridLayout(cols = 2)
                box.add_widget(Label(text="IP: ", bold = True))
                self.st = TextInput(text= "serverText")
                if not (self.ipAddress == None): self.st.text = self.ipAddress #для соединения по локальной сети нужно ввести ip того же компьютера или "localhost", а для подключения через интернет - ip роутера сервера
                box.add_widget(self.st)
                box.add_widget(Label(text="Порт: ", bold = True))
                self.pt = TextInput(text= "portText")
                if not (self.port == None): self.pt.text = self.port
                box.add_widget(self.pt)
                btn = Button(text="Установить", bold=True)
                btn.bind(on_press=self.settingProcess)
                box.add_widget(btn)
                self.popup = Popup(title='Найстройки',content=box,size_hint=(.6,.4))
                self.popup.open()
        
        #устанавливаются ip и порт
        def settingProcess(self, btn):
                try:
                        self.ipAddress = self.st.text
                        self.port = self.pt.text
                        self.camera.Ip(self.ipAddress, self.port)
                except:
                        pass
                self.popup.dismiss()

class ClientApp(App):
    def build(self):
        #создание "камеры" куда будут приходить фото с сервера
        x = Builder.load_string(kv)
        x.camera = KivyCamera(fps=30, resolution = (640,480), pos_hint= {'center_x': .5, 'center_y': 1})
        x.ids.box.add_widget(x.camera)
        im = CoreImage('foo.png').texture
        x.camera.texture = im
        return x
    
def Threadney():
    global coord
    global index
    i = 0
    while True:
        if(coord != ''):
            for root, dirs, files in os.walk(os.path.dirname(__file__) + "\\temp"):
                for file in files:
                    s = ""
                    s = str(ner.neyro(file, index))
                    if s == "повреждённая бетонная стена" or s == "повреждённая кирпичная стена" or s == "разбитое окно":
                        i += 1
                        if "img_save" in file:
                            os.replace(os.path.dirname(__file__) + '\\temp\\' + file, os.path.dirname(__file__) + '\\saves\\' + str(s) + '_' + coord + str(i) + '_yourphoto' + '.jpg')
                        else:
                            os.replace(os.path.dirname(__file__) + '\\temp\\' + file, os.path.dirname(__file__) + '\\saves\\' + str(s) + '_' + coord + str(i) + '.jpg')
                    else:
                        os.remove(os.path.dirname(__file__) + '\\temp\\' + file)
        

global coord
global index
global temp
temp = False
index = 1
coord = ''
Config.set('graphics','resizable',0)
thread2 = thread(target=Threadney, args=())
thread2.start()
ClientApp().run()
if ClientApp().on_stop() == True:
            thread2.join(10)
            sys.exit(0)
#except: pass