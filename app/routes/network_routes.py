from flask import Blueprint, render_template, jsonify
from ..utils import network_monitor
import psutil
import socket
import platform
import subprocess

network = Blueprint('network', __name__)

@network.route('/network')
def network_page():
    return render_template('network/network.html')

@network.route('/api/network/stats')
def get_network_stats():
    return jsonify(network_monitor.get_network_stats())

@network.route('/api/network/devices')
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
                    'local': conn.raddr.ip in local_addresses,
                    'ports': get_device_ports(conn.raddr.ip, connections)
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

def get_device_ports(ip, connections):
    """Get list of ports used by a device."""
    ports = set()
    for conn in connections:
        if conn.raddr and conn.raddr.ip == ip:
            ports.add(conn.raddr.port)
    return sorted(list(ports))

@network.route('/api/network/topology')
def get_network_topology():
    """Get network topology information."""
    try:
        devices = get_network_devices().json
        
        # Create nodes and links for network visualization
        nodes = []
        links = []
        
        # Add router node (assumed to be the gateway)
        nodes.append({
            'id': 'router',
            'name': 'Router',
            'type': 'router',
            'group': 1
        })
        
        # Add other devices
        for i, device in enumerate(devices):
            node_id = f"device_{i}"
            nodes.append({
                'id': node_id,
                'name': device['name'] or f"Device {i+1}",
                'type': device['type'],
                'ip': device['ip'],
                'mac': device['mac'],
                'group': get_device_group(device['type'])
            })
            
            # Link to router
            links.append({
                'source': 'router',
                'target': node_id,
                'value': 1
            })
        
        return jsonify({
            'nodes': nodes,
            'links': links
        })
    except Exception as e:
        print(f"Error getting network topology: {str(e)}")
        return jsonify({'nodes': [], 'links': []})

def get_device_group(device_type):
    """Get group number for device type (for visualization)."""
    groups = {
        'router': 1,
        'desktop': 2,
        'laptop': 2,
        'smartphone': 3,
        'printer': 4,
        'iot': 5,
        'other': 6
    }
    return groups.get(device_type, 6)
