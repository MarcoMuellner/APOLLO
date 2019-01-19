from support.printer import print_int

class InputFileNotFound(Exception):
    def __init__(self, message,kwargs):
        super().__init__(message)
        print_int("NoFile",kwargs)


class ResultFileNotFound(Exception):
    def __init__(self, message,kwargs,err):
        message += f"\nErrormessage:{err}"
        super().__init__(message)
        print_int("summaryErr",kwargs)


class EvidenceFileNotFound(Exception):
    def __init__(self, message,kwargs):
        super().__init__(message)
        print_int("EvidenceErr",kwargs)
