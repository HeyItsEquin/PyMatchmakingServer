def recv_all_data(sock, encoding = 'utf-8'):
    dat = b""
    while True:
        buf = sock.recv(1024)
        if not buf:
            break
        dat += buf
    
    return dat.decode(encoding)