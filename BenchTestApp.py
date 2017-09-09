from pyfirmata import Arduino, util
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



class CtrlPanel(BoxLayout):
    uno = ArduinoUnoHandler()
    connected = 'Disconnected'
    update_inputs_flag = False
    #pin_labels[ObjectProperty() for range(12)]

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
        #Clock.unschedule(self.pyfirmata_update)
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

    def set_update_flag(self):
        if self.update_inputs_flag == False:
            self.update_inputs_flag = True
            self.ids['update_btn'].text = 'Stop Updating Inputs'
        elif self.update_inputs_flag == True:
            self.update_inputs_flag = False
            self.ids['update_btn'].text = 'Update Inputs'            

    def build(self):
        pass

class BenchTestApp(App):
    def build(self):
        return CtrlPanel()

if __name__ == '__main__':
    BenchTestApp().run()
