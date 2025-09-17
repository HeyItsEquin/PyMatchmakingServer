def recv_all_data(sock, encoding = 'utf-8'):
    dat = b""
    while True:
        buf = sock.recv(256)
        if not buf:
            break
        dat += buf
        if b'\0' in dat:
            line, _, rest = dat.partition(b'\0')
            return line.decode(encoding)
    return dat.decode(encoding)