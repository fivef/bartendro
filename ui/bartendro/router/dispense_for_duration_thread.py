# -*- coding: utf-8 -*-
from time import sleep, time
from threading import Thread

class DispenseForDurationThread(Thread):
    def __init__(self, dispenser, duration):
        Thread.__init__(self)
        self.dispenser = dispenser
        self.duration = duration

    def run(self):
        self.dispenser.start_dispensing()       
        sleep(self.duration)
        self.dispenser.stop_dispensing()
