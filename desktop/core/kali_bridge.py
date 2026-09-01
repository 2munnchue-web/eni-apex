#!/usr/bin/env python3
"""
Kali Bridge - Persistent SSH proxy with auto-reconnect and command streaming
"""

import asyncio
import asyncssh
import logging
import json
from pathlib import Path
from typing import Optional, Dict, Callable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KaliBridge")

class KaliBridge:
    def __init__(self, host: str, user: str, key_path: Path, port: int = 22):
        self.host = host
        self.user = user
        self.key_path = key_path
        self.port = port
        self.connection: Optional[asyncssh.SSHClientConnection] = None
        self.session: Optional[asyncssh.SSHClientSession] = None
        self._running = False
        self._callbacks: Dict[str, Callable] = {}
        self._reconnect_interval = 5  # seconds

    async def connect(self):
        """Establish SSH connection with key auth"""
        try:
            self.connection = await asyncssh.connect(
                self.host,
                username=self.user,
                client_keys=[str(self.key_path)],
                known_hosts=None,  # for lab use; in prod use known_hosts
                port=self.port
            )
            logger.info(f"✅ Connected to Kali at {self.host}")
            return True
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return False

    async def exec_command(self, command: str, timeout: int = 60) -> Dict:
        """Execute a command on Kali and return stdout/stderr"""
        if not self.connection:
            if not await self.connect():
                return {"error": "No connection", "stdout": "", "stderr": ""}

        try:
            result = await self.connection.run(command, timeout=timeout)
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.exit_status
            }
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return {"error": str(e), "stdout": "", "stderr": ""}

    async def create_shell_session(self, command: str):
        """Create an interactive shell session for long-running tools"""
        if not self.connection:
            await self.connect()
        self.session = await self.connection.create_session(command)
        return self.session

    def start_keepalive(self):
        """Background thread to maintain connection"""
        async def keepalive():
            while self._running:
                if not self.connection or self.connection.is_closed():
                    logger.warning("Connection lost, reconnecting...")
                    await self.connect()
                await asyncio.sleep(self._reconnect_interval)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(keepalive())

# Singleton for ENI to use
_kali_bridge = None

def get_kali_bridge():
    global _kali_bridge
    if _kali_bridge is None:
        config_path = Path.home() / '.eni' / 'kali_config.json'
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
            _kali_bridge = KaliBridge(
                host=config['host'],
                user=config['user'],
                key_path=Path(config['key_path']),
                port=config.get('port', 22)
            )
        else:
            # Fallback to local VM defaults
            _kali_bridge = KaliBridge(
                host='192.168.56.101',
                user='kali',
                key_path=Path.home() / '.ssh/id_rsa',
                port=22
            )
    return _kali_bridge
