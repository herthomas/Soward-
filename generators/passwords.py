from random import choice

def generate_password(lenth=8) -> str:
    latters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$_"
    password = ''.join(choice(latters) for i in range(lenth))
    return password
