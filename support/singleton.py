class Singleton:
    '''
    Non thread safe helper class to ease implementing singleton patterns.
    This should be used as a decorator to the class that should be a singleton.

    The decorated class can define one '__init__' function that takes only
    the 'self' argument. Other than that, there are no restrictions that apply
    to the decorated class.

    To get the singleton instance, use the 'Instance' method. Trying to use
    '__call__' will result in a 'TypeError' being raised.

    Limitations: The decorated class cannot be inherited from.
    '''
    def __init__(self,decorated):
        self.__decorated = decorated
    def ins(self):
        '''
        Returns the singleton instance. Upon its firsct call, it creates a new
        instance of the decorated class and calls its '__init__' method.
        On all subsequent calls, the already created instance is returned
        '''
        try:
            return self.__instance
        except AttributeError:
            self.__instance = self.__decorated()
            return self.__instance

    def __call__(self):
        raise TypeError("Singletons must be accessed through 'ins()'.")
    def __instancecheck__(self,inst):
        return isinstance(inst,self.__decorated)
