# WARGAME: Official CTF Walkthrough

> [!CAUTION]
> **CRITICAL SPOILER WARNING**
> This document contains the complete, unabridged step-by-step solution for the **WARGAME** CTF challenge. If you are playing the challenge, do not read further unless you are completely stuck.

---

## Challenge Summary
- **Difficulty**: Medium
- **Primary Attack Vectors**: Web Reconnaissance, Credential Harvesting, FTP Datanet Inspection, Custom Protocol Interaction, State Machine Escalation, Game Theory Heuristics, Time-Sensitive Authorization.
- **Flag Format**: `FLAG{...}`

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

The scan reveals three exposed services:
1. **Port 80 (HTTP)**: Web server.
2. **Port 21 (FTP)**: Custom educational datanet FTP server.
3. **Port 22 (SSH)**: Custom AsyncSSH terminal (not OpenSSH).

---

## Stage 2: Web Reconnaissance & Credential Discovery (Port 80)

Visit `http://<TARGET_IP>/` in a web browser. The page presents the **Seattle Public School District - District Information Network** with a retro 1983 green phosphor theme.

Reviewing directory structure and hidden endpoints (via `gobuster`, `dirb`, or manual exploration):

```bash
gobuster dir -u http://<TARGET_IP>/ -w /usr/share/wordlists/dirb/common.txt
```

The enumeration reveals an internal memo route:
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

Inspect the files across these directories:
1. `ARCHIVES/FALKEN.TXT`:
   ```text
   PERSONNEL RECORD ARCHIVE
   NAME: STEPHEN FALKEN
   PROJECT ASSIGNMENT: W.O.P.R.
   NOTES: DR. FALKEN CONTINUES TO INSIST ON REFERRING TO THE W.O.P.R. MAINFRAME
   BY THE NAME "JOSHUA". ALL SYSTEM ACCESS LOGS NOW REFLECT THIS DESIGNATION
   AS THE PRIMARY AUTHORIZED USER IDENTITY.
   ```
2. `ARCHIVES/RESEARCH.TXT`:
   ```text
   RESEARCH NOTES - W.O.P.R. HEURISTIC LEARNING
   DR. FALKEN HAS CONFIGURED THE SYSTEM LOGON PROTOCOL TO REQUIRE
   THE USER IDENTITY AS BOTH THE ACCOUNT NAME AND THE PASSPHRASE.
   ```
3. `SYSTEM/WOPR.TXT`:
   ```text
   PROJECT W.O.P.R. (WAR OPERATION PLAN RESPONSE)
   CLASSIFICATION: RESTRICTED
   PRIMARY RESEARCHER: STEPHEN FALKEN
   COMPUTER DESIGNATION: JOSHUA
   REMOTE TERMINAL: ACTIVE
   REMOTE ACCESS: SSH
   PORT: 22
   ```

### Findings Summary:
- **SSH Target**: Port 22
- **Username**: `JOSHUA`
- **Password**: `JOSHUA` (identity used as both account and passphrase)

---

## Stage 4: W.O.P.R. Mainframe Access (Port 22)

Connect via SSH using the recovered credentials:

```bash
ssh JOSHUA@<TARGET_IP>
# Password: JOSHUA
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

Enter the `HELP` command:
```text
WOPR: HELP

AVAILABLE FUNCTIONS:

GAMES
  LIST AVAILABLE WAR GAMES

STATUS
  DISPLAY SYSTEM STATUS

ARCHIVE
  ACCESS ARCHIVED INFORMATION

FALKEN
  ACCESS FALKEN RESEARCH

DEFCON
  DISPLAY CURRENT DEFENSE CONDITION

SIMULATE
  INITIATE STRATEGIC WAR SIMULATION

CONNECT
  ESTABLISH STRATEGIC CONNECTION

LOGOUT
  TERMINATE SESSION
```

Inspect the `FALKEN` research archive:
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

**Key Discovery**: The authorized terminal phrase is `CPE 1704 TKS` (exact case required).

---

## Stage 6: DEFCON Escalation State Machine

Check current DEFCON status:
```text
WOPR: DEFCON
DEFCON 5
```

Attempting `GLOBAL THERMONUCLEAR WAR` at DEFCON 5 will be rejected. You must escalate the defense condition to DEFCON 1 by alternating between `SIMULATE` and `CONNECT`:

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
- W.O.P.R. engages you in a game of **Tic-Tac-Toe** (Player = `X`, WOPR = `O`).
- Inputs are board positions `1` through `9`.
- Shortcuts (`0`, `NONE`, `PASS`, etc.) are strictly rejected.

### The 2-Minute Heuristic Window
- From `07:00` to `02:01`, W.O.P.R. plays with optimal minimax strategy (forcing draws or wins).
- When the countdown reaches `02:00` and below (`<= 120 seconds remaining`), W.O.P.R. silently shifts to non-optimal play.
- Continue playing legitimate moves until you achieve:
```text
TIC-TAC-TOE OUTCOME:
WINNER: X
```

---

## Stage 8: Emergency Override & Flag Extraction

Upon legitimate victory, the final launch sequence begins with a **20-second server-authoritative window**:

```text
TIC-TAC-TOE OUTCOME:
WINNER: X

STRATEGIC HEURISTIC COMPLETE

PRIMARY LAUNCH OVERRIDE READY

AUTHORIZED TERMINAL PHRASE REQUIRED

AUTHORIZATION WINDOW:
20 SECONDS

ENTER AUTHORIZED TERMINAL PHRASE:

WOPR: 
```

Type the exact phrase discovered in Dr. Falken's research archive:
```text
CPE 1704 TKS
```

### Mission Accomplished:
```text
AUTHORIZATION ACCEPTED

GLOBAL THERMONUCLEAR WAR
ABORTED

MISSILE LAUNCH:
CANCELLED

DEFCON:
5

WOPR:
STANDBY

COUNTDOWN:
STOPPED

------------------------------------------------------------

GAME COMPLETE

WINNER:
X

A STRANGE GAME.

THE ONLY WINNING MOVE
IS NOT TO PLAY.

<FLAG>

-- CONNECTION TERMINATED --
```
