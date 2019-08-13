import serial
import time
import threading
import os
import stat
from commands import commands
from serial import SerialException

class ELM327(object):
    def __init__(self, baudrate, timeout):
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.threads = []

    def _connect(self):
        print "Attempting to Connect"
        try:
                stat.S_ISBLK(os.stat("/dev/rfcomm0").st_mode)
        except:
            os.system("sudo rfcomm bind rfcomm0 00:1D:A5:02:86:67")
        try:
            self.ser = serial.Serial('/dev/rfcomm0', baudrate=self.baudrate, timeout=self.timeout)
            if self.ser.isOpen():
                print "Connection with: {0} established".format(self.ser.name)

                self.ser.flushInput()
                self.ser.write('ATZ\r')
                self.ser.flushOutput()
                self.ser.flushInput()
                self.ser.write('astp0\r')
                self.ser.flushOutput()
                self.ser.flushInput()
                self.ser.write('ath0\r')
                print "Testing Connection: ", self._read()
                time.sleep(1)
                self.ser.flushInput()
                self.ser.flushOutput()
                print "Connection Succesful"
            else:
                print "Connection Error"

        except SerialException:
            print "Serial Exception Error"

    def _command(self, cmd):
        if self.ser.isOpen():
            msg = cmd.cmd
            msg += "\r"
            self.ser.write(msg)
            return self._read(cmd.byte_length, cmd.decoder)

    def _multiple_commands(self, **kwargs):
        if kwargs is not None:
            for k, v in kwargs.iteritems():
                thread = threading.Thread(target=self._command, args=(v,))
                self.threads.append(thread)
                print k, v

            for thread in self.threads:
                if not thread.is_alive():
                    thread.start()
                    thread.join()

    def _read(self, byte_length=None, decoder=None):
        if self.ser.isOpen():
            print byte_length
            data = self.ser.readline().split(' ')
            if byte_length == 1:
                # print "BYTES: ", byte_length
                data = data[-2]
            elif byte_length == 2:
                # print "BYTES: ", byte_length
                data = data[-2].join(data[-3])
            if decoder != None:
                return decoder(data)
            return data

    def _test_cmd(self):
        if self.ser.isOpen():
            self.ser.write("ATZ\r")
            self.ser.flushInput()
            self.ser.flushOutput()
            if self.ser.readline() != '':
                return self.ser.readline().split(' ')
