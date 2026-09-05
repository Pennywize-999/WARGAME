# WARGAME Architecture & System Design

## System Overview
WARGAME is packaged as a hardened, single-purpose virtual appliance running Debian 12 (Bookworm). The appliance simulates a 1983 computing environment while maintaining modern security boundaries on the host system.

```
+-------------------------------------------------------------------+
|                     WARGAME Production Appliance                  |
|                                                                   |
|   +-------------------+  +-------------------+  +---------------+ |
|   |  Port 80 (HTTP)   |  |   Port 21 (FTP)   |  | Port 22 (SSH) | |
|   |   FastAPI/Uvicorn |  |     pyftpdlib     |  |   AsyncSSH    | |
|   |  School Web Portal|  | Datanet FileSystem|  | WOPR Terminal | |
|   +---------+---------+  +---------+---------+  +-------+-------+ |
|             |                      |                    |         |
|             v                      v                    v         |
|      Static HTML/CSS         datanet_fs/          SQLite DB       |
|                                                (Atomic State)     |
|                                                         |         |
|                                                         v         |
|                                               /etc/wargame/       |
|                                               wargame.env (0600)  |
+-------------------------------------------------------------------+
```

---

## Service Architecture

All user-facing services run as the dedicated, unprivileged system user `wargame` (UID: 999, GID: 994) with shell `/usr/sbin/nologin`.

| Service | Daemon / Package | Port | Purpose |
| :--- | :--- | :--- | :--- |
| `wargame-http.service` | FastAPI + Uvicorn | `80/tcp` | Serves public school district portal and `/secret` |
| `wargame-ftp.service` | pyftpdlib 2.2.0 | `21/tcp`, `30000-30009/tcp` | Chrooted read-only Datanet archive |
| `wargame-ssh.service` | AsyncSSH 2.24.0 | `22/tcp` | Custom WOPR retro terminal simulation |
| `wargame-console.service` | Custom Bash Banner | `/dev/tty1` | Retro green phosphor local VM boot banner |

---

## Network & Firewall Configuration
The production appliance utilizes **nftables** (`/etc/nftables.conf`) configured at system initialization:
- **Default Input Policy**: `drop`
- **Default Forward Policy**: `drop`
- **Default Output Policy**: `accept`
- **Open Inbound Ports**:
  - `80/tcp`
  - `21/tcp`
  - `22/tcp`
  - `30000-30009/tcp` (FTP Passive Data Range)

All other listening ports, ICMP router discovery, and management protocols are blocked. OpenSSH is completely disabled and masked (`ssh.service`, `sshd.service`, `ssh.socket` symlinked to `/dev/null`).

---

## State Machine & Persistence Model
The game state is managed via SQLite (`/opt/wargame/state/wargame.db`) with WAL mode enabled:
1. **Single Authoritative Timer**: `game_state.countdown_deadline` stores `int(time.time()) + 420`. Remaining time is computed on-the-fly as `deadline - int(time.time())`.
2. **Hidden Heuristic Switch**: At `remaining <= 120`, WOPR switches move generation from optimal minimax (`_get_wopr_hard_move`) to passive non-optimal moves (`_get_wopr_easy_move`).
3. **Authorization Window**: Solved board triggers `auth_deadline = int(time.time()) + 20`.
4. **Zero-Persistence Timeout**: Expiration of either the 7-minute game timer or the 20-second authorization timer triggers `trigger_timeout()`, resetting DEFCON to 5 and generating a fresh run ID.
