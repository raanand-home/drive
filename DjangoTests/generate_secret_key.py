__author__ = 'Elad'

from django.utils.crypto import get_random_string

def generate_secret_key(path):
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    with open(path, 'w') as f:
        f.write("SECRET_KEY = '" + get_random_string(50, chars) + "'\n")

