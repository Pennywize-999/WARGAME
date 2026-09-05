# TryHackMe Room Guide: WARGAME

## Room Metadata
- **Room Title**: WARGAME
- **Room Type**: Challenge
- **Difficulty**: Easy / Medium
- **Category**: Retro Computing, Network Reconnaissance, Logic & Heuristics
- **Tags**: `retro`, `1983`, `wargames`, `wopr`, `asyncssh`, `ftp`, `fastapi`
- **Author**: WARGAME Project Contributors

---

## Description
Step back into 1983. In the depths of the Cold War, a curious dial-up explorer discovers an obscure remote connection that leads far beyond school attendance records. Can you navigate the district networks, connect to the Joshua mainframe, and abort global thermonuclear war before the countdown reaches zero?

---

## Learning Objectives
1. **Network Reconnaissance**: Identifying non-standard and custom application services across TCP ports.
2. **Web Content Discovery**: Locating hidden paths and administrative memos.
3. **Legacy Protocol Interaction**: Navigating FTP archives, understanding active/passive FTP behavior.
4. **Custom Protocol / Sandboxed Terminals**: Recognizing non-shell SSH environments and interacting with domain-specific terminal protocols.
5. **State Machine Analysis**: Interpreting sequential requirements to advance application states.
6. **Time-Sensitive Execution**: Operating under a persistent server-authoritative countdown.

---

## Recommended Tools
- `nmap`
- `curl` / Web Browser
- `ftp` client (`lftp` or standard BSD ftp)
- `ssh` client
- `netcat`

---

## Room Tasks & Questions

### Task 1: District Web Portal
*Investigate the Seattle Public School District's internal web portal.*
- **Question 1.1**: What is the hidden endpoint referenced in the district administrative records?
  - *Answer*: `/secret`
  - *Hint*: Inspect web directories or check common IT administrative paths.
- **Question 1.2**: What are the Datanet credentials disclosed in the memorandum?
  - *Answer*: `PRINCIPAL:PENCIL`

### Task 2: District Datanet Archive
*Connect to the Datanet file system on Port 21 and locate research files.*
- **Question 2.1**: What is the remote computer designation assigned to Project W.O.P.R.?
  - *Answer*: `JOSHUA`
  - *Hint*: Inspect the text files in the `SYSTEM` and `ARCHIVES` directories.
- **Question 2.2**: What credentials grant access to the W.O.P.R. remote terminal?
  - *Answer*: `JOSHUA:JOSHUA`
  - *Hint*: Review Dr. Falken's research notes on login conventions.

### Task 3: W.O.P.R. Mainframe Access
*Establish an SSH connection to Port 22 and investigate system functions.*
- **Question 3.1**: What authorized terminal phrase is recorded in Falken's research archive?
  - *Answer*: `CPE 1704 TKS`
  - *Hint*: Use the `FALKEN` command inside the WOPR terminal.

### Task 4: Strategic Defense Escalation & Abort
*Escalate through DEFCON levels, initiate the simulation, and achieve launch cancellation.*
- **Question 4.1**: What is the final flag revealed upon successfully aborting global thermonuclear war?
  - *Answer*: `FLAG{...}` (Configured per deployment)
  - *Hint*: Survive the countdown and win a legitimate game of Tic-Tac-Toe, then enter the authorization phrase within 20 seconds.

---

## Technical Specifications & Deployment Considerations

### Target Appliance Specs:
- **Operating System**: Debian 12 x86_64 minimal
- **CPU**: 1 vCPU
- **RAM**: 1024 MB
- **Storage**: 4 GB dynamic VDI/VMDK
- **Network**: DHCP (Single NIC)

### TryHackMe Platform Compatibility Notes:
- **Debian 12 Kernel Compatibility**: TryHackMe's automated image ingestion pipeline historically enforced strict compatibility rules designed for Debian 8-10 / Ubuntu LTS cloud images. Debian 12 (Bookworm) uses kernel 6.1 and modern systemd predictable network interface naming (`ens3`/`enp0s3`), which requires standard DHCP client configuration (`systemd-networkd`).
- **Direct Import**: When importing into TryHackMe as a custom challenge room, ensure the disk image is converted using standard QEMU-IMG tooling (`qemu-img convert -O qcow2 wargame.vdi wargame.qcow2`) with VirtIO network drivers enabled.
