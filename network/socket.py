def recv_all_data(sock, encoding = 'utf-8'):
    dat = b""
    while True:
        buf = sock.recv(256)
        if not buf or buf == b'':
            break
        dat += buf
        if b'\0' in dat:
            line, _, rest = dat.partition(b'\0')
            return line.decode(encoding)
    return dat.decode(encoding)

def recv_all_data_udp(sock, encoding = 'utf-8'):
    buf, addr = sock.recvfrom(4096)
    if not buf or buf == b'':
        return None, None
    if b'\0' in buf:
        line, _, rest = buf.partition(b'\0')
        return line.decode(encoding), addr
    return buf.decode(encoding), addr

def is_valid_socket(sock):
    try:
        if sock.fileno() == -1 or sock is None:
            return False
        
        sock.getpeername()
        return True
    except Exception:
        return False