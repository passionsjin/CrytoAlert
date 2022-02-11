import json
import traceback
from base64 import b64decode
from zlib import decompress, MAX_WBITS


def process_message(message):
    try:
        decompressed_msg = decompress(b64decode(message, validate=True), -MAX_WBITS)
    except SyntaxError:
        decompressed_msg = decompress(b64decode(message, validate=True))
    return json.loads(decompressed_msg.decode())


def is_integer(n):
    try:
        int(n)
    except ValueError:
        return False
    else:
        return True


def is_float(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return True


def is_number(n):
    return True if is_integer(n) or is_float(n) else False


def except_hook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("error catched!:")
    print("error message:\n", tb)