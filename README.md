# WARGAME: 1983 Strategic Simulation CTF

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform: Debian 12](https://img.shields.io/badge/Platform-Debian%2012-red.svg)](docs/ARCHITECTURE.md)
[![Category: CTF Challenge](https://img.shields.io/badge/Category-Retro%20Computing%20/%20CTF-blue.svg)](docs/TRYHACKME.md)

A retro-computing Capture The Flag (CTF) appliance inspired by the classic 1983 film *WarGames*.

Players navigate a multi-stage reconnaissance and state-machine challenge: investigating a public school district web portal, exploring an educational Datanet FTP archive, discovering the secret W.O.P.R. military simulation mainframe, manipulating DEFCON conditions, surviving an intense 7-minute countdown, outplaying the artificial intelligence in Tic-Tac-Toe, and executing a final 20-second launch override to save the world.

---

## Challenge Overview

- **Format**: Standalone CTF Challenge Appliance
- **Difficulty**: Easy
- **Target Audience**: Security enthusiasts, CTF players, retro-computing fans, students
- **Primary Skills**: Reconnaissance, Service Enumeration, Web Content Discovery, FTP Interaction, Custom Terminal Interaction, State Machine Analysis, Time-Sensitive Execution

### Network Topology & Exposed Ports

Production firewall (nftables) strictly exposes only the intended services:

- **Port 80/tcp (HTTP)**: Seattle Public School District Portal
- **Port 21/tcp (FTP)**: District Datanet File System (Passive Ports: 30000-30009)
- **Port 22/tcp (SSH)**: Custom W.O.P.R. / Joshua Terminal (AsyncSSH - No Linux Shell, Player Account: JOSHUA)
- **Port 2222/tcp (SSH)**: Dedicated OpenSSH Maintenance Access (Reserved strictly for TryHackMe platform administration; not part of gameplay)

---

## Quickstart

### Prerequisites

- VirtualBox 7.0+ or VMware Workstation/Fusion
- Kali Linux or another penetration-testing distribution

### Deployment

1. Obtain the official release appliance: `WARGAME-1.0.2.ova`.
2. Import `WARGAME-1.0.2.ova` into VirtualBox or VMware.
3. Configure the network adapter according to your isolated lab or CTF environment.
4. Start the VM. The local console displays the 1983-inspired green-phosphor banner and assigned IP address.
5. Begin reconnaissance from your attacker machine. Player access to the WOPR simulation terminal on Port 22 uses the JOSHUA account (passphrase discovered through in-game Datanet investigation).

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment and configuration information.

> **Note:** The OVA appliance is distributed separately from this source repository. The repository intentionally does not contain VM disk images or release appliances.

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
