from abc import ABC, abstractmethod
import keyboard
from logger import log
import pdb

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
    def wait_for_events(self):
        pass

class KeyboardEventBus(EventBus):
    def wait_for_events(self):
        while True:
            event = keyboard.read_event()
            log.info('Received keyboard event: %s: %s', event, event.__dict__)
            if event.scan_code == 12:  # the buttun 'q'
                event.type = 'contact'
            if event.scan_code == 14:  # the button 'e'
                event.type = 'explain'
            self.post(event) 
