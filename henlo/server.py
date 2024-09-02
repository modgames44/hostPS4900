#!/usr/bin/env python3

import socket
import http.server
import socketserver
import asyncio





async def run_server():
    ip = socket.gethostbyname(socket.gethostname())
    print(ip)
    PORT = 8080
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("gmail.com", 80))
    localIP = s.getsockname()[0]
    s.close()
    print('''
    _   _   _____   _   _   _                       _       
    | | | | | ____| | \ | | | |   ___             __| |  ____
    | |_| | |  _|   |  \| | | |  / _ \           / _` | |_  /
    |  _  | | |___  | |\  | | | | (_) |         | (_| |  / / 
    |_| |_| |_____| |_| \_| |_|  \___/   _____   \__,_| /___|
                                        |_____|              
    ''')
    print("Servidor Iniciado en " + localIP + ":" + str(PORT))
    print('''\n
    Para más información entre a https://github.com/j3andz/henlo_dz

    Recuerde esté fue un simple Mod que hice a partir de https://github.com/SKGleba/henlo_jb
    ''')
    Handler = http.server.SimpleHTTPRequestHandler
    server = socketserver.TCPServer(('0.0.0.0', PORT), Handler)
    server.serve_forever()

if __name__ == '__main__':
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop_policy().get_event_loop()
    loop.create_task(run_server())
    print('*Server Iniciado')
    loop.run_forever()
