import os
import logging
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# Disable writing verbose logs to standard output in tests unless configured
logging.basicConfig(level=logging.WARNING)

_ftp_server = None

def run_ftp_server():
    global _ftp_server
    authorizer = DummyAuthorizer()
    
    # Define the root directory of the FTP server
    ftp_root = os.path.join(os.path.dirname(__file__), 'datanet_fs')
    
    # Ensure root exists
    os.makedirs(ftp_root, exist_ok=True)
    
    # Add user with strictly read-only permissions
    # 'e' = change directory, 'l' = list files, 'r' = retrieve file
    authorizer.add_user('PRINCIPAL', 'PENCIL', ftp_root, perm='elr')
    
    handler = FTPHandler
    handler.passive_ports = range(30000, 30010)
    handler.authorizer = authorizer
    
    # Change the banner
    handler.banner = "SEATTLE PUBLIC SCHOOL DISTRICT DATANET"
    
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', 21))
    sock.listen(100)
    sock.setblocking(0)

    _ftp_server = FTPServer(sock, handler)
    try:
        _ftp_server.serve_forever(timeout=0.2, handle_exit=False)
    except Exception:
        pass

def stop_ftp_server():
    global _ftp_server
    if _ftp_server:
        try:
            _ftp_server.close_all()
        except Exception:
            pass
        _ftp_server = None

if __name__ == '__main__':
    run_ftp_server()
