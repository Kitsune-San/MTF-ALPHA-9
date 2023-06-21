from utilities import load_json
from assets import jsonfiles
from pyDes import *
loader = load_json(jsonfiles)
eck = loader['key']

def ecypt(message:str):
    """Encrypts data using `triple_des()`"""
    tte = triple_des(eck).encrypt(message, padmode=2)
    #padmode 1 for pkcs5 padding and mode 0 for ecb. Mode
    return tte

def dcypt(message:str):
    """Decrypts data using `triple_des()`"""
    ttd = triple_des(eck).decrypt(message)
    return ttd



if __name__ == "__main__":
    print(dcypt())