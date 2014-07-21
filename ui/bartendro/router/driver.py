import sys
import os
import collections
import logging
from subprocess import call
from time import sleep, localtime, time
from dispense_for_duration_thread import DispenseForDurationThread
import random


#import RPi GPIO if this is not available import the RPi GPIO simulation

try:
    import RPi.GPIO as GPIO
except ImportError:
  
    print "\nUnable to import RPi.GPIO! Automatically switched to simulation mode!!! If you are on a Raspberry Pi try sudo apt-get install python-rpi.gpio -y\n"
    import RPiSIM.GPIO as GPIO

#add all gpios here which are connected to a pump/valve, they will be numerated in the order of appearance
GPIOOutputs = [22, 27]

MOTOR_DIRECTION_FORWARD       = 1
MOTOR_DIRECTION_BACKWARD      = 0

log = logging.getLogger('bartendro')

class Dispenser():
    
    def __init__(self, gpio):
        self.gpio = gpio
        self.dispensing = False
        self.dispensing_thread = None
        
    def get_gpio_number(self):
        return self.gpio
    
    def pour_for_duration(self, duration):
        self.dispensing_thread = DispenseForDurationThread(self, duration).start()
            
    def start_dispensing(self):
        GPIO.output(self.gpio, GPIO.LOW)
        self.dispensing = True
        log.info("GPIO: " + str(self.gpio) + " start dispensing.\n")
        #todo error handling 
        return True
        
    def stop_dispensing(self):
        GPIO.output(self.gpio, GPIO.HIGH)
        self.dispensing = False
        log.info("GPIO: " + str(self.gpio) + " stop dispensing.\n")
        #todo error handling 
        return True
        
    def is_dispensing(self):
        return self.dispensing
    

class RouterDriver(object):
    '''This object interacts with the bartendro router controller.'''

    def __init__(self, device, software_only, no_router=False):
        log.info("Starting Driver.\n")
        self.software_only = software_only
        self.dispensers = []
        #add dispensers
        for gpio in GPIOOutputs:
            self.dispensers.append(Dispenser(gpio))
            
        self.startup_log = ""
        self.num_dispensers = len(self.dispensers)
        self.dispenser_version = 0
 
    def get_startup_log(self):
        return self.startup_log
    
    def get_dispenser_version(self):
        return self.dispenser_version

    def reset(self):
        """Reset the hardware. Do this if there is shit going wrong. All motors will be stopped
           and reset."""
        log.info("Reset Hardware. Not implemented.\n")
        
        if self.software_only: return
         
        #TODO: reset
   
    def count(self):
        return self.num_dispensers

    def open(self):
        '''Setup GPIOs'''
        log.info("Setup GPIOS.\n")

        if self.software_only: return

        # use GPIO pin numbering convention (not the actual pin numbers)
        GPIO.setmode(GPIO.BCM)
        
        #define all gpios given in gpiooutputs as outputs
        for dispenser in self.dispensers:
            GPIO.setup(dispenser.get_gpio_number(), GPIO.OUT)
            GPIO.output(dispenser.get_gpio_number(), GPIO.HIGH)

        self._clear_startup_log()

    def close(self):
        if self.software_only: return
        
        #todo close connection

    def log(self, msg):
        return
        if self.software_only: return
        try:
            t = localtime()
            self.cl.write("%d-%d-%d %d:%02d %s" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, msg))
            self.cl.flush()
        except IOError:
            pass

    def dispense_time(self, dispenser, duration):
        log.info("Start dispensing on dispenser " + str(dispenser) + " for " + str(duration) + " seconds.\n")
        if self.software_only: return True     
        self.dispensers[dispenser].pour_for_duration(duration)
        return True

    def ping(self, dispenser):
        log.info("Ping not implemented.\n")
        if self.software_only: return True
        return True

    def start(self, dispenser):
        if self.software_only: return True
        return self.dispensers[dispenser].start_dispensing()
  
    def stop(self, dispenser):
        if self.software_only: return True
        return self.dispensers[dispenser].stop_dispensing()
       
    def is_dispensing(self, dispenser):
        """
        Returns a tuple of (dispensing, is_over_current) 
        """
        if self.software_only: return (False, False)
        return (self.dispensers[dispenser].is_dispensing(), False)
       
    def set_motor_direction(self, dispenser, direction):
        log.info("Set motor direction to " + str(direction) + ".\n")
        if self.software_only: return True
        #todo set motor direction
        return True

    def update_liquid_levels(self):
        log.info("Update liquid level.\n")
        if self.software_only: return True
        return True


    def get_liquid_level(self, dispenser):
        log.info("Get liquid level.\n")
        if self.software_only: return 100
        #todo liquid level?
        return 100

    def get_liquid_level_thresholds(self, dispenser):
        log.info("Get liquid level thersholds.\n")
        if self.software_only: return True
        return True
        
                
    def set_liquid_level_thresholds(self, dispenser, low, out):
        log.info("Set liquid level thersholds. Low: " + str(low) + " Out: " + str(out) + "\n")
        if self.software_only: return True
        return True


    def _clear_startup_log(self):
        self.startup_log = ""

    def _log_startup(self, txt):
        log.info(txt)
        self.startup_log += "%s\n" % txt
