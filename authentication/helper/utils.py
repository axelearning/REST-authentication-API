from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import smart_bytes, smart_str
from rest_framework.exceptions import ParseError


def raise_exception(message):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception:
                raise Exception(message)
        return wrapper
    return decorator


# Base64
def encode_base64(id:int)->str:
    bytes = smart_bytes(id)
    uidb64 = urlsafe_base64_encode(bytes)
    return uidb64

def decode_base64(uidb64:str)->int:
    try:
        bytes = urlsafe_base64_decode(uidb64)
        id = int(smart_str(bytes))
    except:
        raise ParseError('Decoding uidb64 failed', code=400)
    else:
        return id

