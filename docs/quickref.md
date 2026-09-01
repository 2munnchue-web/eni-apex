# 🚨 ENI Quick-Response Manual – Red & Blue

## 🔴 If YOU are the attacker (Red Team)

### Immediate tasks
1. **Check connectivity**: `ping -c 4 <target>`
2. **Enumerate**: `nmap -sV -p- <target>`
3. **Gain foothold**: Use `msfconsole` or Sliver.
4. **Pivot**: `ssh -D 1080 user@target` (SOCKS proxy)
5. **Cover tracks**: `history -c; rm ~/.bash_history`

### If detected (burned)
- **Kill all C2 beacons**: `pkill -f beacon`
- **Wipe logs**: `sudo shred -fuz /var/log/*`
- **Disconnect**: `ip link set eth0 down`
- **Destroy infrastructure**: `terraform destroy -auto-approve`

### Tools
- Recon: `nmap`, `masscan`, `amass`
- Creds: `mimikatz`, `Rubeus`, `laZagne`
- Lateral: `impacket`, `crackmapexec`
- C2: `sliver`, `mythic`

---

## 🔵 If you're DEFENDING (Blue Team)

### Immediate tasks
1. Isolate: `sudo ufw deny out` or disconnect.
2. Collect evidence: `/var/log/auth.log`, `/var/log/syslog`
3. Reset credentials.
4. Block IOCs: `sudo ufw deny from <attacker_ip>`
5. Start investigation.

### Hunting
- Active connections: `ss -tupn | grep ESTAB`
- Auth logs: `grep "Failed password" /var/log/auth.log`
- Scheduled tasks: `crontab -l` + `systemctl list-timers`
- Listening ports: `sudo netstat -tulpn`
- Recent files: `sudo find / -mtime -1 -type f`

---

## 🧪 In a Pinch

| Scenario            | Action                                      |
|---------------------|---------------------------------------------|
| Suspicious login    | `last` + force password reset               |
| Unknown process     | `ps aux | grep -v "\["` ; kill if bad       |
| DNS beaconing       | Check `/etc/hosts` ; `dig`                  |
| Ransomware          | Shut down, isolate, restore from backup     |
| Lost SSH key        | Revoke key, generate new one immediately    |
