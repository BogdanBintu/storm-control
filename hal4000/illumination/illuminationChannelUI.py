#!/usr/bin/python
#
## @file
#
# This file contains the various ChannelUI classes.
#
# Hazen 04/14
#

from PyQt4 import QtCore, QtGui

## ChannelUI
#
# A QWidget for displaying the UI elements associated with
# an illumination channel.
#
class ChannelUI(QtGui.QFrame):
    onOffChange = QtCore.pyqtSignal(object)
    powerChange = QtCore.pyqtSignal(int)

    ## __init__
    #
    # @param name The name of the channel (a text string).
    # @param color The background color to use for the channel (RGB triple as a string).
    # @param parent The PyQt parent of this object.
    #
    def __init__(self, name, color, parent):
        QtGui.QFrame.__init__(self, parent)

        self.color = color
        self.enabled = True

        self.setLineWidth(2)
        self.setStyleSheet("background-color: rgb(" + self.color + ");")
        self.setFrameShape(QtGui.QFrame.Panel)
        self.setFrameShadow(QtGui.QFrame.Raised)
        self.resize(48, 204)

        # Text label.
        self.wavelength_label = QtGui.QLabel(self)
        self.wavelength_label.setGeometry(5, 5, 40, 10)
        self.wavelength_label.setText(name)
        self.wavelength_label.setAlignment(QtCore.Qt.AlignCenter)

        # Power on/off radio button.
        self.on_off_button = QtGui.QRadioButton(self)
        self.on_off_button.setGeometry(18, self.height() - 24, 18, 18)

        # Connect signals
        self.on_off_button.clicked.connect(self.handleOnOffChange)

    ## disableChannel
    #
    # Disables all the UI elements of the channel.
    #
    def disableChannel(self):
        self.setOnOff(False)
        self.setStyleSheet("background-color: rgb(128,128,128);")
        self.setFrameShadow(QtGui.QFrame.Sunken)
        self.wavelength_label.setStyleSheet("QLabel { color: rgb(200,200,200)}")
        self.on_off_button.setCheckable(False)
        self.enabled = False

    ## enableChannel
    #
    # enables all the UI elements of the channel.
    #
    def enableChannel(self):
        self.setStyleSheet("background-color: rgb(" + self.color + ");")
        self.setFrameShadow(QtGui.QFrame.Raised)
        self.wavelength_label.setStyleSheet("QLabel { color: black}")
        self.on_off_button.setCheckable(True)
        self.enabled = True

    ## getAmplitude
    #
    # @return The current amplitude (as a string).
    #
    def getAmplitude(self):
        if self.on_off_button.isChecked():
            return 1.0
        else:
            return 0.0

    ## handleOnOffChange
    #
    # Called when the on/off radio button is pressed.
    #
    # @param on_off The state of the radio button.
    #
    def handleOnOffChange(self, on_off):
        self.onOffChange.emit(on_off)

    ## isEnabled
    #
    # @return True/False if the channel is enabled.
    #
    def isEnabled(self):
        return self.enabled

    ## isOn
    #
    # @return True/False if the channel is on.
    #
    def isOn(self):
        return self.on_off_button.isChecked()

    ## newSettings
    #
    # @param on True/False if the on/off radio button is pressed.
    # @param power (int) The new power.
    #
    # @return [old state of on/off radio button, old power slider setting]
    #
    def newSettings(self, on, power):
        old_on = self.on_off_button.isChecked()
        if (old_on != on):
            self.setOnOff(on)
        return [old_on, 0]

    ## remoteIncPower
    #
    # @param power_inc (int) The power increment.
    #
    def remoteIncPower(self, power_inc):
        pass

    ## remoteSetPower
    #
    # @param new_power (int) The new power.
    #
    def remoteSetPower(self, new_power):
        if self.enabled:
            if (new_power > 0.5):
                self.setOnOff(self, true)
            else:
                self.setOnOff(self, false)

    ## setOnOff
    #
    # Programmatically sets the state of the on/off button. This
    # also generates event that the button changed state.
    #
    # @param state True/False.
    #
    def setOnOff(self, state):
        self.on_off_button.setChecked(state)
        self.handleOnOffChange(state)

    ## setupButtons
    #
    # @param button_data An array of button data for this channel.
    #
    def setupButtons(self, button_data):
        pass

    ## startFilm
    #
    # Checks the on/off button and disables it.
    #
    def startFilm(self):
        self.on_off_button.setEnabled(False)

    ## stopFilm
    #
    # Enables the on/off button.
    def stopFilm(self):
        self.on_off_button.setEnabled(True)


## ChannelUIAdjustable.
#
# A QWidget for displaying the UI elements associated with
# an adjustable illumination channel.
#
class ChannelUIAdjustable(ChannelUI):

    ## __init__
    #
    # @param name The name of the channel (a text string).
    # @param color The background color to use for the channel (RGB triple as a string).
    # @param minimum The minimum amplitude for this channel.
    # @param maximum The maximum amplitude for this channel.
    # @param parent The PyQt parent of this object.
    #
    def __init__(self, name, color, minimum, maximum, parent):
        ChannelUI.__init__(self, name, color, parent)

        self.buttons = []
        self.cur_y = 202
        self.max_amplitude = maximum
        self.min_amplitude = minimum

        # Current power label.
        self.power_label = QtGui.QLabel(self)
        self.power_label.setGeometry(5, 19, 40, 10)
        self.power_label.setText("")
        self.power_label.setAlignment(QtCore.Qt.AlignCenter)

        # Slider for controlling the power.
        self.powerslider = QtGui.QSlider(self)
        self.powerslider.setGeometry(13, 34, 24, 141)
        self.powerslider.setMinimum(minimum)
        self.powerslider.setMaximum(maximum)
        page_step = 0.1 * (maximum - minimum)
        if (page_step > 1.0):
            self.powerslider.setPageStep(page_step)
        self.powerslider.setSingleStep(1)
        self.powerslider.valueChanged.connect(self.handleAmplitudeChange)

    ## disableChannel
    #
    # Disables all the UI elements of the channel.
    #
    def disableChannel(self):
        ChannelUI.disableChannel(self)
        self.power_label.setStyleSheet("QLabel { color: rgb(200,200,200)}")
        self.powerslider.setEnabled(False)
        for button in self.buttons:
            button.setEnabled(False)

    ## enableChannel
    #
    # enables all the UI elements of the channel.
    #
    def enableChannel(self):
        ChannelUI.enableChannel(self)
        self.power_label.setStyleSheet("QLabel { color: black}")
        self.powerslider.setEnabled(True)
        for button in self.buttons:
            button.setEnabled(True)

    ## getAmplitude
    #
    # @return The current amplitude.
    #
    def getAmplitude(self):
        return self.powerslider.value()

    ## handleAmplitudeChange
    #
    # @param amplitude The new slider amplitude value.
    #
    def handleAmplitudeChange(self, amplitude):
        self.powerChange.emit(amplitude)

    ## newSettings
    #
    # @param on True/False if the on/off radio button is pressed.
    # @param power (int) The new power.
    #
    # @return [old state of on/off radio button, old power slider setting]
    #
    def newSettings(self, on, power):
        old_on = self.on_off_button.isChecked()
        old_power = self.powerslider.value()
        if (old_on != on):
            self.setOnOff(on)
        if (old_power != power):
            self.setAmplitude(power)
        return [old_on, old_power]

    ## remoteIncPower
    #
    # @param power_inc (int) The power increment.
    #
    def remoteIncPower(self, power_inc):
        if self.enabled:
            self.setAmplitude(self.powerslider.value() + power_inc)

    ## remoteSetPower
    #
    # @param new_power (int) The new power.
    #
    def remoteSetPower(self, new_power):
        if self.enabled:
            self.setAmplitude(new_power)

    ## setAmplitude
    #
    # @param amplitude The new value for the power slider.
    #
    def setAmplitude(self, amplitude):
        self.powerslider.setValue(amplitude)

    ## setupButtons
    #
    # @param button_data An array of button data for this channel.
    #
    def setupButtons(self, button_data):

        # Make sure we have enough buttons.
        while (len(self.buttons) < len(button_data)):
            new_button = PowerButton(self.cur_y, self)
            new_button.powerChange.connect(self.setAmplitude)
            self.buttons.append(new_button)
            self.cur_y += 22

        # Hide all the buttons.
        for button in self.buttons:
            button.hide()

        # Set text and value of the buttons we'll use & show them.
        amp_range = float(self.max_amplitude - self.min_amplitude)
        for i in range(len(button_data)):
            self.buttons[i].setText(button_data[i][0])
            self.buttons[i].setValue(int(round(button_data[i][1] * amp_range + self.min_amplitude)))
            self.buttons[i].show()

        # Resize based on number of visible buttons.
        self.resize(50, 204 + 22 * len(button_data))

    ## updatePowerText
    #
    # @param new_text The new text string to display.
    #
    def updatePowerText(self, new_text):
        self.power_label.setText(new_text)


## PowerButton
#
# A push button specialized for amplitude / power control.
#
class PowerButton(QtGui.QPushButton):
    powerChange = QtCore.pyqtSignal(int)

    ## __init__
    #
    # @param y_loc Where to draw the button in y.
    # @param parent The PyQt parent of the button.
    #
    def __init__(self, y_loc, parent):
        QtGui.QPushButton.__init__(self, parent)

        self.value = 0.0
        self.setGeometry(6, y_loc, 38, 20)
        self.setStyleSheet("background-color: None;")

        self.clicked.connect(self.handleClicked)

    ## handleClicked
    #
    # @param boolean Dummy parameter.
    #
    def handleClicked(self, boolean):
        self.powerChange.emit(self.value)

    ## setValue
    #
    # @param value The value this button will emit when clicked.
    #
    def setValue(self, value):
        self.value = value

#
# The MIT License
#
# Copyright (c) 2014 Zhuang Lab, Harvard University
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
