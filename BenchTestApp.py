from pyfirmata import Arduino, util
import logging
import time

import kivy

kivy.require('1.10.0') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty
from kivy.clock import Clock


class ArduinoUnoHandler:

    #Change the port to match your own setup (e.g. COM1, /dev/ttyACM0, etc.)
    port = 'COM4'
    
    board = None
    connected = 'Disconnected'
    di_states = ['0' for i in range(12)]
    thread = None

    def connect(self):
        try:
            self.board = Arduino(self.port)
            thread = util.Iterator(self.board)
            thread.start()
            for i in range(12):
                self.board.digital[i+2].mode = 0
            for i in range(6):
                self.board.analog[i].enable_reporting()
            self.connected = 'Connected'
            return True
        except:
            self.connected = 'Error'
            return False

    def disconnect(self):
        try:
            self.board.exit()
            self.connected = 'Disconnected'
            return True
        except:
            self.connected = 'Error'
            return False

    def get_digital(self, pin):
        if self.board.digital[pin].mode == 0:
            return not self.board.digital[pin].read()
        else:
            return False

    def set_digital(self, pin, val):
        if self.board.digital[pin].mode == 1:
            self.board.digital[pin].write(val)

    def set_mode(self, pin, mode):
        self.board.digital[pin].mode = mode

    def get_analog(self, pin):
        return self.board.analog[pin].read()
        

class CtrlPanel(BoxLayout):
    uno = ArduinoUnoHandler()
    connected = 'Disconnected'
    update_inputs_flag = False
    anal_visible = True
    #LOG_FILENAME = 'save_file.txt'
    logger = logging.getLogger()
    
    def setup_logger(self):
        handler = logging.FileHandler('save_file.txt')
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        self.logger.debug('often makes a very good meal of %s', 'visiting tourists')
    
    def pyfirmata_connect(self):
        self.ids['con_stat_lbl'].text = 'Connecting...'
        Clock.schedule_interval(self.pyfirmata_update, 0.1)
        if self.uno.connect():
            self.ids['con_stat_lbl'].text = self.uno.connected
            self.ids['con_btn'].disabled = True
            for i in range(12):
                pin = i+2
                self.ids['pin' + str(pin) + '_mode_di'].disabled = False
        else:
            return False

    def pyfirmata_disconnect(self):
        self.ids['con_stat_lbl'].text = 'Disconnecting...'
        Clock.unschedule(self.pyfirmata_update)
        if self.uno.disconnect():
            self.ids['con_stat_lbl'].text = self.uno.connected
            self.ids['con_btn'].disabled = False
            for i in range(12):
                pin = i+2
                self.ids['pin' + str(pin) + '_mode_di'].disabled = True
        else:
            return False

    def set_modes(self):
        if self.uno.connected == 'Connected':
            for i in range(12):
                pin = i+2
                if self.ids['pin' + str(pin) + '_mode_di'].active == True:
                    self.ids['pin' + str(pin) + '_do'].disabled = True
                    self.uno.set_mode(pin, 0)
                elif self.ids['pin' + str(pin) + '_mode_di'].active == False:
                    self.ids['pin' + str(pin) + '_do'].disabled = False
                    self.uno.set_mode(pin, 1)

    def set_outputs(self):
        if self.uno.connected == 'Connected':
            for i in range(12):
                pin = i+2
                if self.ids['pin' + str(pin) + '_do'].active == True:
                    self.uno.set_digital(pin, 1)  
                elif self.ids['pin' + str(pin) + '_do'].active == False:
                    self.uno.set_digital(pin, 0)

    def pyfirmata_update(self, dt):
        if self.uno.connected == 'Connected' and self.update_inputs_flag == True:
            for i in range(12):
                pin = i+2
                if self.uno.board.digital[pin].mode == 0:
                    self.ids['pin' + str(pin) + '_state'].text = str(self.uno.get_digital(pin))
            for i in range(6):
                pin = i
                self.ids['pinA' + str(pin) + '_val'].text = str(self.uno.get_analog(pin))

    def set_update_flag(self):
        if self.update_inputs_flag == False:
            self.update_inputs_flag = True
            self.ids['update_btn'].text = 'Stop Updating Inputs'
        elif self.update_inputs_flag == True:
            self.update_inputs_flag = False
            self.ids['update_btn'].text = 'Update Inputs'            

    def hide_anal(self):
        self.anal_visible = not self.anal_visible
        if(self.anal_visible):
            self.ids['anal_layout'].size_hint_x = 0.3
            self.ids['anal_layout'].padding = 10
            self.ids['anal_layout_lbl'].size_hint_y = 0.1
            self.ids['hide_anal_btn'].text = 'Hide Analog'
        else:
            self.ids['anal_layout'].size_hint_x = 0
            self.ids['anal_layout'].padding = 0
            self.ids['anal_layout_lbl'].size_hint_y = 0
            self.ids['hide_anal_btn'].text = 'Show Analog'

    def save_lbls(self):
        self.ids['save_btn'].disabled = True
        for i in range(12):
            self.logger.info(self.ids['desc' + str(i+1)].text)
            self.ids['save_btn'].disabled = True
            time.sleep(0.2)
        self.ids['save_btn'].disabled = False

    def build(self):
        pass

class BenchTestApp(App):
    def build(self):
        cp = CtrlPanel()
        cp.setup_logger()
        return cp


if __name__ == '__main__':
    BenchTestApp().run()
