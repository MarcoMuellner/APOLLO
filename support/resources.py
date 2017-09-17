#Library Import
from multiprocessing import Queue
from threading import Lock
#Application Import
from support.singleton import Singleton


@Singleton
class ResourceHandler:
    """
    Simple Multithreading resource handler. Locks a resource for a different thread if this is applied.
    Can also be used for managing resources.
    """
    def __init__(self):
        self.__map = {}
        self.__lock = Lock()
        return
    def getResource(self,name):
        if type(name) is not str:
            #log here
            raise TypeError

        self.__lock.acquire()
        try:
            if name in self.__map:
                return self.__map[name]
            else:
                newQueue = Queue()
                self.__map[name] = newQueue
                return self.__map[name]
        finally:
            self.__lock.release()

