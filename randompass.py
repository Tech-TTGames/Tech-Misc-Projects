'''Generate Random Passwords Safe for server use.'''
import secrets
import string
import argparse

import pyperclip

def generate_password(length: int = 12, special: bool = False) -> str:
    '''Generate a random password of length using cryptographically secure random numbers.'''
    chars = string.ascii_letters + string.digits
    if special:
        chars += string.punctuation
    return ''.join(secrets.choice(chars) for _ in range(length))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a random password.')
    parser.add_argument('-l', '--length', type=int, default=12, help='Length of the password.')
    parser.add_argument('-s', '--special', action='store_true', help='Use special characters.')
    args=parser.parse_args()
    pyperclip.copy(generate_password(args.length,args.special))
    print(f'Password of length {args.length} copied to clipboard.')
