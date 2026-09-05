# Security Policy

## Overview
WARGAME is an educational Capture The Flag (CTF) challenge. It is intentionally configured with realistic retro-computing puzzle mechanics in its application layer. However, the host operating system, underlying services, and sandbox isolation are hardened to prevent breakout into administrative accounts or host-level code execution.

## Scope
- **In-Scope for CTF Gameplay**:
  - Application-level challenge discovery (HTTP `/secret`, FTP clues, custom WOPR terminal commands, Tic-Tac-Toe state machine).
- **Out-of-Scope (Vulnerabilities in Infrastructure)**:
  - Linux kernel exploits, container/VM escapes, denial-of-service against the host, or vulnerabilities in third-party dependencies outside challenge design.

## Intended Challenge Isolation
- The WOPR terminal (Port 22) uses custom AsyncSSH process isolation. It provides **no interactive Linux shell**, execution channel, or system access.
- The FTP server (Port 21) runs as an unprivileged service user jailed strictly to `datanet_fs` with read-only permissions (`perm='elr'`).
- The production FLAG is stored exclusively in `/etc/wargame/wargame.env` with `0600 root:root` permissions and is revealed only via legitimate terminal authorization.

## Reporting a Vulnerability
If you discover an unintentional security vulnerability in the underlying VM architecture or packaging that allows full root compromise outside the CTF progression, please open a private GitHub advisory or contact the maintainers.
