# WARGAME: Official CTF Walkthrough

> [!CAUTION]
> **CRITICAL SPOILER WARNING**
> This document contains the complete, unabridged step-by-step solution for the **WARGAME** CTF challenge. If you are playing the challenge, do not read further unless you are completely stuck.

---

## Challenge Summary
- **Difficulty**: Easy
- **Primary Attack Vectors**: Web Reconnaissance, Credential Discovery, FTP Datanet Inspection, Custom Protocol Interaction, State Machine Analysis, Game-Theory Heuristics, Time-Sensitive Authorization.
- **Flag Format**: Deployment-specific (`THM{...}` for the TryHackMe deployment)

---

## Stage 1: Initial Reconnaissance & Port Scanning

Begin with an Nmap service and version scan against the target VM:

```bash
nmap -Pn -sS -sV -p- <TARGET_IP>
```

### Scan Results
```text
PORT     STATE SERVICE VERSION
21/tcp   open  ftp     pyftpdlib 2.2.0 (SEATTLE PUBLIC SCHOOL DISTRICT DATANET)
22/tcp   open  ssh     AsyncSSH 2.24.0 (WOPR Simulation Terminal)
80/tcp   open  http    uvicorn (Seattle Public School District Web Portal)
```

The scan reveals three gameplay services:
1. **Port 80 (HTTP)**: Web server.
2. **Port 21 (FTP)**: Custom educational datanet FTP server.
3. **Port 22 (SSH)**: Custom AsyncSSH terminal (not OpenSSH).

Port 2222 is a dedicated TryHackMe maintenance service and is not part of gameplay.

---

## Stage 2: Web Reconnaissance & Credential Discovery (Port 80)

Visit `http://<TARGET_IP>/` in a web browser. The page presents the **Seattle Public School District - District Information Network** with a retro 1983 green phosphor theme.

Reviewing directory structure and hidden endpoints (via `gobuster`, `dirb`, or manual exploration):

```bash
gobuster dir -u http://<TARGET_IP>/ -w /usr/share/wordlists/dirb/common.txt
```

The enumeration reveals the internal memo route:
```text
/secret (Status: 200)
```

Navigating to `http://<TARGET_IP>/secret` displays an internal IT notice:
```text
SEATTLE PUBLIC SCHOOL DISTRICT
COMPUTER SERVICES
------------------------------------------------------------
DISTRICT DATANET ACCESS INFORMATION

ACCOUNT NAME:
    PRINCIPAL

PASSWORD:
    PENCIL

SYSTEM:
    SEATTLE PUBLIC SCHOOL DISTRICT DATANET

ACCESS METHOD:
    REMOTE TERMINAL
------------------------------------------------------------
```

---

## Stage 3: Datanet FTP Enumeration (Port 21)

Connect to the FTP service on Port 21 using the discovered credentials:

```bash
ftp <TARGET_IP>
# Name: PRINCIPAL
# Password: PENCIL
```

The FTP server uses passive mode (`ports 30000-30009`). Listing directories:
```text
ftp> ls
drwxr-xr-x ARCHIVES
drwxr-xr-x FACULTY
drwxr-xr-x PROGRAMS
drwxr-xr-x STUDENTS
drwxr-xr-x SYSTEM
```

Inspect the relevant files:
1. `ARCHIVES/FALKEN.TXT` identifies Stephen Falken and the W.O.P.R. project.
2. `ARCHIVES/RESEARCH.TXT` contains the W.O.P.R. terminal access parameters.
3. `SYSTEM/WOPR.TXT` identifies the remote terminal as SSH on port 22.

### Findings Summary
- **SSH Target**: Port 22
- **Username**: `JOSHUA`
- **Password**: `<WOPR_PASSWORD>` (retrieved from `ARCHIVES/RESEARCH.TXT`)

---

## Stage 4: W.O.P.R. Mainframe Access (Port 22)

Connect via SSH using the recovered credentials:

```bash
ssh JOSHUA@<TARGET_IP>
# Password: <WOPR_PASSWORD>
```

You are greeted by the W.O.P.R. terminal interface:
```text
LOGON COMPLETE
W.O.P.R. ONLINE
DESIGNATION: JOSHUA

GREETINGS PROFESSOR FALKEN.

SHALL WE PLAY A GAME?

WOPR:
```

> [!NOTE]
> This SSH session is a sandboxed AsyncSSH terminal. Standard Linux shell commands (`ls`, `whoami`, `cat`) are unrecognized.

---

## Stage 5: Discovering the Emergency Authorization Clue

Enter the `HELP` command and inspect the available WOPR functions. Then use the `FALKEN` command:

```text
WOPR: FALKEN

------------------------------------------------------------

FALKEN RESEARCH ARCHIVE

RESEARCHER:
STEPHEN FALKEN

PROJECT:
W.O.P.R.

COMPUTER DESIGNATION:
JOSHUA

RESEARCH NOTE:

AUTHORIZED TERMINAL PHRASE:
CPE 1704 TKS

ARCHIVE STATUS:
RESTRICTED

------------------------------------------------------------
```

**Key Discovery:** The authorized terminal phrase is `CPE 1704 TKS` (exact case required).

---

## Stage 6: DEFCON Escalation State Machine

Check current DEFCON status:
```text
WOPR: DEFCON
DEFCON 5
```

You must escalate the defense condition to DEFCON 1 by alternating between `SIMULATE` and `CONNECT`:

1. `SIMULATE` -> DEFCON 5 to 4
2. `CONNECT`  -> DEFCON 4 to 3
3. `SIMULATE` -> DEFCON 3 to 2
4. `CONNECT`  -> DEFCON 2 to 1

At DEFCON 1, the missile systems are primed.

---

## Stage 7: Strategic Simulation & Tic-Tac-Toe Heuristic

At DEFCON 1, initiate the simulation:
```text
WOPR: GLOBAL THERMONUCLEAR WAR
```

The terminal transitions into simulation mode:
- A fixed **7-minute server-authoritative countdown** (`T-MINUS 07:00`) starts in the terminal header.
- W.O.P.R. engages you in **Tic-Tac-Toe** (Player = `X`, WOPR = `O`).
- Inputs are board positions `1` through `9`.
- Invalid shortcuts are rejected.

### The 2-Minute Heuristic Window
- From `07:00` to `02:01`, W.O.P.R. uses optimal play.
- At `02:00` and below (`<= 120 seconds remaining`), W.O.P.R. silently shifts to non-optimal play.
- Continue playing legitimate moves until you achieve:
```text
TIC-TAC-TOE OUTCOME:
WINNER: X
```

---

## Stage 8: Emergency Override & Flag Extraction

Upon legitimate victory, the final launch sequence begins with a **20-second server-authoritative window**.

Enter the exact phrase discovered in Dr. Falken's research archive:
```text
CPE 1704 TKS
```

### Mission Accomplished
The terminal displays the launch cancellation, returns DEFCON to 5, and reveals the deployment-configured flag.

The exact flag value is intentionally not documented in this source repository. For the TryHackMe deployment, the expected flag uses the `THM{...}` format.
