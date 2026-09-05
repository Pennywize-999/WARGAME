#!/bin/bash
# 1983 WARGAME Console Experience
# Wait for active IPv4 address
IP=""
for i in {1..30}; do
    IP=$(ip -4 addr show scope global | awk '/inet / {print $2}' | cut -d/ -f1 | head -n1)
    if [ -n "$IP" ]; then
        break
    fi
    sleep 1
done

if [ -z "$IP" ]; then
    IP="ACQUIRING..."
fi

# Clear screen
clear

# 1983 Green phosphor style
printf "\033[1;32m"
cat << 'EOF'

WARGAME
WAR OPERATION PLAN RESPONSE


SYSTEM INITIALIZATION

MEMORY TEST ............... COMPLETE
SYSTEM CHECK .............. COMPLETE
NETWORK INTERFACE .......... READY

NETWORK ADDRESS:

EOF

printf "  %s\n\n\n" "$IP"
printf "SYSTEM READY\n\n"
printf "> \033[5m_\033[0m\n"

# Prevent interactive shell breakout; keep retro prompt on screen
while true; do
    sleep 3600
done
