"""Local Freebox Revolution remote exposed over MCP stdio."""
import os
import ipaddress
import socket
import re
import time
from pathlib import Path
import httpx
from dotenv import dotenv_values
from fastmcp import FastMCP

ROOT = Path(__file__).resolve().parent
mcp = FastMCP('Freebox Revolution')
KEYS = set('power home back up down left right ok vol_inc vol_dec mute prgm_inc prgm_dec red green yellow blue play pause stop rec fwd bwd next prev info epg tv'.split()) | set('0123456789')

def config():
    values = dotenv_values(ROOT / '.env')
    host = os.environ.get('FREEBOX_PLAYER_HOST', values.get('FREEBOX_PLAYER_HOST') or 'hd1.freebox.fr')
    if not re.fullmatch(r'[A-Za-z0-9.-]+', host):
        raise ValueError('Invalid player hostname')
    code = os.environ.get('FREEBOX_REMOTE_CODE', values.get('FREEBOX_REMOTE_CODE') or '')
    return host, code

def request(params):
    host, _ = config()
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(host, 80, type=socket.SOCK_STREAM)}
        if not addresses or any(not ipaddress.ip_address(address).is_private for address in addresses):
            raise RuntimeError('Player hostname must resolve to a private local-network address.')
    except socket.gaierror:
        raise RuntimeError('Cannot resolve the local Player hostname.') from None
    try:
        with httpx.Client(trust_env=False, timeout=5, follow_redirects=False) as client:
            response = client.get(f'http://{host}/pub/remote_control', params=params)
        return response.status_code
    except httpx.RequestError:
        raise RuntimeError('Cannot reach Freebox Player. Check the local network and hostname.') from None

def send(key, long_press=False):
    if key not in KEYS:
        raise ValueError('Unsupported remote key')
    _, code = config()
    if not code or not code.isdigit():
        raise ValueError('Set FREEBOX_REMOTE_CODE in the local .env file first.')
    params = {'code': code, 'key': key}
    if long_press:
        params['long'] = 'true'
    status = request(params)
    if status != 200:
        raise RuntimeError(f'Player rejected command (HTTP {status}). Check the remote code.')
    return {'accepted': True, 'key': key, 'note': 'HTTP acceptance does not confirm the visible TV state.'}

@mcp.tool()
def connection_status() -> dict:
    """Probe network access without pressing a key. Does not validate the remote code."""
    host, code = config()
    status = request({})
    return {'host': host, 'http_status': status, 'service_responded': True, 'remote_code_configured': bool(code), 'remote_code_verified': False}

@mcp.tool()
def press_key(key: str, long_press: bool = False) -> dict:
    """Press a remote key. power and mute toggle state; never retry them automatically. No TV state feedback is available."""
    return send(key, long_press)

@mcp.tool()
def change_channel(channel: int) -> dict:
    """Send a channel number (1–9999). Player must already be in live TV. No channel-state feedback."""
    if type(channel) is not int or not 1 <= channel <= 9999:
        raise ValueError('Channel must be from 1 to 9999')
    digits = str(channel)
    for i, digit in enumerate(digits):
        send(digit, long_press=i < len(digits)-1)
        if i < len(digits)-1:
            time.sleep(0.15)
    return {'accepted': True, 'channel_requested': channel}

@mcp.tool()
def adjust_volume(direction: str, steps: int = 1) -> dict:
    """Raise/lower volume by 1–10 remote presses. Absolute percentage is unavailable."""
    if direction not in ('up', 'down') or type(steps) is not int or not 1 <= steps <= 10:
        raise ValueError('Use up/down and 1–10 steps')
    for i in range(steps):
        send('vol_inc' if direction == 'up' else 'vol_dec')
        if i < steps-1:
            time.sleep(0.1)
    return {'accepted': True, 'direction': direction, 'steps': steps}

if __name__ == '__main__':
    mcp.run(transport='stdio')
