#!/usr/bin/env python3

# A flawed variant of Matyas-Meyer-Oseas (MMO) hash function based on AES. 
# (c) Alwen Tiu, 2022

from Crypto.Cipher import AES
from Crypto.Util.number import *
from Crypto.Util.Padding import pad
from Crypto.Util.strxor import *
import argparse 

H0=b'0123456789abcdef'

H1 = bytearray.fromhex('e570e3e9013959374ff1e57908617f74')
H2 = bytearray.fromhex('52948bfca7b0843e38b96b86a33c8741')
H3 = bytearray.fromhex('8a652c9354bfe038b4e16f70a2a475c7')
H4 = bytearray.fromhex("d58daf194a8e552608efc598ce354bac")

def aes_encrypt(key, x, i):
    cipher=AES.new(key, AES.MODE_ECB)
    return strxor(cipher.encrypt(x), long_to_bytes(i, AES.block_size))

def get_snd_bin(data):
    x1 = b'0' * 16
    H1_new = aes_encrypt(H0, x1, 1)
    H2_crypt = strxor(H2, long_to_bytes(2, 16))

    cipher = AES.new(H1_new, AES.MODE_ECB)
    x2 = cipher.decrypt(H2_crypt)

    snd_data = x1 + x2 + data[32:]

    with open('snd.bin', 'wb') as outf:
        outf.write(snd_data)

    return snd_data

def mmoctr(data):
    data=pad(data, AES.block_size)

    k = len(data)//AES.block_size 

    Hi = H0 
    for i in range(0,k): 
        print("H%d: %s" % (i, Hi.hex()))
        x = data[i*16:(i+1)*16]
        cipher=AES.new(Hi, AES.MODE_ECB)
        # H_{i} = enc(x, H_{i-1}) XOR i  
        Hi = strxor(cipher.encrypt(x), long_to_bytes(i+1, AES.block_size))

    return Hi.hex()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str, help='file to compute the hash for')
    args = parser.parse_args()

    with open(args.file, "rb") as f:
        data=f.read()
    digest = mmoctr(data)
    print("Hash: " + digest)
    snd_data = get_snd_bin(data)
    snd_hash = mmoctr(snd_data)
    print("Snd Hash: " + snd_hash)
    print(snd_hash == H4.hex())

if __name__ == "__main__":
    main()
   