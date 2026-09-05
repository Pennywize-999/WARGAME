import asyncio
import asyncssh
import os
import sys

from src.ssh_server.wopr import WoprSession

_server = None
_loop = None
_active_connections = set()

class WoprSSHServer(asyncssh.SSHServer):
    def connection_made(self, conn):
        self._conn = conn
        _active_connections.add(conn)

    def connection_lost(self, exc):
        _active_connections.discard(self._conn)

    def password_auth_supported(self):
        return True

    def validate_password(self, username, password):
        if username.upper() == 'JOSHUA' and password.upper() == 'JOSHUA':
            return True
        raise asyncssh.DisconnectError(
            11, 
            "\r\n** IDENTIFICATION NOT RECOGNIZED **\r\n** ACCESS DENIED **\r\n-- CONNECTION TERMINATED --\r\n"
        )

async def handle_client(process):
    try:
        session = WoprSession(process.stdin, process.stdout, process.stderr)
        await session.run()
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        try:
            process.stdout.close()
        except Exception:
            pass
        try:
            process.close()
        except Exception:
            pass
        process.exit(0)

async def start_server():
    global _server
    # Dynamically generate key if not exists
    key_path = os.environ.get('SSH_HOST_KEY', os.path.join(os.path.dirname(__file__), 'ssh_host_key'))
    if not os.path.exists(key_path):
        key = asyncssh.generate_private_key('ssh-rsa')
        key.write_private_key(key_path)

    _server = await asyncssh.listen(
        '0.0.0.0', 22,
        server_host_keys=[key_path],
        server_factory=WoprSSHServer,
        process_factory=handle_client,
        reuse_address=True
    )
    return _server

from src.database.db import init_db

_stop_event = None

def stop_ssh_server():
    global _stop_event, _loop
    if _loop and _loop.is_running() and _stop_event:
        _loop.call_soon_threadsafe(_stop_event.set)

def run_ssh_server():
    global _loop, _server, _stop_event
    init_db()
    _loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_loop)
    
    async def _main():
        global _stop_event
        _stop_event = asyncio.Event()
        await start_server()
        await _stop_event.wait()
        for conn in list(_active_connections):
            try:
                conn.abort()
            except Exception:
                pass
        _active_connections.clear()
        if _server:
            _server.close()
            try:
                await asyncio.wait_for(_server.wait_closed(), timeout=0.5)
            except Exception:
                pass

    try:
        _loop.run_until_complete(_main())
    except (asyncio.CancelledError, Exception):
        pass
    finally:
        if _server:
            _server.close()
            _server = None
        if not _loop.is_closed():
            _loop.close()

if __name__ == '__main__':
    run_ssh_server()
