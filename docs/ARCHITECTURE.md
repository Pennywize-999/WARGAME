# WARGAME Architecture & System Design

## System Overview
WARGAME is packaged as a hardened, single-purpose virtual appliance running Debian 12 (Bookworm). The appliance simulates a 1983 computing environment while maintaining modern security boundaries on the host system.

```
+-----------------------------------------------------------------------------------+
|                            WARGAME Production Appliance                           |
|                                                                                   |
|   +-------------------+  +-------------------+  +---------------+  +------------+ |
|   |  Port 80 (HTTP)   |  |   Port 21 (FTP)   |  | Port 22 (SSH) |  |  Port 2222 | |
|   |   FastAPI/Uvicorn |  |     pyftpdlib     |  |   AsyncSSH    |  |  (OpenSSH) | |
|   |  School Web Portal|  | Datanet FileSystem|  | WOPR Terminal |  | Maintenance| |
|   +---------+---------+  +---------+---------+  +-------+-------+  +-----+------+ |
|             |                      |                    |                |        |
|             v                      v                    v                v        |
|      Static HTML/CSS         datanet_fs/          SQLite DB          Linux Shell  |
|                                                (Atomic State)       (thmadmin Only|
|                                                         |            Sudo Access) |
|                                                         v                         |
|                                               /etc/wargame/                       |
|                                               wargame.env (0600)                  |
+-----------------------------------------------------------------------------------+
```

---

## Service Architecture & Port Separation

A fundamental design requirement of the appliance is the strict separation between the player-facing retro terminal and administrative platform maintenance:

| Service | Daemon / Package | Port | Authentication | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `wargame-http.service` | FastAPI + Uvicorn | `80/tcp` | None (Public) | Serves public school district portal and `/secret` |
| `wargame-ftp.service` | pyftpdlib 2.2.0 | `21/tcp`, `30000-30009/tcp` | `PRINCIPAL:PENCIL` | Chrooted read-only Datanet archive |
| `wargame-ssh.service` | AsyncSSH 2.24.0 | `22/tcp` | `JOSHUA` (wargame.env) | Player WOPR retro terminal simulation (No Linux shell) |
| `ssh.service` | OpenSSH 9.2p1 | `2222/tcp` | `thmadmin` (Private) | TryHackMe platform administration only |
| `wargame-console.service` | Custom Bash Banner | `/dev/tty1` | Local Console | Retro green phosphor local VM boot banner |

### Isolation Rules
1. **WOPR AsyncSSH (`22/tcp`)**:
   - Runs as the unprivileged `wargame` system user (`UID 999, GID 994`, shell `/usr/sbin/nologin`).
   - Bound strictly to TCP port 22.
   - Handled entirely in Python by `src.ssh_server.wopr.WoprSession`.
   - No interactive shell, no PTY allocation, no SFTP/SCP, no command execution.
   - Account username is `JOSHUA`; access passphrase is dynamically provisioned in `/etc/wargame/wargame.env` and discovered in-game via Datanet.

2. **OpenSSH Maintenance Service (`2222/tcp`)**:
   - Runs as system `ssh.service` bound strictly to TCP port 2222 (`Port 2222`).
   - Systemd socket activation (`ssh.socket`) is permanently masked to `/dev/null` to guarantee OpenSSH never intercepts port 22.
   - Root login is strictly forbidden (`PermitRootLogin no`).
   - Standard password authentication is globally disabled and permitted exclusively for `thmadmin` via `Match User thmadmin`.
   - Accessible only to the dedicated `thmadmin` account (`AllowUsers thmadmin`).
   - Maintenance credentials are never shared with players and never stored in Git.

---

## Network & Firewall Configuration
The production appliance utilizes **nftables** (`/etc/nftables.conf`) configured at system initialization:
- **Default Input Policy**: `drop`
- **Default Forward Policy**: `drop`
- **Default Output Policy**: `accept`
- **Permitted Inbound Ports**:
  - `80/tcp` (HTTP Web Portal)
  - `21/tcp` (FTP Control)
  - `22/tcp` (WOPR Simulation SSH)
  - `2222/tcp` (TryHackMe OpenSSH Maintenance)
  - `30000-30009/tcp` (FTP Passive Data Range)

All other inbound traffic is silently dropped.

---

## State Machine & Persistence Model
The game state is managed via SQLite (`/opt/wargame/state/wargame.db`) with WAL mode enabled:
1. **Single Authoritative Timer**: `game_state.countdown_deadline` stores `int(time.time()) + 420`. Remaining time is computed on-the-fly as `deadline - int(time.time())`.
2. **Hidden Heuristic Switch**: At `remaining <= 120`, WOPR switches move generation from optimal minimax (`_get_wopr_hard_move`) to passive non-optimal moves (`_get_wopr_easy_move`).
3. **Authorization Window**: Solved board triggers `auth_deadline = int(time.time()) + 20`.
4. **Zero-Persistence Timeout**: Expiration of either the 7-minute game timer or the 20-second authorization timer triggers `trigger_timeout()`, resetting DEFCON to 5 and generating a fresh run ID.
