# WARGAME: 1983 Strategic Simulation CTF

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform: Debian 12](https://img.shields.io/badge/Platform-Debian%2012-red.svg)](docs/ARCHITECTURE.md)
[![Category: CTF Challenge](https://img.shields.io/badge/Category-Retro%20Computing%20/%20CTF-blue.svg)](docs/TRYHACKME.md)

A retro-computing Capture The Flag (CTF) appliance inspired by the classic 1983 film *WarGames*. 

Players navigate a realistic multi-stage reconnaissance and privilege escalation path: investigating a public school district web portal, exploring an educational dial-up/datanet FTP archive, discovering the secret W.O.P.R. military simulation mainframe, manipulating DEFCON conditions, surviving an intense 7-minute countdown, outplaying the artificial intelligence in Tic-Tac-Toe, and executing a final 20-second launch override to save the world.

---

## Challenge Overview

- **Format**: Boot-to-Root / Standalone Challenge Appliance
- **Difficulty**: Easy / Medium
- **Target Audience**: Security enthusiasts, CTF players, retro-computing fans, students
- **Primary Skills**: Reconnaissance, Service Enumeration, Protocol Inspection, State Machine Analysis, Retro Terminals

### Network Topology & Exposed Ports
Production firewall (`nftables`) strictly exposes only the intended challenge services:
- **Port 80/tcp (HTTP)**: Seattle Public School District Portal
- **Port 21/tcp (FTP)**: District Datanet File System (Passive Ports: `30000-30009`)
- **Port 22/tcp (SSH)**: Custom W.O.P.R. / Joshua Terminal (AsyncSSH - No Linux Shell)

---

## Quickstart (Running the Appliance)

### Prerequisites
- VirtualBox 7.0+ or VMware Workstation/Fusion
- Kali Linux or any penetration testing distribution

### Deployment
1. Import `WARGAME.ova` into VirtualBox.
2. Ensure Network Adapter is configured to **Host-Only** or **NAT Network** (DHCP enabled).
3. Start the VM. The local console (`tty1`) will display the 1983 green phosphor boot banner showing the VM's assigned IP address.
4. Begin reconnaissance from your attacker machine.

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed setup and configuration options.

---

## Documentation Index

- [Walkthrough (SPOILERS)](docs/WALKTHROUGH.md) - Official step-by-step CTF solution guide.
- [TryHackMe Room Guide](docs/TRYHACKME.md) - Room structure, task breakdown, hints, and platform considerations.
- [System Architecture](docs/ARCHITECTURE.md) - Technical architecture, systemd services, and isolation model.
- [Deployment Guide](docs/DEPLOYMENT.md) - Build, deployment, and configuration instructions.
- [Security Review](docs/SECURITY-REVIEW.md) - Static security audit and package inventory.

---

## Legal & Copyright Disclaimer

**WARGAME** is an original, fan-inspired educational cybersecurity challenge created for learning, historical appreciation, and Capture The Flag competitions. 

This project is **not** an official product and is **not affiliated with, endorsed by, or sponsored by Metro-Goldwyn-Mayer Studios Inc. (MGM), United Artists, or the creators, producers, or copyright holders of the 1983 motion picture *WarGames***. All trademarks, service marks, and trade names referenced are the property of their respective owners. No proprietary motion picture footage, audio clips, proprietary scripts, or commercial assets are included in this repository. All source code, terminal renderings, and text files are original creations.
