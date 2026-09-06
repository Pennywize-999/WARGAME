# WARGAME Deployment Guide

This guide details how to build, configure, and deploy the **WARGAME** CTF appliance.

---

## 1. Local VirtualBox Deployment

### System Requirements
- 1 vCPU (x86_64)
- 1024 MB RAM
- 4 GB Storage (Dynamic VDI)
- Network: Host-Only Adapter or NAT Network

### Running the Pre-built Appliance
1. Open VirtualBox -> File -> Import Appliance.
2. Select `WARGAME-1.0.2.ova`.
3. Configure the network adapter to connect to your preferred test network (e.g., `vboxnet0` with DHCP enabled).
4. Start the virtual machine.
5. Watch the VM display: `tty1` will automatically present the retro boot screen and show the dynamically assigned IP address.
6. Connect to Port 22 with `ssh JOSHUA@<IP>` using the discovered player passphrase to access the game simulation.

The OVA is a deployment artifact and is intentionally excluded from this source repository.

---

## 2. TryHackMe Maintenance Architecture & Credentials

TryHackMe requires standard privileged SSH access for platform maintenance, connectivity verification, and VM lifecycle management:

- **Service**: OpenSSH
- **Port**: `2222`
- **Username**: `thmadmin`
- **Privileges**: Sudo administrative access (`/etc/sudoers.d/thmadmin`)

### Maintenance Credential Management
To maintain security and prevent CTF solution leakage:
- **Never commit maintenance credentials**: Real maintenance passwords are never committed to version control, public documentation, or repository files.
- **Offline Provisioning**: The `thmadmin` account password is set during appliance generation via secure offline provisioning.
- **Retrieval**: When building or staging the VM, the provisioning workflow outputs the generated credentials into a local, uncommitted file (`build/maintenance_credentials.txt`) for the VM deployer to enter into the TryHackMe room upload form.

---

## 3. Configuring the Production FLAG

The production flag is stored strictly outside the source code, SQLite database, and web directory:

- **Location**: `/etc/wargame/wargame.env`
- **Permissions**: `chmod 600 /etc/wargame/wargame.env`
- **Owner**: `chown root:root /etc/wargame/wargame.env`

### Example Configuration
```ini
FLAG=THM{REPLACE_WITH_DEPLOYMENT_SECRET}
WOPR_PASSWORD=REPLACE_WITH_WOPR_PASSWORD
DB_PATH=/opt/wargame/state/wargame.db
SSH_HOST_KEY=/etc/wargame/ssh_host_key
WOPR_TYPE_DELAY=0
PYTHONPATH=/opt/wargame
```

The repository source may contain `@@WOPR_PASSWORD@@` as a placeholder in the FTP research clue. Production provisioning must replace that placeholder with the same deployment `WOPR_PASSWORD` used by the WOPR SSH service. Never commit the real password or flag.

---

## 4. Database Initialization

To generate a pristine factory database:
```bash
python3 /opt/wargame/init_state.py /opt/wargame/state/wargame.db
chown -R wargame:wargame /opt/wargame/state
chmod 750 /opt/wargame/state
chmod 640 /opt/wargame/state/wargame.db
```

This initializes:
- `run_id = 1`
- `defcon_level = 5`
- `simulation_active = 0`
- `auth_deadline = 0`
- Empty `runs_history`
