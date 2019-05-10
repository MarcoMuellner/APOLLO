from support.printer import print_int

class InputFileNotFound(Exception):
    def __init__(self, message,kwargs):
        super().__init__(message)


class ResultFileNotFound(Exception):
    def __init__(self, message,kwargs,err):
        message += f"\nErrormessage:{err}"
        super().__init__(message)


class EvidenceFileNotFound(Exception):
    def __init__(self, message,kwargs):
        super().__init__(message)
