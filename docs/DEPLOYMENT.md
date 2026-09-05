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
2. Select `WARGAME-1.0.0.ova`.
3. Configure the network adapter to connect to your preferred test network (e.g., `vboxnet0` with DHCP enabled).
4. Start the virtual machine.
5. Watch the VM display: `tty1` will automatically present the retro boot screen and show the dynamically assigned IP address.

---

## 2. Configuring the Production FLAG

The production flag is stored strictly outside the source code, SQLite database, and web directory:

- **Location**: `/etc/wargame/wargame.env`
- **Permissions**: `chmod 600 /etc/wargame/wargame.env`
- **Owner**: `chown root:root /etc/wargame/wargame.env`

### Example Configuration:
```ini
FLAG=FLAG{EXAMPLE_REPLACE_WITH_YOUR_SECRET_FLAG}
DB_PATH=/opt/wargame/state/wargame.db
SSH_HOST_KEY=/etc/wargame/ssh_host_key
WOPR_TYPE_DELAY=0
PYTHONPATH=/opt/wargame
```

---

## 3. Database Initialization

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
