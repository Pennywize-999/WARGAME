# TryHackMe Room Guide: WARGAME

## Room Metadata

- **Room Title**: WARGAME
- **Room Type**: Challenge
- **Difficulty**: Easy
- **Category**: Retro Computing, Network Reconnaissance, Logic & Heuristics
- **Tags**: `retro`, `1983`, `wargames`, `wopr`, `asyncssh`, `ftp`, `fastapi`
- **Author**: WARGAME Project Contributors

---

## Description

Step back into 1983. In the depths of the Cold War, a curious dial-up explorer discovers an obscure remote connection that leads far beyond school attendance records. Can you navigate the district networks, connect to the Joshua mainframe, and abort global thermonuclear war before the countdown reaches zero?

---

## TryHackMe VM Upload Specifications

When submitting the appliance to the TryHackMe custom VM upload form, specify:

| Field | Value | Notes |
| :--- | :--- | :--- |
| **Access Method** | `SSH` | Platform management access |
| **Port** | `2222` | Dedicated OpenSSH maintenance port |
| **Administrator Username** | `thmadmin` | Dedicated maintenance user with sudo permissions |
| **Administrator Password** | `[Provisioned Password]` | Configured during offline build; never committed to Git |

> [!NOTE]
> **TCP Port 22 is reserved for CTF Gameplay**: Players connect to Port 22 using the `JOSHUA` account and the passphrase discovered during the Datanet investigation to access the AsyncSSH WOPR simulation terminal. OpenSSH is isolated to Port 2222 and is not part of the challenge attack surface.

---

## Learning Objectives

1. **Network Reconnaissance**: Identifying non-standard and custom application services across TCP ports.
2. **Web Content Discovery**: Locating hidden paths and administrative memos.
3. **Legacy Protocol Interaction**: Navigating FTP archives and understanding passive FTP behavior.
4. **Custom Protocol / Sandboxed Terminals**: Recognizing non-shell SSH environments and interacting with domain-specific terminal protocols.
5. **State Machine Analysis**: Interpreting sequential requirements to advance application states.
6. **Time-Sensitive Execution**: Operating under a persistent server-authoritative countdown.

---

## Recommended Tools

- `nmap`
- `curl` / Web Browser
- `gobuster` or `dirb`
- `ftp` client (`lftp` or standard BSD ftp)
- `ssh` client

---

## Room Tasks & Questions

### Task 1: District Web Portal

*Investigate the Seattle Public School District's internal web portal.*

- **Question 1.1**: What is the hidden endpoint discovered during web content discovery?
  - *Answer*: `/secret`
  - *Hint*: Inspect common web directories.

- **Question 1.2**: What are the Datanet credentials disclosed in the memorandum?
  - *Answer*: `PRINCIPAL:PENCIL`

### Task 2: District Datanet Archive

*Connect to the Datanet file system on Port 21 and locate the research files.*

- **Question 2.1**: What is the remote computer designation assigned to Project W.O.P.R.?
  - *Answer*: `JOSHUA`
  - *Hint*: Inspect the files under `SYSTEM` and `ARCHIVES`.

- **Question 2.2**: What credentials grant access to the W.O.P.R. remote terminal?
  - *Answer*: `JOSHUA:<WOPR_PASSWORD>`
  - *Hint*: Review Dr. Falken's research notes on terminal access parameters in the Datanet archives.

### Task 3: W.O.P.R. Mainframe Access

*Establish an SSH connection to Port 22 and investigate system functions.*

- **Question 3.1**: What authorized terminal phrase is recorded in Falken's research archive?
  - *Answer*: `CPE 1704 TKS`
  - *Hint*: Use the `FALKEN` command inside the WOPR terminal.

### Task 4: Strategic Defense Escalation & Abort

*Escalate through DEFCON levels, initiate the simulation, and achieve launch cancellation.*

- **Question 4.1**: What is the final flag revealed upon successfully aborting global thermonuclear war?
  - *Answer*: `THM{...}` (configured in the TryHackMe deployment)
  - *Hint*: Win a legitimate game of Tic-Tac-Toe, then enter the authorization phrase within 20 seconds.

---

## Technical Specifications & Deployment Considerations

### Target Appliance Specs

- **Operating System**: Debian 12 x86_64 minimal
- **CPU**: 1 vCPU
- **RAM**: 1024 MB
- **Storage**: 8 GB dynamic VDI/VMDK
- **Network**: DHCP (Single NIC)

---

## Exposed Services

The production appliance exposes only the services required for gameplay and platform administration:

| Port | Protocol | Service | Purpose |
| :--- | :--- | :--- | :--- |
| `21` | TCP | FTP | Seattle Public School District Datanet |
| `22` | TCP | SSH | Custom W.O.P.R. / JOSHUA terminal |
| `80` | TCP | HTTP | Seattle Public School District web portal |
| `2222` | TCP | SSH | TryHackMe maintenance access |
| `30000-30009` | TCP | FTP Passive | Dynamic FTP data transfers |

Port `22` is handled by the custom AsyncSSH WOPR terminal and does not provide a normal Linux shell.

Port `2222` is reserved for TryHackMe platform administration and is not part of the intended player attack path.

---

## Gameplay Flow

The intended challenge progression is:

```text
HTTP
  |
  v
/secret
  |
  v
PRINCIPAL:PENCIL
  |
  v
FTP :21
  |
  v
ARCHIVES/RESEARCH.TXT
  |
  v
JOSHUA + WOPR passphrase
  |
  v
SSH :22
  |
  v
WOPR TERMINAL
  |
  v
FALKEN
  |
  v
CPE 1704 TKS
  |
  v
DEFCON escalation
  |
  v
GLOBAL THERMONUCLEAR WAR
  |
  v
Tic-Tac-Toe
  |
  v
WINNER: X
  |
  v
20-second authorization window
  |
  v
CPE 1704 TKS
  |
  v
FLAG