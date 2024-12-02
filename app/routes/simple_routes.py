from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from app.services.network_monitor.monitor import network_monitor
import os
import urllib.parse
import requests
from datetime import datetime
import psutil
import socket
import platform
import subprocess

simple = Blueprint('simple', __name__)

@simple.route('/')
def index():
    return redirect(url_for('simple.simple_dashboard'))

@simple.route('/dashboard')
@simple.route('/simple-dashboard')
def simple_dashboard():
    return render_template('simple_dashboard.html')

@simple.route('/network')
@simple.route('/network-monitor')
def network_monitor_page():
    return render_template('network_monitor.html')

@simple.route('/api/quick-scan', methods=['POST'])
def quick_scan():
    # Simulate a quick system scan
    return jsonify({
        'status': 'success',
        'message': 'System scan completed',
        'threats_found': 0,
        'last_scan': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@simple.route('/api/check-url', methods=['POST'])
def check_url():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    # Basic URL validation
    try:
        result = urllib.parse.urlparse(url)
        if not all([result.scheme, result.netloc]):
            return jsonify({'error': 'Invalid URL format'}), 400
    except:
        return jsonify({'error': 'Invalid URL'}), 400

    # Here you would typically check against known malicious URL databases
    # For now, we'll return a simulated response
    return jsonify({
        'status': 'safe',
        'url': url,
        'check_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'safety_score': 95
    })

@simple.route('/api/scan-file', methods=['POST'])
def scan_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        # Here you would typically scan the file for threats
        # For now, we'll return a simulated response
        return jsonify({
            'status': 'safe',
            'filename': filename,
            'scan_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'safety_score': 98
        })

@simple.route('/api/security-tips', methods=['GET'])
def security_tips():
    tips = {
        'phishing': [
            'Never share sensitive information via email',
            'Check sender addresses carefully',
            'Be wary of urgent or threatening language',
            'Hover over links before clicking',
            'Look for spelling and grammar errors'
        ],
        'password': [
            'Use at least 12 characters',
            'Mix letters, numbers, and symbols',
            'Avoid personal information',
            'Use unique passwords for each account',
            'Consider using a password manager'
        ]
    }
    return jsonify(tips)

@simple.route('/api/network-stats')
def get_network_stats():
    return jsonify(network_monitor.get_network_stats())

@simple.route('/api/active-connections')
def get_active_connections():
    return jsonify(network_monitor.get_active_connections())

@simple.route('/api/network-devices')
def get_network_devices():
    try:
        # Get all network interfaces
        addrs = psutil.net_if_addrs()
        connections = psutil.net_connections()
        
        devices = []
        seen_ips = set()
        
        # Get this machine's addresses to identify local device
        local_addresses = set()
        for interface, addrs_list in addrs.items():
            for addr in addrs_list:
                if addr.family == socket.AF_INET:  # IPv4
                    local_addresses.add(addr.address)
        
        # Process active connections to find devices
        for conn in connections:
            if conn.raddr and conn.raddr.ip and conn.raddr.ip not in seen_ips:
                seen_ips.add(conn.raddr.ip)
                
                # Try to get device name through reverse DNS
                try:
                    name = socket.gethostbyaddr(conn.raddr.ip)[0]
                except (socket.herror, socket.gaierror):
                    name = None
                
                # Determine device type based on port and protocol
                device_type = determine_device_type(conn.raddr.port, conn.type)
                
                devices.append({
                    'name': name,
                    'ip': conn.raddr.ip,
                    'mac': get_mac_address(conn.raddr.ip),
                    'type': device_type,
                    'active': True,
                    'local': conn.raddr.ip in local_addresses
                })
        
        return jsonify(devices)
    except Exception as e:
        print(f"Error getting network devices: {str(e)}")
        return jsonify([])

def determine_device_type(port, protocol):
    """Determine device type based on port and protocol."""
    common_ports = {
        80: 'desktop',    # HTTP
        443: 'desktop',   # HTTPS
        22: 'desktop',    # SSH
        21: 'desktop',    # FTP
        25: 'desktop',    # SMTP
        53: 'router',     # DNS
        67: 'router',     # DHCP
        68: 'router',     # DHCP
        137: 'desktop',   # NetBIOS
        138: 'desktop',   # NetBIOS
        139: 'desktop',   # NetBIOS
        445: 'desktop',   # SMB
        548: 'desktop',   # AFP
        631: 'printer',   # IPP (Printing)
        5353: 'iot',      # mDNS
        1900: 'iot',      # SSDP (IoT Discovery)
        8080: 'desktop',  # HTTP Alternate
        3389: 'desktop',  # RDP
    }
    
    if port in common_ports:
        return common_ports[port]
    elif port >= 49152:  # Ephemeral ports often used by mobile devices
        return 'smartphone'
    else:
        return 'other'

def get_mac_address(ip):
    """Get MAC address for an IP address using ARP table."""
    try:
        if platform.system() == "Windows":
            # Run the ARP command
            output = subprocess.check_output(f"arp -a {ip}", shell=True).decode()
            # Parse the output to find the MAC address
            for line in output.split('\n'):
                if ip in line:
                    mac = line.split()[1].replace('-', ':')
                    return mac
        return "Unknown"
    except:
        return "Unknown"
