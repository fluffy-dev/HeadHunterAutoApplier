from hh.libs.exceptions import AlreadyExists, NotFound

#User
class UserAlreadyExist(AlreadyExists):
    pass

class UserNotFound(NotFound):
    pass

#Auth
class CredentialsException(Exception):
    pass
