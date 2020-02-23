'''
@Author: Firefly
@Date: 2020-02-02 12:47:49
@Descripttion: 
@LastEditTime: 2020-02-23 20:01:26
'''

import sys
import socket


# 先从文件中读取
# 调用函数的时候可以 读取到吗？
host = ""
port = 8888

def init_rec():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while 1:
        try:
            sock.bind((host, port))
            print("Socket bind complete")
            break
        except socket.error:
            print("Failed to bind")
            time.sleep(0.5)
            continue
    sock.listen(3)
    count = 0
    print('waiting..........')
    conn, addr = sock.accept()
    return (sock, conn)

def get_img(sock, conn):
    image = bytes()
    try:
        conn.send(b'a')
        k = 0
        while 1:
            buf = conn.recv(1)
            if k == 0:
                if buf == b'f':
                    k = 1
            elif k == 1:
                if buf == b'i':
                    k = 2
                elif buf == b'f':
                    k = 1
                else:
                    k = 0
            elif k == 2:
                if buf == b'r':
                    k = 3
                elif buf == b'f':
                    k = 1
                else:
                    k = 0
            elif k == 3:
                if buf == b'e':
                    k = 4
                elif buf == b'f':
                    k = 1
                else:
                    k = 0
            elif k == 4:
                if buf == b'f':
                    k = 5
                elif buf == b'f':
                    k = 1
                else:
                    k = 0
            elif k == 5:
                if buf == b'l':
                    k = 6
                elif buf == b'f':
                    k = 1
                else:
                    k = 0
            else:
                if buf == b'y':
                    break
                elif buf == b'f':
                    k = 1
                else:
                    k = 0   
        print("\nstart receiving data")
        bytesize = conn.recv(4)
        filesize = int.from_bytes(bytesize, byteorder='little', signed=False)
        print("image\'s size is {0}".format(filesize))
        recsize = 0
        while recsize < filesize:
            if filesize - recsize >= 1024:
                data = conn.recv(1024)
                image += data
                recsize += len(data)
            else:
                data = conn.recv(1024)
                image += data
                recsize = filesize
        print("receive image completed\n")
    except (ConnectionError, Exception):
        print("\nClient disconnected! waiting......")
        conn, addr = sock.accept()
        time.sleep(0.5)
    return  image



def main():
    get_img()

if __name__ == "__main__":
    main()
