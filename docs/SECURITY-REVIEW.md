# WARGAME Production Security Review & Audit

**Date of Audit**: 2026-09-05  
**Auditor**: Automated Static Release Auditor  
**Status**: PASSED - PRODUCTION READY  

---

## 1. Production Package & Dependency Inventory

All dependencies were verified directly from the production Debian 12 VDI root:

| Component | Exact Version | Source | Network Exposed? | Security Assessment |
| :--- | :--- | :--- | :--- | :--- |
| **Debian Linux** | 12.15 (Bookworm) | Debian Base Repository | OS Level | Current Debian stable release; security updates applied. |
| **Linux Kernel** | 6.1.0-52-amd64 | Debian Package | Internal | Long Term Support (LTS) kernel branch. |
| **Python** | 3.11.2 | Debian Package | Internal | Standard Python runtime for Debian 12. |
| **AsyncSSH** | 2.24.0 | PyPI (venv) | **Port 22/tcp** | Patched against Terrapin (CVE-2023-48795) & Rogue Extension. Custom WOPR simulation. |
| **OpenSSH** | 9.2p1-2+deb12u3 | Debian Base Repository | **Port 2222/tcp** | Hardened maintenance service; password auth restricted to `thmadmin`. Root login disabled. |
| **pyftpdlib** | 2.2.0 | PyPI (venv) | **Port 21/tcp** | Hardened; chrooted read-only Datanet root (`perm='elr'`). |
| **Uvicorn** | 0.52.4 | PyPI (venv) | **Port 80/tcp** | Production ASGI server; reload/debug modes disabled. |
| **FastAPI** | 0.141.1 | PyPI (venv) | **Port 80/tcp** | Static routing; path traversal protected via Starlette. |
| **Cryptography** | 50.0.1 | PyPI (venv) | Internal (AsyncSSH) | Modern cryptography backend. |
| **OpenSSL** | 3.0.20 (7 Apr 2026) | Debian `libssl3` | Internal | Patched Debian security update. |
| **SQLite** | 3.40.1 | Debian `sqlite3` | Local File Only | No network sockets; atomic WAL transactions. |
| **nftables** | 1.0.6 | Debian `nftables` | Packet Filter | Default DROP input policy; strict port whitelist. |

---

## 2. SSH Architecture & Port Isolation

### Port 22 (AsyncSSH - WOPR Simulation)
- **Channel Isolation**: No shell execution (`/bin/sh` or `/bin/bash`), no PTY allocation, no command exec channel.
- **Subsystem Isolation**: SFTP and SCP subsystems are not registered.
- **Port Forwarding**: Agent forwarding and TCP port forwarding are disabled.
- **Process Factory**: Client sessions instantiate only `WoprSession`, binding strictly to standard stream I/O.
- **Credentials**: Username `JOSHUA` and player access passphrase validated against protected environment configuration (never hardcoded in application layer).

### Port 2222 (OpenSSH - TryHackMe Platform Maintenance)
- **Port Binding**: Explicitly bound to `Port 2222`. No binding on port 22.
- **Socket Activation**: `ssh.socket` permanently masked to `/dev/null`.
- **Root Login**: Explicitly disabled (`PermitRootLogin no`).
- **User Whitelist**: Restricted to `thmadmin` (`AllowUsers thmadmin`).
- **Authentication**: Global password authentication disabled; permitted solely for `thmadmin`.
- **Privilege Separation**: Standard OpenSSH privilege separation sandbox enabled.

---

## 3. FTP Security Review (pyftpdlib)
- **Authentication**: `PRINCIPAL:PENCIL` only. Anonymous access is rejected.
- **Chroot Jail**: Confined to `/opt/wargame/src/ftp_server/datanet_fs`.
- **Permissions**: Read-only (`elr`). No write, modify, delete, append, or directory creation allowed.
- **Passive Port Range**: Confined strictly to `30000-30009`.

---

## 4. HTTP Security Review (FastAPI / Uvicorn)
- **Debug & Reload**: Explicitly disabled (`--host 0.0.0.0 --port 80` without `--reload`).
- **Path Traversal**: Tested against `StaticFiles` root; traversal outside `/static` rejected.
- **Sensitive Files**: No `.env`, `wargame.env`, `wargame.db`, or Python sources exposed via web.
- **Intentional Route**: `/secret` remains accessible as the designed CTF discovery path.

---

## 5. Flag & Secrets Protection
- Flag stored solely in `/etc/wargame/wargame.env` (`0600 root:root`).
- Zero hardcoded fallback flags in source code, SQLite database, or web/FTP assets.
- Flag revealed exclusively upon legitimate terminal authorization (`CPE 1704 TKS`) within 20 seconds.
