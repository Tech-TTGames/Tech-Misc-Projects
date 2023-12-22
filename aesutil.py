"""General AES cipher utilities in python."""
import secrets
import argparse
import base64

import pyperclip
from Crypto.Cipher import AES


def keygen(length: int = 256) -> str:
    """Generate a random AES key of length using cryptographically secure random numbers."""
    return (base64.b64encode(secrets.token_bytes(length // 8))).decode()


def encrypt(data: str, key: str) -> str:
    """Encrypt data using key."""
    key_b = base64.b64decode(key)
    cipher = AES.new(key_b, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data.encode('UTF-8'))
    nonce = cipher.nonce
    return (base64.b64encode(
        bytes(nonce) + b'|' + bytes(tag) + b'|' + bytes(ciphertext))).decode()


def decrypt(data: str, key: str) -> str:
    """Decrypt data using key."""
    key_b = base64.b64decode(key)
    nonce, tag, ciphertext = (base64.b64decode(data.encode())).split(b'|',
                                                                     maxsplit=2)
    cipher = AES.new(key_b, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext.decode('UTF-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='AES cipher utilities by Tech~.',
        prog='aesutil.py',
    )

    subparser = parser.add_subparsers(
        help='commands',
        dest='command',
    )

    # Generate a random key
    parser_genkey = subparser.add_parser('genkey',
                                         help='Generate a random AES key.')
    parser_genkey.add_argument('-l',
                               '--length',
                               type=int,
                               default=256,
                               help='Length of the key.',
                               choices=[128, 192, 256, 512])

    # Encrypt data using key
    parser_encrypt = subparser.add_parser('enc',
                                          help='Encrypt data using a key.')
    parser_encrypt.add_argument('data', type=str, help='Data to encrypt.')
    key_encr_grp = parser_encrypt.add_mutually_exclusive_group()
    key_encr_grp.add_argument('-k',
                              '--key',
                              type=str,
                              help='Key to use for encryption.')
    key_encr_grp.add_argument(
        '-ke',
        '--keyenv',
        help='Use environmental value AES_KEY to encrypt.',
        action='store_true')

    # Decrypt data using key
    parser_decrypt = subparser.add_parser(
        'dec',
        help='Decrypt data using a key.',
    )
    parser_decrypt.add_argument(
        'data',
        type=str,
        help='Data to decrypt.',
    )
    key_decr_grp = parser_decrypt.add_mutually_exclusive_group()
    key_decr_grp.add_argument(
        '-k',
        '--key',
        type=str,
        help='Key to use for decryption.',
    )
    key_decr_grp.add_argument(
        '-ke',
        '--keyenv',
        help='Use environmental value AES_KEY to decrypt.',
        action='store_true',
    )

    args = parser.parse_args()
    if args.command == 'genkey':
        pyperclip.copy(keygen(args.length))
        print(f'Key of type AES-{args.length} copied to clipboard.')
    elif args.command == 'enc':
        if args.keyenv:
            import os

            master_key = os.environ['AES_KEY']
        else:
            master_key = args.key
        pyperclip.copy(encrypt(args.data, master_key))
        print('Encrypted data copied to clipboard.')
    elif args.command == 'dec':
        if args.keyenv:
            import os

            master_key = os.environ['AES_KEY']
        else:
            master_key = args.key
        pyperclip.copy(decrypt(args.data, master_key))
        print('Decrypted data copied to clipboard.')
    else:
        raise ValueError('Invalid command.')
