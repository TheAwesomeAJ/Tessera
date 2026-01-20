import base64, os

secret = base64.b32encode(os.urandom(20)).decode('utf-8')  # 20 random bytes
print(secret)