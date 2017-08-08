class _BaseException(Exception):
    def __init__(self, message, *args):
        super(_BaseException, self).__init__(*args)
        self.message = message


class WrongCredential(_BaseException):
    pass


class WrongParameters(_BaseException):
    pass


class NfvoException(_BaseException):
    pass


class NotFoundException(_BaseException):
    pass


class SdkException(_BaseException):
    pass
