
# Need a datum select pop-up 
# Need a setup screen to set the total station type to simulation
# Need a select prism pop-up
# Need the program flow from record point, to select prism, to edit point, to save
# Need a read and write ini to be able to easily resume the program
# Need status screen
# Then start working on the flow for more complex setups
# See if individual items in the data grid can be selected
# Add communications parameters to setup
# Add serial port communications
# Add bluetooth communications

__version__ = '1.0.0'

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ListProperty, StringProperty, ObjectProperty, BooleanProperty, NumericProperty
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.core.window import Window

import os
import string
import random
import numpy as np
import datetime
import pandas as pd 
import logging

from collections import OrderedDict

OPTIONBUTTON_BACKGROUND = (128/255, 216/255, 255/255, 1) #80D8FF (lighter blue)
OPTIONBUTTON_COLOR = (0, 0, 0, 1) # black
BUTTON_BACKGROUND = (0, .69, 255/255, 1) #00B0FF (deep blue)
BUTTON_COLOR =  (0, 0, 0, 1) # black
WINDOW_BACKGROUND = (255/255, 255/255, 255/255, 1) #FFFFFF
WINDOW_COLOR = (0, 0, 0, 1)

test = (128 / 255, 216/255, 255/255, 1)
# get anglr.py library
# or get angles.py library (looks maybe better)

# use pySerial for serial communications

class points:
    MAX_FIELDS = 30

    class field:
        def __init__(self, name):
            self.name = name
            self.type = 'Text'
            self.menulist = []
            self.prompt = name
            self.maxlen = 10
            self.increment = False
            self.required = False
            self.carry = False 
            self.unique = False

    def __init__(self, filename):
        self.filename = filename
        # check to see if this file exists already and if so read in the data
        # if no file exists are after opening the file there are no fields, insert default fields
        self.fields = []
        self.records = []

    def status(self):
        txt = 'The points file is %s\n' % self.filename
        txt += '%s points in the data file\n' % self.record_count()
        txt += 'with %s fields per point' % self.field_count()
        return(txt)

    def create_defaults(self):
        pass

    def names(self):
        name_list = []
        for field in self.fields:
            name_list.append(field.name)
        return(name_list)

    def field_count(self):
        return(len(self.fields))

    def record_count(self):
        pass
    
    def delete_all(self):
        self.records = []

    def export_csv(self):
        pass

    def delete_record(self):
        pass

    def add_record(self):
        pass

    def initialize(self):
        pass

class datums:
    MAX_DATUMS = 100
    
    class datum:
        def __init__(self, datum_name):
            self.name = datum_name
            self.x = 0
            self.y = 0
            self.z = 0
            self.date_created = ''
    
    def __init__(self, filename):
        self.filename = filename
        if os.path.exists(self.filename):
            self.datums = pd.read_csv(self.filename)
        else:
            self.datums = pd.DataFrame(columns = ['Name','X','Y','Z','Date_Created'])
            self.save()

    def status(self):
        txt = '%s datums are defined\n' % self.count()
        return(txt)

    def save(self):
        self.datums.to_csv(self.filename, index=False)

    def count(self):
        return(self.datums.shape[0])

    def names(self):
        return(self.datums.loc[:,'Name'])

class prisms:
    MAX_PRISMS = 20

    class prism:
        def __init__(self):
            self.name = ''
            self.height = 0
            self.offset = 0

    def __init__(self, filename):
        self.filename = filename
        if os.path.exists(self.filename):
            self.prisms = pd.read_csv(self.filename)
        else:
            self.prisms = pd.DataFrame(columns = ['Name','Height','Offset'])
            self.save()

    def status(self):
        txt = '%s prisms are defined\n' % self.count()
        return(txt)

    def save(self):
        self.prisms.to_csv(self.filename, index=False)

    def count(self):
        return(self.prisms.shape[0])

    def names(self):
        return(self.prisms.loc[:,'Name'])

class units:
    MAX_UNITS = 100

    class unit:
        def __init__(self):
            self.name = ''
            self.x1 = 0
            self.y1 = 0
            self.x2 = 0
            self.y2 = 0
            self.radius = 0

    def __init__(self, filename):
        self.filename = filename
        if os.path.exists(self.filename):
            self.units = pd.read_csv(self.filename)
        else:
            self.units = pd.DataFrame(columns = ['Name','X1','Y1','X2','Y2','Radius'])
            self.save()

    def status(self):
        txt = '%s units are defined\n' % self.count()
        return(txt)

    def save(self):
        self.units.to_csv(self.filename, index=False)

    def count(self):
        return(self.units.shape[0])

    def names(self):
        return(self.units.loc[:,'Name'])

class manage_inicfg:
    def update_value(blocks, blockname, varname, vardata, append = False):
        block_exists = False
        for block in blocks:
            if block['BLOCKNAME']==blockname:
                block_exists = True
                if (varname in block.keys()) and append:
                    block[varname] = [block[varname] , vardata]
                else:
                    block[varname] = vardata 
                return(True)
        if not block_exists:
            temp = {}
            temp['BLOCKNAME'] = blockname
            temp[varname] = vardata
            blocks.append(temp)
            return(True)
        return(False)

    def read_blocks(filename):
        blocks = []
        try:
            with open(filename) as f:
                for line in f:
                    if len(line) > 2:
                        if line.strip()[0]=="[":
                            blockname = line.strip()[1:-1].upper()
                        else:
                            if '=' in line:
                                varname = line.split("=")[0].strip().upper()
                                vardata = line.split("=")[1].strip()
                                manage_inicfg.update_value(blocks, blockname, varname, vardata)
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            logging.exception(message)
            return([])
        return(blocks)

    def names(blocks):
        name_list = []
        for block in blocks:
            name_list.append(block['BLOCKNAME'])
        return(name_list)
        
    def get_value(blocks, blockname, varname):
        for block in blocks:
            if block['BLOCKNAME'] == blockname:
                if varname in block.keys():
                    return(block[varname])
                else:
                    return('')
        return('')                

    def write_blocks(filename, blocks):
        try:
            with open(filename, mode = 'w') as f:
                for block in blocks:
                    f.write("[%s]\n" % block['BLOCKNAME'])
                    for item in block.keys():
                        f.write(item + "=%s\n" % block[item])
                    f.write("\n")
            return(True)
        except:
            return(False)

class ini:
    
    blocks = []

    def __init__(self, filename):
        self.filename = filename
        self.blocks = manage_inicfg.read_blocks('EDMpy.ini')

    def update(self):
        global edm_station
        global edm_cfg
        manage_inicfg.update_value(self.blocks,'STATION','TotalStation', edm_station.make)
        manage_inicfg.update_value(self.blocks,'STATION','Communication', edm_station.communication)
        manage_inicfg.update_value(self.blocks,'STATION','COMPort', edm_station.comport)
        manage_inicfg.update_value(self.blocks,'STATION','BAUD', edm_station.baudrate)
        manage_inicfg.update_value(self.blocks,'STATION','Parity', edm_station.parity)
        manage_inicfg.update_value(self.blocks,'STATION','DataBits', edm_station.databits)
        manage_inicfg.update_value(self.blocks,'STATION','StopBits', edm_station.stopbits)
        manage_inicfg.update_value(self.blocks,'EDM','CFG', edm_cfg.filename)
        self.save()

    def get_value(self, blockname, varname):
        return(manage_inicfg.get_value(self.blocks, blockname, varname))

    def save(self):
        manage_inicfg.write_blocks('EDMpy.ini', self.blocks)

class cfg:

    blocks = []
    filename = ""

    def __init__(self, filename):
        self.load(filename)

    def fields(self):
        return(manage_inicfg.names(self.blocks))

    def get_value(self, blockname, varname):
        return(manage_inicfg.get_value(self.blocks, blockname, varname))

    def build_default(self):
        manage_inicfg.update_value(self.blocks, 'UNIT', 'Prompt', 'Unit :')
        manage_inicfg.update_value(self.blocks, 'UNIT', 'Type', 'Text')
        manage_inicfg.update_value(self.blocks, 'UNIT', 'Length', 6)

        manage_inicfg.update_value(self.blocks, 'ID', 'Prompt', 'ID :')
        manage_inicfg.update_value(self.blocks, 'ID', 'Type', 'Text')
        manage_inicfg.update_value(self.blocks, 'ID', 'Length', 6)

        manage_inicfg.update_value(self.blocks, 'SUFFIX', 'Prompt', 'Suffix :')
        manage_inicfg.update_value(self.blocks, 'SUFFIX', 'Type', 'Numeric')

        manage_inicfg.update_value(self.blocks, 'LEVEL', 'Prompt', 'Level :')
        manage_inicfg.update_value(self.blocks, 'LEVEL', 'Type', 'Menu')
        manage_inicfg.update_value(self.blocks, 'LEVEL', 'Length', 20)

        manage_inicfg.update_value(self.blocks, 'CODE', 'Prompt', 'Code :')
        manage_inicfg.update_value(self.blocks, 'CODE', 'Type', 'Menu')
        manage_inicfg.update_value(self.blocks, 'CODE', 'Length', 20)

        manage_inicfg.update_value(self.blocks, 'EXCAVATOR', 'Prompt', 'Excavator :')
        manage_inicfg.update_value(self.blocks, 'EXCAVATOR', 'Type', 'Menu')
        manage_inicfg.update_value(self.blocks, 'EXCAVATOR', 'Length', 20)

        manage_inicfg.update_value(self.blocks, 'PRISM', 'Prompt', 'Prism :')
        manage_inicfg.update_value(self.blocks, 'PRISM', 'Type', 'Numeric')

        manage_inicfg.update_value(self.blocks, 'X', 'Prompt', 'X :')
        manage_inicfg.update_value(self.blocks, 'X', 'Type', 'Numeric')

        manage_inicfg.update_value(self.blocks, 'Y', 'Prompt', 'Y :')
        manage_inicfg.update_value(self.blocks, 'Y', 'Type', 'Numeric')

        manage_inicfg.update_value(self.blocks, 'Z', 'Prompt', 'Z :')
        manage_inicfg.update_value(self.blocks, 'Z', 'Type', 'Numeric')

        manage_inicfg.update_value(self.blocks, 'DATE', 'Prompt', 'Date :')
        manage_inicfg.update_value(self.blocks, 'DATE', 'Type', 'Text')
        manage_inicfg.update_value(self.blocks, 'DATE', 'Length', 24)

        # should add hangle, vangle, sloped 

    def validate(self):
        pass

    def save(self):
        manage_inicfg.write_blocks(self.filename, self.blocks)

    def load(self, filename):
        self.filename = filename 
        self.blocks = manage_inicfg.read_blocks(filename)
        if self.blocks==[]:
            self.build_default()
    
    def status(self):
        txt = 'CFG file is %s\n' % self.filename
        return(txt)

class totalstation:
    def __init__(self, make = "Emulation", model = ''):
        self.make = make
        self.model = model
        self.communication = 'Serial'
        self.comport = 'COM1'
        self.baudrate = '1200'
        self.parity = 'EVEN'
        self.databits = 7
        self.stopbits = 1
        self.comport_settings = ''
        self.input_string = ''
        self.output_string = ''
        self.port_open = False
        self.current_x = 0
        self.current_y = 0
        self.current_z = 0
        self.x = 0
        self.y = 0
        self.z = 0
        self.prism = 0
        self.hangle = ''
        self.vangle = ''
        self.sloped = 0

    def status(self):
        txt = 'Total Station:\n'
        txt += 'Make is %s\n' % self.make
        txt += 'Communication type is %s\n' % self.communication
        txt += 'COM Port is %s\n' % self.comport
        txt += 'Com settings are %s, %s, %s, %s\n' % (self.baudrate,self.parity,self.databits,self.stopbits)
        if self.port_open:
            txt += 'COM Port is open\n'
        else:
            txt += 'COM port is closed\n'
        txt += 'Station X : %s\n' % self.current_x
        txt += 'Station Y : %s\n' % self.current_y
        txt += 'Station Z : %s\n' % self.current_z

        return(txt)

    def initialize(self):
        pass

    def parseangle(self, hangle):
        hangle = str(hangle)
        if hangle.find("."): 
            angle = int(hangle) 
            minutes = 0
            seconds = 0
        else:
            hangle = hangle + "0000"
            angle = hangle.split(".")[0]
            minutes = hangle.split(".")[1][0:2]
            seconds = hangle.split(".")[1][2:4]

        return([angle, minutes, seconds])

    def hash(self, hashlen):
        hash = ""
        for a in range(0, hashlen):
            hash = hash + random.choice(string.ascii_uppercase)
        return(hash)

    def take_shot(self):
        if self.make=='TOPCON':
            clearcom()
            edm_output("Z34")   # Slope angle mode
            edm_input
            delay(0.5)

            edm_output("C")     # Take the shot
            edm_input()
            delay(0.5)

        if self.make=="WILD" or self.make=="LEICA":
            clear_com()
            edm_output("GET/M/WI11/WI21/WI22/WI31/WI51")

        if self.make=="SOKKIA":
            edm_output(Chr(17))

    def set_horizontal_angle(angle):
        pass

    def vhd_to_nez(self):
        pass

    def parse_nez(self):
        pass

    def make_bcc(self, itext):
        #Dim b As Integer = 0
        #Dim i As Integer
        #Dim q As Integer
        #Dim b1 As Integer
        #Dim b2 As Integer

        b = 0 
        for i in range(0,len(itext)):
            #q = asc(itext[i:i+1])
            #b1 = q and (Not b) # this is not at all ready
            #b2 = b and (Not q)
            #b = b1 or b2
            pass

        bcc = "000" + str(b).strip()
        return(bcc[-3])

    def init_edm(self):
        if self.make=='TOPCON':
            edm_output("ST0")
        if self.make=="WILD" or self.make=="LEICA":
            if edm_output("SET/41/0")==0:
                edm_input()
            if edm_output("SET/149/2")==0:
                edm_input()

    def horizontal(self):
        if self.make=='TOPCON':
            edm_output("Z10")
            return(edm_input)

    def edm_output(self, d):
        error_code = 0
        return(error_code)

    def edm_input(self):
        return('')

    def close_com(self):
        pass

    def open_com(self):
        pass

    def clear_com(self):
        pass

    def deg_to_rad(self):
        pass

    def conv_angle_to_degminsec(self):
        pass

    def calculate_angle(self):
        pass

class LoadDialog(FloatLayout):
    start_path =  ObjectProperty(None)
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)

class Root(FloatLayout):
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load_cfg(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Open CFG file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load_cfg(self, path, filename):
        cfg = cfg(os.path.join(path, filename[0]))
        cfg.load()
        self.dismiss_popup()

    def save(self, path, filename):
        with open(os.path.join(path, filename), 'w') as stream:
            stream.write(self.text_input.text)

        self.dismiss_popup()

class EditDatums(Screen):
    pass

class record_button(Button):
    def __init__(self,id,text,**kwargs):
        super(Button, self).__init__(**kwargs)
        self.text = text
        self.id = id
        self.size_hint_y = None
        self.id = id
        self.color = BUTTON_COLOR
        self.background_color = BUTTON_BACKGROUND
        self.background_normal = ''

class MainScreen(Screen):

    popup = ObjectProperty(None)

    def __init__(self,**kwargs):
        super(MainScreen, self).__init__(**kwargs)

        global edm_cfg

        layout = GridLayout(cols = 3, spacing = 10, size_hint_y = .8)

        if edm_cfg.get_value('BUTTON1','TITLE'):
            button1 = record_button(text = edm_cfg.get_value('BUTTON1','TITLE'), id = 'button1')
            layout.add_widget(button1)
            button1.bind(on_press = self.take_shot)

        if edm_cfg.get_value('BUTTON2','TITLE'):
            button2  = record_button(text = edm_cfg.get_value('BUTTON2','TITLE'), id = 'button2')
            layout.add_widget(button2)
            button2.bind(on_press = self.take_shot)

        if edm_cfg.get_value('BUTTON3','TITLE'):
            button3  = record_button(text = edm_cfg.get_value('BUTTON3','TITLE'), id = 'button3')
            layout.add_widget(button3)
            button3.bind(on_press = self.take_shot)

        if edm_cfg.get_value('BUTTON4','TITLE'):
            button4  = record_button(text = edm_cfg.get_value('BUTTON4','TITLE'), id = 'button4')
            layout.add_widget(button4)
            button4.bind(on_press = self.take_shot)

        if edm_cfg.get_value('BUTTON5','TITLE'):
            button5  = record_button(text = edm_cfg.get_value('BUTTON5','TITLE'), id = 'button5')
            layout.add_widget(button5)
            button5.bind(on_press = self.take_shot)

        if edm_cfg.get_value('BUTTON6','TITLE'):
            button6  = record_button(text = edm_cfg.get_value('BUTTON6','TITLE'), id = 'button6')
            layout.add_widget(button6)
            button6.bind(on_press = self.take_shot)

        button_rec = Button(text = 'Record', size_hint_y = None, id = 'record',
                        color = BUTTON_COLOR,
                        background_color = BUTTON_BACKGROUND,
                        background_normal = '')
        layout.add_widget(button_rec)
        button_rec.bind(on_press = self.take_shot)

        button_continue = Button(text = 'Continue', size_hint_y = None, id = 'continue',
                        color = BUTTON_COLOR,
                        background_color = BUTTON_BACKGROUND,
                        background_normal = '')
        layout.add_widget(button_continue)
        button_continue.bind(on_press = self.take_shot)

        button_measure = Button(text = 'Measure', size_hint_y = None, id = 'measure',
                        color = BUTTON_COLOR,
                        background_color = BUTTON_BACKGROUND,
                        background_normal = '')
        layout.add_widget(button_measure)
        button_measure.bind(on_press = self.take_shot)

        self.add_widget(layout)

    def take_shot(self, value):
        global edm_prisms
        layout_popup = GridLayout(cols = 1, spacing = 10, size_hint_y = None)
        layout_popup.bind(minimum_height=layout_popup.setter('height'))
        for prism in edm_prisms.names():
            button1 = Button(text = prism, size_hint_y = None, id = prism,
                        color = OPTIONBUTTON_COLOR,
                        background_color = OPTIONBUTTON_BACKGROUND,
                        background_normal = '')
            layout_popup.add_widget(button1)
            button1.bind(on_press = self.show_edit_screen)
        button2 = Button(text = 'Back', size_hint_y = None,
                        color = BUTTON_COLOR,
                        background_color = BUTTON_BACKGROUND,
                        background_normal = '')
        layout_popup.add_widget(button2)
        root = ScrollView(size_hint=(1, None), size=(Window.width, Window.height/1.9))
        root.add_widget(layout_popup)
        self.popup = Popup(title = 'Prism Height',
                    content = root,
                    size_hint = (None, None),
                    size=(400, 400),
                    #pos_hint = {None, None},
                    auto_dismiss = False)
        button2.bind(on_press = self.popup.dismiss)
        self.popup.open()

    def show_edit_screen(self, value):
        self.popup.dismiss()
        # note that prism name is value.text 
        self.parent.current = 'EditPointScreen'

    def show_load_cfg(self):
        content = LoadDialog(load = self.load, 
                            cancel = self.dismiss_popup,
                            start_path = os.path.dirname(os.path.abspath( __file__ )))
        self._popup = Popup(title = "Load CFG file", content = content,
                            size_hint = (0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        global edm_cfg, edm_ini
        edm_cfg.load(os.path.join(path, filename[0]))
        edm_ini.update()
        self.dismiss_popup()

    def dismiss_popup(self):
        self.popup.dismiss()
        self.parent.current = 'MainScreen'

class InitializeOnePointHeader(Label):
    pass

class InitializeDirectScreen(Screen):

    popup = ObjectProperty(None)

    def datum_list(self):
        layout_popup = GridLayout(cols = 1, spacing = 10, size_hint_y = None)
        layout_popup.bind(minimum_height=layout_popup.setter('height'))
        for datum in datums.names(EDMpy.edm_datums):
            button1 = Button(text = datum, size_hint_y = None, id = datum,
                        color = OPTIONBUTTON_COLOR,
                        background_color = OPTIONBUTTON_BACKGROUND,
                        background_normal = '')
            layout_popup.add_widget(button1)
            button1.bind(on_press = self.initialize_direct)
        button2 = Button(text = 'Cancel', size_hint_y = None,
                        color = BUTTON_COLOR,
                        background_color = BUTTON_BACKGROUND,
                        background_normal = '')
        layout_popup.add_widget(button2)
        root = ScrollView(size_hint=(1, None), size=(Window.width, Window.height/1.9))
        root.add_widget(layout_popup)
        self.popup = Popup(title = 'Initial Direct',
                    content = root,
                    size_hint = (None, None),
                    size=(400, 400),
                    #pos_hint = {None, None},
                    auto_dismiss = False)
        button2.bind(on_press = self.popup.dismiss)
        self.popup.open()

    def initialize_direct(self, value):
        EDMpy.edm_station.X = EDMpy.edm_datums.datums[EDMpy.edm_datums.datums.Name==value.id].iloc[0]['X']
        EDMpy.edm_station.Y = EDMpy.edm_datums.datums[EDMpy.edm_datums.datums.Name==value.id].iloc[0]['X']
        EDMpy.edm_station.Z = EDMpy.edm_datums.datums[EDMpy.edm_datums.datums.Name==value.id].iloc[0]['X']
        self.popup.dismiss()
        self.parent.current = 'MainScreen'

class InitializeSetAngleScreen(Screen):
    def set_angle(self, foreshot, backshot):
        if foreshot:
            totalstation.set_horizontal_angle(foreshot)
        elif backshot:
            # flip angle 180
            totalstation.set_horizontal_angle(foreshot)
        self.parent.current = 'MainScreen'

class InitializeOnePointScreen(Screen):
    def __init__(self,**kwargs):
        super(InitializeOnePointScreen, self).__init__(**kwargs)
        self.add_widget(InitializeOnePointHeader())
        self.add_widget(DatumLister())

class InitializeTwoPointScreen(Screen):
    def __init__(self,**kwargs):
        super(InitializeTwoPointScreen, self).__init__(**kwargs)
        self.add_widget(InitializeOnePointHeader())
        self.add_widget(DatumLister())

class InitializeThreePointScreen(Screen):
    def __init__(self,**kwargs):
        super(InitializeThreePointScreen, self).__init__(**kwargs)
        self.add_widget(InitializeOnePointHeader())
        self.add_widget(DatumLister())

class EditPointScreen(Screen):

    def on_pre_enter(self):
        #super(Screen, self).__init__(**kwargs)
        global edm_cfg
        layout = GridLayout(cols = 1, spacing = 10, size_hint_y = None)
        layout.bind(minimum_height=layout.setter('height'))
        for field in edm_cfg.fields():
            layout.add_widget(Label(text = field, size_hint_y = None, color = BUTTON_COLOR))
        button2 = Button(text = 'Save', size_hint_y = None,
                        color = BUTTON_COLOR,
                        background_color = BUTTON_BACKGROUND,
                        background_normal = '')
        layout.add_widget(button2)
        button3 = Button(text = 'Back', size_hint_y = None,
                        color = BUTTON_COLOR,
                        background_color = BUTTON_BACKGROUND,
                        background_normal = '')
        layout.add_widget(button3)
        root = ScrollView(size_hint=(1, None), size=(Window.width, Window.height/1.5))
        root.add_widget(layout)
        self.add_widget(root)

class EditPointsScreen(Screen):
    pass

class EditPrismsScreen(Screen):
    def __init__(self,**kwargs):
        super(EditPrismsScreen, self).__init__(**kwargs)
        global edm_prisms
        self.add_widget(DfguiWidget(edm_prisms.prisms, "prisms"))

class EditUnitsScreen(Screen):
    def __init__(self,**kwargs):
        super(EditUnitsScreen, self).__init__(**kwargs)
        global edm_units
        self.add_widget(DfguiWidget(edm_units.units, "units"))

class EditDatumsScreen(Screen):
    def __init__(self,**kwargs):
        super(EditDatumsScreen, self).__init__(**kwargs)
        global edm_datums
        self.add_widget(DfguiWidget(edm_datums.datums, "datums"))


class datumlist(RecycleView, Screen):
    def __init__(self, **kwargs):
        super(datumlist, self).__init__(**kwargs)
        self.data = [{'text': str(x)} for x in range(100)]


class MessageBox(Popup):

    def popup_dismiss(self):
        self.dismiss()


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    """ Adds selection and focus behaviour to the view. """
    selected_value = StringProperty('')
    btn_info = ListProperty(['Button 0 Text', 'Button 1 Text', 'Button 2 Text'])


class SelectableButton(RecycleDataViewBehavior, Button):
    """ Add selection support to the Label """
    index = None

    def refresh_view_attrs(self, rv, index, data):
        """ Catch and handle the view changes """
        self.index = index
        return super(SelectableButton, self).refresh_view_attrs(rv, index, data)

    def on_press(self):
        self.parent.selected_value = 'Selected: {}'.format(self.parent.btn_info[int(self.id)])

    def on_release(self):
        MessageBox().open()


class RV(RecycleView):
    rv_layout = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = [{'text': "Datum " + str(x), 'id': str(x)} for x in range(30)]


class DatumLister(BoxLayout,Screen):
    def __init__(self, list_dicts=[], *args, **kwargs):

        super(DatumLister, self).__init__(*args, **kwargs)
        self.orientation = "vertical"
        self.add_widget(RV())


class EditDatumScreen(Screen):
    pass


class StationConfigurationScreen(Screen):
    def __init__(self,**kwargs):
        super(StationConfigurationScreen, self).__init__(**kwargs)
    
        layout = GridLayout(cols = 2, spacing = 5)

        # Station type menu
        self.StationLabel = Label(text="Station type", color = WINDOW_COLOR)
        layout.add_widget(self.StationLabel)
        self.StationMenu = Spinner(text="Simulate", values=("Leica", "Wild", "Topcon", "Simulate"), id = 'station',
                                    color = OPTIONBUTTON_COLOR,
                                    background_color = OPTIONBUTTON_BACKGROUND,
                                    background_normal = '')
        self.StationMenu.size_hint  = (0.3, 0.2)
        layout.add_widget(self.StationMenu)

        # Communications type menu
        self.CommTypeLabel = Label(text="Communications", color = WINDOW_COLOR)
        layout.add_widget(self.CommTypeLabel)
        self.CommTypeMenu = Spinner(text="None", values=("Serial", "Bluetooth"), id = 'communications',
                                    color = OPTIONBUTTON_COLOR,
                                    background_color = OPTIONBUTTON_BACKGROUND,
                                    background_normal = '')
        self.CommTypeMenu.size_hint  = (0.3, 0.2)
        layout.add_widget(self.CommTypeMenu)

        # Port number
        self.PortNoLabel = Label(text="Port Number", color = WINDOW_COLOR)
        layout.add_widget(self.PortNoLabel)
        self.PortNoMenu = Spinner(text="COM1", values=("COM1", "COM2","COM3","COM4","COM5","COM6"), id = 'comport',
                                    color = OPTIONBUTTON_COLOR,
                                    background_color = OPTIONBUTTON_BACKGROUND,
                                    background_normal = '')
        self.PortNoMenu.size_hint  = (0.3, 0.2)
        layout.add_widget(self.PortNoMenu)

        # Speed
        self.SpeedLabel = Label(text="Speed", color = WINDOW_COLOR)
        layout.add_widget(self.SpeedLabel)
        self.SpeedMenu = Spinner(text="1200", values=("1200", "2400","4800","9600"), id = 'baudrate',
                                    color = OPTIONBUTTON_COLOR,
                                    background_color = OPTIONBUTTON_BACKGROUND,
                                    background_normal = '')
        self.SpeedMenu.size_hint  = (0.3, 0.2)
        layout.add_widget(self.SpeedMenu)

        # Parity
        self.ParityLabel = Label(text="Parity", color = WINDOW_COLOR)
        layout.add_widget(self.ParityLabel)
        self.ParityMenu = Spinner(text="Even", values=("Even", "Odd","None"), id = 'parity',
                                    color = OPTIONBUTTON_COLOR,
                                    background_color = OPTIONBUTTON_BACKGROUND,
                                    background_normal = '')
        self.ParityMenu.size_hint  = (0.3, 0.2)
        layout.add_widget(self.ParityMenu)

        # Databits
        self.DataBitsLabel = Label(text="Data bits", color = WINDOW_COLOR)
        layout.add_widget(self.DataBitsLabel)
        self.DataBitsMenu = Spinner(text="7", values=("7", "8"), id = 'databits',
                                    color = OPTIONBUTTON_COLOR,
                                    background_color = OPTIONBUTTON_BACKGROUND,
                                    background_normal = '')
        self.DataBitsMenu.size_hint  = (0.3, 0.2)
        layout.add_widget(self.DataBitsMenu)

        # Stopbits
        self.StopBitsLabel = Label(text="Stop bits", color = WINDOW_COLOR)
        layout.add_widget(self.StopBitsLabel)
        self.StopBitsMenu = Spinner(text="1", values=("0", "1", "2"), id = 'stopbits',
                                    color = OPTIONBUTTON_COLOR,
                                    background_color = OPTIONBUTTON_BACKGROUND,
                                    background_normal = '')
        self.StopBitsMenu.size_hint  = (0.3, 0.2)
        layout.add_widget(self.StopBitsMenu)

        button1 = Button(text = 'Save', size_hint_y = None, id = 'save',
                        color = BUTTON_COLOR,
                        background_color = BUTTON_BACKGROUND,
                        background_normal = '')
        layout.add_widget(button1)
        button1.bind(on_press = self.close_screen)
        button2 = Button(text = 'Back', size_hint_y = None, id = 'cancel',
                        color = BUTTON_COLOR,
                        background_color = BUTTON_BACKGROUND,
                        background_normal = '')
        layout.add_widget(button2)
        button2.bind(on_press = self.close_screen)

        self.add_widget(layout)

    def close_screen(self, instance):
        if instance.id=='save':
            for child in self.children[0].children:
                if child.id=='stopbits':
                    EDMpy.edm_station.stopbits = child.text
                if child.id=='baudrate':
                    EDMpy.edm_station.baudrate = child.text
                if child.id=='databits':
                    EDMpy.edm_station.databits = child.text
                if child.id=='comport':
                    EDMpy.edm_station.comport = child.text
                if child.id=='parity':
                    EDMpy.edm_station.parity = child.text
                if child.id=='communications':
                    EDMpy.edm_station.communications = child.text
                if child.id=='station':
                    EDMpy.edm_station.make = child.text
                ## need code to open com port here
        self.parent.current = 'MainScreen'


class AboutScreen(Screen):
    pass


class DebugScreen(Screen):
    pass


class LogScreen(Screen):
    pass


class StatusScreen(Screen):
    def __init__(self,**kwargs):
        super(StatusScreen, self).__init__(**kwargs)

        global edm_station, edm_datums, edm_units, edm_prisms
        global edm_cfg

        layout = GridLayout(cols = 1, size_hint_y = None)
        layout.bind(minimum_height=layout.setter('height'))
        txt = edm_station.status() + edm_datums.status() + edm_prisms.status()
        txt += edm_units.status()
        label = Label(text = txt, size_hint_y = None,
                     color = (0,0,0,1), id = 'content',
                     halign = 'left',
                     font_size = 20)
        layout.add_widget(label)
        label.bind(texture_size = label.setter('size'))
        label.bind(size_hint_min_x = label.setter('width'))
        button = Button(text = 'Back', size_hint_y = None,
                        color = BUTTON_COLOR,
                        background_color = BUTTON_BACKGROUND,
                        background_normal = '')
        root = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        root.add_widget(layout)
        self.add_widget(root)
        self.add_widget(button)
        button.bind(on_press = self.go_back)

    def on_pre_enter(self):
        global edm_station, edm_datums, edm_units, edm_prisms
        global edm_cfg
        for widget in self.walk():
            if widget.id=='content':
                txt = edm_station.status() + edm_datums.status() + edm_prisms.status()
                txt += edm_units.status() + edm_cfg.status()
                widget.text = txt

    def go_back(self, value):
        self.parent.current = 'MainScreen'


# Code from https://github.com/MichaelStott/DataframeGUIKivy/blob/master/dfguik.py

def create_dummy_data(size):

    user_ids = np.random.randint(1, 1000000, 10)
    product_ids = np.random.randint(1, 1000000, 100)

    def choice(*values):
        return np.random.choice(values, size)

    random_dates = [
        datetime.date(2016, 1, 1) + datetime.timedelta(days=int(delta))
        for delta in np.random.randint(1, 50, size)
    ]
    return pd.DataFrame.from_items([
        ("Date", random_dates),
        ("UserID", choice(*user_ids)),
        ("ProductID", choice(*product_ids)),
        ("IntColumn", choice(1, 2, 3)),
        ("FloatColumn", choice(np.nan, 1.0, 2.0, 3.0)),
        ("StringColumn", choice("A", "B", "C")),
        ("Gaussian 1", np.random.normal(0, 1, size)),
        ("Gaussian 2", np.random.normal(0, 1, size)),
        ("Uniform", np.random.uniform(0, 1, size)),
        ("Binomial", np.random.binomial(20, 0.1, size)),
        ("Poisson", np.random.poisson(1.0, size)),
    ])

class HeaderCell(Button):
    pass

class TableHeader(ScrollView):
    """Fixed table header that scrolls x with the data table"""
    header = ObjectProperty(None)

    def __init__(self, titles = None, *args, **kwargs):
        super(TableHeader, self).__init__(*args, **kwargs)

        for title in titles:
            self.header.add_widget(HeaderCell(text=title))

class ScrollCell(Label):
    text = StringProperty(None)
    is_even = BooleanProperty(None)

class TableData(RecycleView):
    nrows = NumericProperty(None)
    ncols = NumericProperty(None)
    rgrid = ObjectProperty(None)

    def __init__(self, list_dicts=[], column_names = None, *args, **kwargs):
        self.nrows = len(list_dicts)
        self.ncols = len(column_names)

        super(TableData, self).__init__(*args, **kwargs)

        self.data = []
        for i, ord_dict in enumerate(list_dicts):
            is_even = i % 2 == 0
            row_vals = ord_dict.values()
            for text in row_vals:
                self.data.append({'text': text, 'is_even': is_even})

    def sort_data(self):
        #TODO: Use this to sort table, rather than clearing widget each time.
        pass
        
class Table(BoxLayout):

    def __init__(self, list_dicts=[], column_names = None, *args, **kwargs):

        super(Table, self).__init__(*args, **kwargs)
        self.orientation = "vertical"

        self.header = TableHeader(column_names)
        self.table_data = TableData(list_dicts = list_dicts, column_names = column_names)

        self.table_data.fbind('scroll_x', self.scroll_with_header)

        self.add_widget(self.header)
        self.add_widget(self.table_data)

    def scroll_with_header(self, obj, value):
        self.header.scroll_x = value

class DataframePanel(BoxLayout):
    """
    Panel providing the main data frame table view.
    """

    def populate_data(self, df):
        self.df_orig = df
        self.original_columns = self.df_orig.columns[:]
        self.current_columns = self.df_orig.columns[:]
        self._disabled = []
        self.sort_key = None
        self._reset_mask()
        self._generate_table()

    def _generate_table(self, sort_key=None, disabled=None):
        self.clear_widgets()
        df = self.get_filtered_df()
        data = []
        if disabled is not None:
            self._disabled = disabled
        keys = [x for x in df.columns[:] if x not in self._disabled]
        if sort_key is not None:
            self.sort_key = sort_key
        elif self.sort_key is None or self.sort_key in self._disabled:
            self.sort_key = keys[0]
        for i1 in range(len(df.iloc[:, 0])):
            row = OrderedDict.fromkeys(keys)
            for i2 in range(len(keys)):
                row[keys[i2]] = str(df.iloc[i1, i2])
            data.append(row)
        data = sorted(data, key=lambda k: k[self.sort_key]) 
        self.add_widget(Table(list_dicts=data, column_names = df.columns))
        
    def apply_filter(self, conditions):
        """
        External interface to set a filter.
        """
        old_mask = self.mask.copy()

        if len(conditions) == 0:
            self._reset_mask()

        else:
            self._reset_mask()  # set all to True for destructive conjunction

            no_error = True
            for column, condition in conditions:
                if condition.strip() == '':
                    continue
                condition = condition.replace("_", "self.df_orig['{}']".format(column))
                print("Evaluating condition:", condition)
                try:
                    tmp_mask = eval(condition)
                    if isinstance(tmp_mask, pd.Series) and tmp_mask.dtype == np.bool:
                        self.mask &= tmp_mask
                except Exception as e:
                    print("Failed with:", e)
                    no_error = False

        has_changed = any(old_mask != self.mask)

    def get_filtered_df(self):
        return self.df_orig.loc[self.mask, :]

    def _reset_mask(self):
        pass
        self.mask = pd.Series([True] *
                              self.df_orig.shape[0],
                              index=self.df_orig.index)

class FilterPanel(BoxLayout):
    
    def populate(self, columns):            
        self.filter_list.bind(minimum_height=self.filter_list.setter('height'))
        for col in columns:
            self.filter_list.add_widget(FilterOption(columns))

    def get_filters(self):
        result=[]
        for opt_widget in self.filter_list.children:
            if opt_widget.is_option_set():
                result.append(opt_widget.get_filter())
        return [x.get_filter() for x in self.filter_list.children
                if x.is_option_set]

class FilterOption(BoxLayout):
        
    def __init__(self, columns, **kwargs):
        super(FilterOption, self).__init__(**kwargs)
        self.height="30sp"
        self.size_hint=(0.9, None)
        self.spacing=10
        options = ["Select Column"]
        options.extend(columns)
        self.spinner = Spinner(text='Select Column',
                               values= options,
                               size_hint=(0.25, None),
                               height="30sp",
                               pos_hint={'center_x': .5, 'center_y': .5})
        self.txt = TextInput(multiline=False, size_hint=(0.75, None),\
                             font_size="15sp")
        self.txt.bind(minimum_height=self.txt.setter('height'))
        self.add_widget(self.spinner)
        self.add_widget(self.txt)

    def is_option_set(self):
        return self.spinner.text != 'Select Column'

    def get_filter(self):
        return (self.spinner.text, self.txt.text)

class AddNewPanel(BoxLayout):
    
    def populate(self, columns, df_name):
        self.df_name = df_name            
        self.addnew_list.bind(minimum_height=self.addnew_list.setter('height'))
        for col in columns:
            self.addnew_list.add_widget(AddNew(col, df_name))
        self.addnew_list.add_widget(AddNew('Save', df_name))

    def get_addnews(self):
        result=[]
        for opt_widget in self.addnew_list.children:
            result.append(opt_widget.get_addnew())
        return(result)

class AddNew(BoxLayout):

    def __init__(self, col, df_name, **kwargs):
        super(AddNew, self).__init__(**kwargs)
        self.df_name = df_name
        self.widget_type = 'data'
        self.height="30sp"
        self.size_hint=(0.9, None)
        self.spacing=10
        if col=='Save':
            self.label = Label(text = "")
            self.button = Button(text = "Save", size_hint=(0.75, 1), font_size="15sp")
            self.button.bind(on_press = self.append_data)
            self.add_widget(self.label)
            self.add_widget(self.button)
            self.widget_type = 'button'
        else:
            self.label = Label(text = col)
            self.txt = TextInput(multiline=False, size_hint=(0.75, None), font_size="15sp")
            self.txt.bind(minimum_height=self.txt.setter('height'))
            self.add_widget(self.label)
            self.add_widget(self.txt)

    def get_addnew(self):
        return (self.label.text, self.txt.text)

    def append_data(self, instance):
        result = {}
        for obj in instance.parent.parent.children:
            if obj.widget_type=='data':
                result[obj.label.text] = obj.txt.text 
                obj.txt.text = ''
        new_data = pd.DataFrame(result, index=[result['Name']])
        if self.df_name == 'datums':
            EDMpy.edm_datums.datums = EDMpy.edm_datums.datums.append(new_data)
            EDMpy.edm_datums.save()
        elif self.df_name == 'prisms':
            EDMpy.edm_prisms.prisms = EDMpy.edm_prisms.prisms.append(new_data)
            EDMpy.edm_prisms.save()
        elif self.df_name == 'units':
            EDMpy.edm_units.units = EDMpy.edm_units.units.append(new_data)
            EDMpy.edm_units.save()

class DfguiWidget(TabbedPanel):

    def __init__(self, df, df_name, **kwargs):
        super(DfguiWidget, self).__init__(**kwargs)
        self.df = df
        self.df_name = df_name
        self.panel1.populate_data(df)
        #self.panel2.populate_columns(df.columns[:])
        self.panel3.populate(df.columns[:])
        self.panel4.populate(df.columns[:], df_name)
        #self.panel4.populate_options(df.columns[:])
        #self.panel5.populate_options(df.columns[:])

    # This should be changed so that the table isn't rebuilt
    # each time settings change.
    def open_panel1(self):
        arr = self.panel3.get_filters()
        #print(str(arr))
        self.panel1.apply_filter(self.panel3.get_filters())
        #self.panel1._generate_table(disabled=self.panel2.get_disabled_columns())
        self.panel1._generate_table()
    
    def cancel(self):
        pass

# End code from https://github.com/MichaelStott/DataframeGUIKivy/blob/master/dfguik.py

class YesNoCancel(Popup):
    def __init__(self, caption, cancel = False, **kwargs):
        super(YesNoCancel, self).__init__(**kwargs)
        box = BoxLayout()
        self.label = Label(text = caption)
        self.button1 = Button(text = "Yes", size_hint=(0.75, 1), font_size="15sp")
        self.button1.bind(on_press = self.yes)
        self.button2 = Button(text = "No", size_hint=(0.75, 1), font_size="15sp")
        self.button2.bind(on_press = self.no)
        box.add_widget(self.label)
        box.add_widget(self.button1)
        box.add_widget(self.button2)
        if cancel == True:
            box.button3 = Button(text = "Cancel", size_hint=(0.75, 1), font_size="15sp")
            box.button3.bind(on_press = self.cancel)
            box.add_widget(self.button3)
        self.add_widget(box)
        self.open()
    def yes(self, instance):
        return('Yes')
    def no(self, instance):
        return('No')
    def cancel(self, instance):
        return('Cancel')

class EDMpy(App):

    def build(self):
        Window.clearcolor = WINDOW_BACKGROUND
        self.title = "EDMpy 1.0"

        #sm.current = 'main'
        #df = create_dummy_data(0)
        #df = edm_datums.datums 
        #test = YesNoCancel("This is a test of a yes no popup box", cancel=False)
        #print(test)
        #return(DfguiWidget(EDMpy.edm_datums.datums, "datums"))
    
Factory.register('Root', cls=Root)
Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)
Factory.register('EDMpy', cls=EDMpy)

if __name__ == '__main__':
    logging.basicConfig(filename='EDMpy.log', filemode='w', level=logging.DEBUG)
    database = 'EDM'
    edm_ini = ini('EDMpy.ini')
    edm_station = totalstation()
    edm_cfg = cfg(edm_ini.get_value("EDM", "CFG"))
    edm_points = points(database + '_points.csv')
    edm_units = units(database + '_units.csv')
    edm_prisms = prisms(database + '_prisms.csv')
    edm_datums = datums(database + '_datums.csv')
    if not edm_cfg.filename:
        edm_cfg.filename = 'EDMpy.cfg'
    edm_cfg.save()
    edm_ini.update()
    edm_ini.save()
    
    EDMpy().run()