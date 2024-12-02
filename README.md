# CyberShield AI Defence System

A comprehensive network security and monitoring platform with real-time packet analysis and threat detection capabilities.

## System Requirements
- Python 3.11+ (tested on Python 3.12)
- Administrator/Root privileges for packet capture
- Windows/Linux OS
- Network interface access

## Installation
1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
venv\Scripts\activate     # On Windows
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application
```bash
python run.py
```
Access the dashboard at: http://localhost:5000

## Feature Status

### Working Features

#### Network Monitoring
- Real-time packet capture and analysis
- Protocol distribution tracking
- Source/Destination IP monitoring
- Port usage statistics
- Basic packet filtering
- Packet length analysis

#### System Monitoring
- CPU usage tracking
- Memory utilization
- Disk space monitoring
- Network interface statistics
- Process monitoring

#### Security Features
- Port scanning detection
- Basic intrusion detection
- Network anomaly detection
- Traffic pattern analysis

#### Dashboard
- Real-time system metrics display
- Network traffic visualization
- Interactive charts and graphs
- System health indicators

### Partially Working Features

#### Network Analysis
- Deep packet inspection (limited functionality)
- Protocol-specific analysis (basic implementation)
- Traffic pattern recognition (needs optimization)

#### Security Features
- Threat detection (basic rules only)
- Alert system (needs configuration)
- Log analysis (basic implementation)

#### Dashboard Integration
- Real-time packet visualization (occasional delays)
- Custom filter application (basic filters only)
- Historical data viewing (limited functionality)

### Not Working/Under Development

#### Security Features
- Advanced threat detection
- Machine learning-based analysis
- Automated response system
- Vulnerability scanning
- Malware detection

#### Analysis Tools
- Advanced packet filtering
- Custom rule creation
- Traffic prediction
- Network topology mapping

#### Dashboard Features
- Custom dashboard layouts
- Advanced data export
- Report generation
- Alert customization

### Background Services (Running but Not Connected to Dashboard)

1. Advanced Packet Analysis Service
   - Detailed protocol analysis
   - Traffic pattern matching
   - Payload inspection
   - Status: Running independently, data not displayed

2. Network Forensics Module
   - Packet recording
   - Session reconstruction
   - Protocol decoding
   - Status: Functional but not integrated

3. Threat Intelligence Service
   - IP reputation checking
   - Known threat detection
   - Malicious pattern matching
   - Status: Active but not visualized

4. Performance Monitoring Service
   - Detailed performance metrics
   - Resource usage tracking
   - Network latency monitoring
   - Status: Collecting data, not displayed

## Known Issues
1. WebSocket connection may require reconnection after long periods
2. High CPU usage during intensive packet capture
3. Memory usage grows over time with packet capture enabled
4. Some features require elevated privileges
5. TripleDES deprecation warnings from Scapy library
6. Wireshark integration shows configuration warnings

## Security Notes
- Requires administrator privileges for packet capture
- Only monitors local network interfaces
- Implements basic access controls
- Handles sensitive network data

## Upcoming Features
1. Advanced machine learning integration
2. Improved threat detection algorithms
3. Enhanced visualization options
4. Custom rule engine
5. Automated response capabilities
6. Extended reporting features

## Contributing
Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
