#!/usr/bin/python
#
# Joystick monitoring class.
#
# Hazen 09/12
# Jeff 09/12

from PyQt4 import QtCore

# Debugging
import halLib.hdebug as hdebug

#
# Joystick monitoring class.
#
class JoystickObject(QtCore.QObject):
    lock_jump = QtCore.pyqtSignal(float)
    motion = QtCore.pyqtSignal(float, float)
    step = QtCore.pyqtSignal(int, int)
    toggle_film = QtCore.pyqtSignal()

    @hdebug.debug
    def __init__(self, parameters, joystick, parent = None):
        QtCore.QObject.__init__(self, parent)
        self.button_timer = QtCore.QTimer(self)
        self.jstick = joystick
        self.parameters = parameters
        self.parameters.joystick_gain_index = 0
        self.parameters.multiplier = 1
        self.old_right_joystick = [0, 0]
        self.old_left_joystick = [0, 0]
        self.to_emit = False

        self.jstick.start(self.joystickHandler)

        self.button_timer.setInterval(100)
        self.button_timer.setSingleShot(True)
        self.button_timer.timeout.connect(self.buttonDownHandler)

    def buttonDownHandler(self):
        if self.to_emit:
            self.to_emit()
            self.button_timer.start()

    @hdebug.debug
    def close(self):
        self.jstick.shutDown()

    def hatEvent(self, sx, sy):
        p = self.parameters
        sx = sx*p.hat_step*p.joystick_signx
        sy = sy*p.hat_step*p.joystick_signy

        if p.xy_swap:
            self.step.emit(sy, sx)
        else:
            self.step.emit(sx,sy)

    def rightJoystickEvent(self, x_speed, y_speed):
        # the right joystick is not currently used
        pass
        
    def leftJoystickEvent(self, x_speed, y_speed):
        p = self.parameters

        if(abs(x_speed) > p.min_offset) or (abs(y_speed) > p.min_offset):
            if (p.joystick_mode == "quadratic"):
                x_speed = x_speed * x_speed * cmp(x_speed, 0.0)
                y_speed = y_speed * y_speed * cmp(y_speed, 0.0)

                # x_speed and y_speed range from -1.0 to 1.0.
                # convert to units of microns per second
                gain = p.multiplier*p.joystick_gain[p.joystick_gain_index]
                x_speed = gain*x_speed*p.joystick_signx
                y_speed = gain*y_speed*p.joystick_signy

                # The stage and the joystick might have different ideas
                # about which direction is x.
                if p.xy_swap:
                    self.motion.emit(y_speed, x_speed)
                else:
                    self.motion.emit(x_speed, y_speed)
        else:
            self.motion.emit(0.0, 0.0)
        
    def joystickHandler(self, data):
        p = self.parameters
        events = self.jstick.dataHandler(data)

        for [e_type, e_data] in events:
            # Buttons
            if(e_type == "left upper trigger") and (e_data == "Press"): # focus up
                self.lock_jump.emit(p.multiplier*p.lockt_step)
            elif(e_type == "left lower trigger") and (e_data == "Press"): # focus down
                self.lock_jump.emit(-p.multiplier*p.lockt_step)
            elif(e_type == "right upper trigger") and (e_data == "Press"): # start/stop film
                self.toggle_film.emit()
            elif(e_type == "back") and (e_data == "Press"): # emergency stage stop
                self.motion.emit(0.0, 0.0)
            elif(e_type == "left joystick press") and (e_data == "Press"): # toggle movement gain
                p.joystick_gain_index += 1
                if(p.joystick_gain_index == len(p.joystick_gain)):
                    p.joystick_gain_index = 0
            elif(e_type == "X"): # engage/disengage movement multiplier
                if (e_data == "Press"):
                    p.multiplier = p.joystick_multiplier_value 
                else: # "Release"
                    p.multiplier = 1
                # Recall joystick event to reflect changes in gain
                self.leftJoystickEvent(self.old_left_joystick[0], self.old_left_joystick[1])

            # Hat
            elif(e_type == "up") and (e_data == "Press"):
                self.hatEvent(0.0,-1.0)
            elif(e_type == "down") and (e_data == "Press"):
                self.hatEvent(0.0,1.0)
            elif(e_type == "left") and (e_data == "Press"):
                self.hatEvent(-1.0,0.0)
            elif(e_type == "right") and (e_data == "Press"):
                self.hatEvent(1.0,0.0)

            # Joysticks
            elif (e_type == "left joystick"):
                self.leftJoystickEvent(e_data[0], e_data[1])
                self.old_left_joystick = e_data # remember joystick state

#
# The MIT License
#
# Copyright (c) 2012 Zhuang Lab, Harvard University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
