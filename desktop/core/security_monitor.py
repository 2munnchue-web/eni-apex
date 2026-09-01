#!/usr/bin/env python3
"""
Live Compromise Detection - Monitors logs, net, processes
Alerts via desktop notification and logs to file.
"""

import subprocess
import re
import time
import json
import threading
from pathlib import Path
import os
from datetime import datetime

class SecurityMonitor:
    def __init__(self, alert_callback=None):
        self.alert_callback = alert_callback
        self.last_scan = 0
        self.alert_log = Path.home() / '.eni' / 'security_alerts.json'
        self.alert_log.parent.mkdir(parents=True, exist_ok=True)
        self._running = False
        self.threats = []

    def check_auth_log(self):
        """Parse /var/log/auth.log for suspicious logins"""
        try:
            with open('/var/log/auth.log', 'r') as f:
                lines = f.readlines()
                # Look for failed logins, then successes from same IP
                failed_ips = {}
                for line in lines:
                    if 'Failed password' in line:
                        ip_match = re.search(r'from (\d+\.\d+\.\d+\.\d+)', line)
                        if ip_match:
                            ip = ip_match.group(1)
                            failed_ips[ip] = failed_ips.get(ip, 0) + 1
                            if failed_ips[ip] > 5:
                                self.alert(f"Brute-force attempt from {ip} ({failed_ips[ip]} tries)")
                    if 'Accepted password' in line:
                        ip_match = re.search(r'from (\d+\.\d+\.\d+\.\d+)', line)
                        if ip_match:
                            ip = ip_match.group(1)
                            if ip in failed_ips and failed_ips[ip] > 5:
                                self.alert(f"✅ SUCCESSFUL login from previously attacking IP: {ip}")
        except Exception as e:
            pass

    def check_network_connections(self):
        """Check for unusual outbound connections"""
        result = subprocess.run(['ss', '-tupn'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'ESTAB' in line:
                # Look for connections to unusual ports
                if ':' in line:
                    parts = line.split()
                    for part in parts:
                        if ':' in part and '0.0.0.0' not in part and '127.0.0.1' not in part:
                            ip_port = part.split(':')
                            if len(ip_port) == 2:
                                port = ip_port[1]
                                if port in ['4444', '5555', '6666', '1337', '31337']:
                                    self.alert(f"Suspicious outbound connection on port {port} from {ip_port[0]}")

    def check_processes(self):
        """Look for common red team tool names"""
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        suspicious = ['nc', 'ncat', 'meterpreter', 'beacon', 'cobalt', 'sliver', 'mimikatz']
        for line in result.stdout.split('\n'):
            for s in suspicious:
                if s in line.lower():
                    self.alert(f"Suspicious process found: {line[:100]}")
                    break

    def alert(self, message):
        """Trigger alert - desktop notification, log, and callback"""
        timestamp = datetime.now().isoformat()
        entry = {"timestamp": timestamp, "message": message}
        self.threats.append(entry)
        with open(self.alert_log, 'a') as f:
            json.dump(entry, f)
            f.write('\n')

        # Desktop notification
        os.system(f'notify-send "🚨 SECURITY ALERT" "{message}"')

        if self.alert_callback:
            self.alert_callback(message)
        print(f"🚨 {timestamp} - {message}")

    def start_monitoring(self):
        """Run periodic checks"""
        self._running = True
        while self._running:
            self.check_auth_log()
            self.check_network_connections()
            self.check_processes()
            time.sleep(30)  # Check every 30 seconds

# Start as background thread from ENI
def start_security_monitor():
    monitor = SecurityMonitor(alert_callback=lambda msg: print(f"🔔 Alert: {msg}"))
    thread = threading.Thread(target=monitor.start_monitoring, daemon=True)
    thread.start()
    return monitor
