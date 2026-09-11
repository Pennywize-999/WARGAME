# Changelog

All notable changes to the WARGAME CTF release are documented in this file.

## [1.0.2] - 2026-09-11

### Fixed

- Corrected challenge documentation to describe WARGAME as a standalone CTF challenge rather than a boot-to-root or privilege-escalation challenge.
- Standardized documented difficulty to Easy to match the TryHackMe room configuration.
- Updated the walkthrough and TryHackMe guide to avoid exposing the deployment-specific flag value.
- Pinned Python dependencies to the production package versions documented by the security review.
- Enforced exact case-sensitive WOPR password validation in the player authentication flow.

### Changed

- Updated release documentation references to `WARGAME-1.0.2.ova`.
- Clarified that TCP/2222 is maintenance-only and TCP/22 is the player-facing WOPR terminal.
- Updated the public TryHackMe room guide to reflect the current Easy difficulty.
- Updated documented appliance storage from 4 GB to 8 GB.
- Updated TryHackMe room documentation to reflect the current exposed services and gameplay architecture.
- Removed obsolete VM compatibility and conversion instructions from the TryHackMe room guide.
- Updated the README to reflect the current Easy difficulty and production network configuration.
- Clarified that the Port 22 SSH service is the custom W.O.P.R. terminal and does not provide a Linux shell.
- Clarified that Port 2222 is reserved for TryHackMe platform administration and is not part of the intended gameplay attack surface.

### Removed

- Removed the public `docs/WALKTHROUGH.md` answer key to prevent the complete challenge solution from being exposed in the public repository.
- Removed the public README link to the full walkthrough.

### Security

- Confirmed that production flags, WOPR passwords, maintenance credentials, private keys, VM images, and runtime databases are excluded from the repository.
- Retained only placeholder values in `conf/wargame.env.example`.
- Retained the intentionally exposed CTF credentials and challenge clues required for gameplay.

---

## [1.0.1] - 2026-09-05

### Fixed

- Corrected the pre-built appliance filename in `docs/DEPLOYMENT.md` to `WARGAME-1.0.0.ova`.

---

## [1.0.0] - 2026-09-05

### Added

- Complete 1983 WOPR CRT terminal experience over AsyncSSH (Port 22).
- SEATTLE PUBLIC SCHOOL DISTRICT web portal (Port 80) and Datanet FTP service (Port 21).
- Server-authoritative persistent game timer (7 minutes / 420 seconds) in SQLite.
- Silent background difficulty transition to EASY mode during final 2 minutes (<= 120 seconds).
- 20-second server-authoritative authorization countdown with exact case-sensitive phrase requirement (`CPE 1704 TKS`).
- Debian 12 minimal production VM appliance with nftables firewall and native systemd process management.
- Comprehensive CTF Walkthrough, TryHackMe room deployment guide, and architecture documentation.

### Changed

- Refactored all timer calculations to derive strictly from SQLite `countdown_deadline`.
- Standardized gameplay duration from 15 minutes to 7 minutes (420s) and difficulty transition from 3 minutes to 2 minutes (120s).
- Improved SSH `HELP` output with period-accurate 60-dash bordered block and indented command descriptions.
- Enhanced `FALKEN` research archive output to deliver authentic terminal clue.

### Fixed

- Resolved AsyncSSH TCP/22 startup failure caused by variable typo in database initialization.
- Masked OpenSSH daemon units in systemd to ensure port 22 belongs exclusively to custom WOPR terminal.
- Enforced strict FTP passive port range `30000-30009` in firewall and pyftpdlib configuration.
- Eliminated redundant in-memory timer definitions across codebase.