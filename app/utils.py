from passlib.context import CryptContext
pwd_context = CryptContext(schemes=['bcrypt'],deprecated="auto")

def hasher(passowrd:str):
    return pwd_context.hash(passowrd)

def verify(password,hashed_password):
    return pwd_context.verify(password,hashed_password)