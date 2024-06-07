from abc import ABC, abstractmethod
import shepard_effect
from types import SimpleNamespace
import keyboard
from leds_manager import LedsManager
from logger import defaultLogger as log
import RPi.GPIO as GPIO
import requests
import time

class Subscriber(ABC):
    @abstractmethod
    def handle_event(self, event):
        pass


class EventBus(ABC):
    def __init__(self):
        self._subscribers = []

    def subscribe(self, subscriber: Subscriber):
        self._subscribers.append(subscriber)

    def unsubscribe(self, subscriber:Subscriber):
        self._subscribers.remove(subscriber)

    def post(self, event):
        for subscriber in self._subscribers:
            subscriber.handle_event(event)

    @abstractmethod
    def wait_for_events(self):
        pass



class GpioEventBus(EventBus):
    
    EXPLAIN_BUTTON_PIN = 9

    def __init__(self, leds_manager: LedsManager): # dirty but late
        super().__init__()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(GpioEventBus.EXPLAIN_BUTTON_PIN, GPIO.OUT)
        self.leds_manager = leds_manager

    def wait_for_events(self):
        log.info('Waiting for gpio events')
        last_read = GPIO.input(GpioEventBus.EXPLAIN_BUTTON_PIN)
        while True:
            try:
                new_read = GPIO.input(GpioEventBus.EXPLAIN_BUTTON_PIN)
                if new_read != last_read:
                    event = SimpleNamespace(pin=GpioEventBus.EXPLAIN_BUTTON_PIN, value=new_read, type='explain',
                                            pressed=True if new_read == 1 else False)
                    self.post(event)
                    last_read = new_read
                leds_maintain()
                # self.leds_manager.maintainance()
            except Exception as e:
                log.error('Error while waiting for gpio events: %s', e)
                    

last_execution_time = 0

def leds_maintain():
    global last_execution_time
    current_time = time.time()
    if current_time - last_execution_time >= 5:
        try:
            response = requests.get('http://localhost:5000/maintain')
            log.info('Response from leds maintenance: %s', response.text)
            last_execution_time = current_time
        except Exception as e:
            log.error('Error while calling leds maintenance: %s', e)

class KeyboardEventBus(EventBus):
    def wait_for_events(self):
        log.info('Waiting for keyboard events')
        while True:
            try:
                event = keyboard.read_event()
                log.info('Received keyboard event: %s: %s', event, event.__dict__)
                if event.scan_code == 12:  # the buttun 'q'
                    event.type = 'contact'
                if event.scan_code == 14:  # the button 'e'
                    event.type = 'explain'
                self.post(event) 
            except Exception as e:
                log.error('Error while waiting for events: %s', e)

