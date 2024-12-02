// Network monitoring functions
let networkHistory = {
    download: [],
    upload: [],
    timestamp: [],
    devices: new Map() // Track devices over time
};

// Keep track of active modal
let activeModal = null;
let modalUpdateInterval = null;

function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 B/s';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['B/s', 'KB/s', 'MB/s', 'GB/s'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// System processes to filter out
const systemProcesses = [
    'svchost.exe',
    'msedge.exe',
    'language_server_windows',
    'ArmouryCrate',
    'Aura',
    'System',
    'python.exe',
    'Windsurf.exe'
];

function isSystemProcess(processName) {
    return systemProcesses.some(sysProc => processName.toLowerCase().includes(sysProc.toLowerCase()));
}

function updateDashboardNetworkStats() {
    fetch('/api/network-stats')
        .then(response => response.json())
        .then(data => {
            // Update current speeds
            document.getElementById('dashboardDownloadSpeed').textContent = formatBytes(data.download_speed);
            document.getElementById('dashboardUploadSpeed').textContent = formatBytes(data.upload_speed);
            document.getElementById('dashboardActiveConnections').textContent = data.connections;

            // Store historical data (keep last 20 readings)
            const now = new Date().toLocaleTimeString();
            networkHistory.download.push(data.download_speed);
            networkHistory.upload.push(data.upload_speed);
            networkHistory.timestamp.push(now);

            if (networkHistory.download.length > 20) {
                networkHistory.download.shift();
                networkHistory.upload.shift();
                networkHistory.timestamp.shift();
            }

            // Update modal if open
            if (activeModal) {
                updateActiveModal();
            }
        })
        .catch(error => console.error('Error fetching network stats:', error));
}

function updateActiveModal() {
    switch (activeModal) {
        case 'download':
            showSpeedDetails('download', true);
            break;
        case 'upload':
            showSpeedDetails('upload', true);
            break;
        case 'connections':
            showConnectionCount(true);
            break;
        case 'devices':
            showDeviceDetails(true);
            break;
    }
}

function showSpeedDetails(type, isUpdate = false) {
    const modal = document.getElementById('connectionModal');
    const modalContent = document.getElementById('connectionModalContent');
    
    if (!isUpdate) {
        activeModal = type;
        startModalUpdates();
    }
    
    const speeds = type === 'download' ? networkHistory.download : networkHistory.upload;
    const timestamps = networkHistory.timestamp;
    
    const avgSpeed = speeds.length ? speeds.reduce((a, b) => a + b, 0) / speeds.length : 0;
    const maxSpeed = speeds.length ? Math.max(...speeds) : 0;
    const minSpeed = speeds.length ? Math.min(...speeds) : 0;
    
    modalContent.innerHTML = `
        <div class="bg-white p-6 rounded-lg shadow-xl max-w-2xl w-full">
            <div class="flex justify-between items-start mb-4">
                <h3 class="text-lg font-semibold text-gray-900">
                    ${type.charAt(0).toUpperCase() + type.slice(1)} Speed Statistics
                    <span class="text-sm text-gray-500 ml-2">(Auto-updating)</span>
                </h3>
                <button onclick="closeModal()" class="text-gray-400 hover:text-gray-500">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="space-y-6">
                <div class="grid grid-cols-3 gap-4">
                    <div class="bg-gray-50 p-4 rounded-lg">
                        <div class="text-sm text-gray-500">Average</div>
                        <div class="text-lg font-semibold ${type === 'download' ? 'text-green-600' : 'text-blue-600'}">
                            ${formatBytes(avgSpeed)}
                        </div>
                    </div>
                    <div class="bg-gray-50 p-4 rounded-lg">
                        <div class="text-sm text-gray-500">Maximum</div>
                        <div class="text-lg font-semibold ${type === 'download' ? 'text-green-600' : 'text-blue-600'}">
                            ${formatBytes(maxSpeed)}
                        </div>
                    </div>
                    <div class="bg-gray-50 p-4 rounded-lg">
                        <div class="text-sm text-gray-500">Minimum</div>
                        <div class="text-lg font-semibold ${type === 'download' ? 'text-green-600' : 'text-blue-600'}">
                            ${formatBytes(minSpeed)}
                        </div>
                    </div>
                </div>
                <div>
                    <h4 class="text-sm font-medium text-gray-700 mb-3">Speed History (Last 20 readings)</h4>
                    <div class="bg-gray-50 p-4 rounded-lg">
                        <div class="space-y-2 max-h-60 overflow-y-auto">
                            ${speeds.map((speed, i) => `
                                <div class="flex items-center justify-between text-sm border-b border-gray-100 py-1 last:border-0">
                                    <span class="text-gray-500">${timestamps[i]}</span>
                                    <span class="${type === 'download' ? 'text-green-600' : 'text-blue-600'} font-medium">
                                        ${formatBytes(speed)}
                                    </span>
                                </div>
                            `).reverse().join('')}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    if (!isUpdate) {
        modal.classList.remove('hidden');
    }
}

function showConnectionCount(isUpdate = false) {
    fetch('/api/active-connections')
        .then(response => response.json())
        .then(connections => {
            const modal = document.getElementById('connectionModal');
            const modalContent = document.getElementById('connectionModalContent');
            
            if (!isUpdate) {
                activeModal = 'connections';
                startModalUpdates();
            }

            // Count connections by status
            const statusCounts = connections.reduce((acc, conn) => {
                acc[conn.status] = (acc[conn.status] || 0) + 1;
                return acc;
            }, {});

            // Count connections by process
            const processCounts = connections.reduce((acc, conn) => {
                acc[conn.process] = (acc[conn.process] || 0) + 1;
                return acc;
            }, {});

            modalContent.innerHTML = `
                <div class="bg-white p-6 rounded-lg shadow-xl max-w-2xl w-full">
                    <div class="flex justify-between items-start mb-4">
                        <h3 class="text-lg font-semibold text-gray-900">Connection Statistics</h3>
                        <button onclick="closeModal()" class="text-gray-400 hover:text-gray-500">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="grid grid-cols-2 gap-6">
                        <div>
                            <h4 class="text-sm font-medium text-gray-700 mb-3">Status Distribution</h4>
                            <div class="bg-gray-50 p-4 rounded-lg">
                                <div class="space-y-3">
                                    ${Object.entries(statusCounts).map(([status, count]) => `
                                        <div class="flex items-center justify-between">
                                            <span class="text-sm text-gray-600">${status}</span>
                                            <span class="px-2 py-1 text-xs font-medium rounded-full 
                                                ${status === 'ESTABLISHED' ? 'bg-green-100 text-green-800' : 
                                                status === 'LISTENING' ? 'bg-blue-100 text-blue-800' : 
                                                'bg-gray-100 text-gray-800'}">
                                                ${count}
                                            </span>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                        <div>
                            <h4 class="text-sm font-medium text-gray-700 mb-3">Top Processes</h4>
                            <div class="bg-gray-50 p-4 rounded-lg">
                                <div class="space-y-3">
                                    ${Object.entries(processCounts)
                                        .sort((a, b) => b[1] - a[1])
                                        .slice(0, 5)
                                        .map(([process, count]) => `
                                            <div class="flex items-center justify-between">
                                                <span class="text-sm text-gray-600 truncate max-w-[200px]" title="${process}">
                                                    ${process}
                                                </span>
                                                <span class="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-800 rounded-full">
                                                    ${count}
                                                </span>
                                            </div>
                                        `).join('')}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            if (!isUpdate) {
                modal.classList.remove('hidden');
            }
        })
        .catch(error => console.error('Error fetching connections:', error));
}

function showDeviceDetails(isUpdate = false) {
    fetch('/api/network-devices')
        .then(response => response.json())
        .then(devices => {
            const modal = document.getElementById('connectionModal');
            const modalContent = document.getElementById('connectionModalContent');
            
            if (!isUpdate) {
                activeModal = 'devices';
                startModalUpdates();
            }

            // Track devices in history
            devices.forEach(device => {
                if (!networkHistory.devices.has(device.mac)) {
                    networkHistory.devices.set(device.mac, {
                        firstSeen: new Date().toLocaleString(),
                        ...device
                    });
                }
            });

            // Group devices by type
            const deviceTypes = devices.reduce((acc, device) => {
                acc[device.type] = (acc[device.type] || 0) + 1;
                return acc;
            }, {});

            modalContent.innerHTML = `
                <div class="bg-white p-6 rounded-lg shadow-xl max-w-4xl w-full">
                    <div class="flex justify-between items-start mb-4">
                        <h3 class="text-lg font-semibold text-gray-900">
                            Connected Devices
                            <span class="text-sm text-gray-500 ml-2">(Auto-updating)</span>
                        </h3>
                        <button onclick="closeModal()" class="text-gray-400 hover:text-gray-500">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="space-y-6">
                        <div class="grid grid-cols-4 gap-4">
                            <div class="bg-gray-50 p-4 rounded-lg">
                                <div class="text-sm text-gray-500">Total Devices</div>
                                <div class="text-lg font-semibold text-purple-600">${devices.length}</div>
                            </div>
                            ${Object.entries(deviceTypes).map(([type, count]) => `
                                <div class="bg-gray-50 p-4 rounded-lg">
                                    <div class="text-sm text-gray-500">${type}</div>
                                    <div class="text-lg font-semibold text-purple-600">${count}</div>
                                </div>
                            `).join('')}
                        </div>
                        <div class="bg-white rounded-lg">
                            <div class="overflow-x-auto">
                                <table class="min-w-full divide-y divide-gray-200">
                                    <thead class="bg-gray-50">
                                        <tr>
                                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Device Name</th>
                                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">IP Address</th>
                                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">MAC Address</th>
                                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">First Seen</th>
                                        </tr>
                                    </thead>
                                    <tbody class="bg-white divide-y divide-gray-200">
                                        ${devices.map(device => {
                                            const deviceHistory = networkHistory.devices.get(device.mac);
                                            return `
                                                <tr class="hover:bg-gray-50">
                                                    <td class="px-4 py-3 whitespace-nowrap">
                                                        <div class="flex items-center">
                                                            <i class="fas ${getDeviceIcon(device.type)} text-gray-400 mr-2"></i>
                                                            <div class="text-sm font-medium text-gray-900">
                                                                ${device.name || 'Unknown Device'}
                                                            </div>
                                                        </div>
                                                    </td>
                                                    <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                                                        ${device.ip}
                                                    </td>
                                                    <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                                                        ${device.mac}
                                                    </td>
                                                    <td class="px-4 py-3 whitespace-nowrap">
                                                        <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                                                            ${device.type}
                                                        </span>
                                                    </td>
                                                    <td class="px-4 py-3 whitespace-nowrap">
                                                        <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                                                            ${device.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
                                                            ${device.active ? 'Active' : 'Inactive'}
                                                        </span>
                                                    </td>
                                                    <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                                                        ${deviceHistory ? deviceHistory.firstSeen : 'Just Now'}
                                                    </td>
                                                </tr>
                                            `;
                                        }).join('')}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div class="bg-gray-50 p-4 rounded-lg">
                            <h4 class="text-sm font-medium text-gray-700 mb-2">Network Security Status</h4>
                            <div class="space-y-2">
                                <div class="flex items-center justify-between">
                                    <span class="text-sm text-gray-600">Unknown Devices</span>
                                    <span class="px-2 py-1 text-xs font-medium rounded-full 
                                        ${devices.filter(d => !d.name).length > 0 ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}">
                                        ${devices.filter(d => !d.name).length}
                                    </span>
                                </div>
                                <div class="flex items-center justify-between">
                                    <span class="text-sm text-gray-600">New Devices (Last 24h)</span>
                                    <span class="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                                        ${devices.filter(d => {
                                            const history = networkHistory.devices.get(d.mac);
                                            if (!history) return true;
                                            const hours = (new Date() - new Date(history.firstSeen)) / (1000 * 60 * 60);
                                            return hours < 24;
                                        }).length}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            if (!isUpdate) {
                modal.classList.remove('hidden');
            }
        })
        .catch(error => console.error('Error fetching device information:', error));
}

function getDeviceIcon(deviceType) {
    const icons = {
        'smartphone': 'fa-mobile-alt',
        'laptop': 'fa-laptop',
        'desktop': 'fa-desktop',
        'tablet': 'fa-tablet-alt',
        'printer': 'fa-print',
        'router': 'fa-network-wired',
        'iot': 'fa-microchip',
        'other': 'fa-question-circle'
    };
    return icons[deviceType.toLowerCase()] || 'fa-question-circle';
}

function startModalUpdates() {
    if (modalUpdateInterval) {
        clearInterval(modalUpdateInterval);
    }
    modalUpdateInterval = setInterval(updateActiveModal, 3000);
}

function closeModal() {
    const modal = document.getElementById('connectionModal');
    modal.classList.add('hidden');
    activeModal = null;
    if (modalUpdateInterval) {
        clearInterval(modalUpdateInterval);
        modalUpdateInterval = null;
    }
}

function updateDashboardConnections(showSystemProcesses = false) {
    fetch('/api/active-connections')
        .then(response => response.json())
        .then(connections => {
            const tbody = document.getElementById('recentConnectionsTable');
            tbody.innerHTML = '';

            // Filter connections based on showSystemProcesses flag
            const filteredConnections = connections.filter(conn => 
                showSystemProcesses || !isSystemProcess(conn.process)
            );

            // Show only the first 5 connections
            filteredConnections.slice(0, 5).forEach(conn => {
                const row = document.createElement('tr');
                row.className = 'hover:bg-gray-50 transition-colors duration-200';
                
                // Determine if this is a system process
                const isSystem = isSystemProcess(conn.process);
                const processClass = isSystem ? 'text-gray-500' : 'text-gray-900';
                const processIcon = isSystem ? 'fa-cog' : 'fa-desktop';
                
                row.innerHTML = `
                    <td class="px-4 py-2 whitespace-nowrap">
                        <div class="flex items-center">
                            <i class="fas ${processIcon} ${isSystem ? 'text-gray-400' : 'text-blue-400'} mr-2"></i>
                            <div class="text-sm ${processClass} font-medium">${conn.process}</div>
                        </div>
                    </td>
                    <td class="px-4 py-2 whitespace-nowrap">
                        <div class="text-sm text-gray-500">${conn.local_address}</div>
                        <div class="text-xs text-gray-400">${conn.remote_address || 'N/A'}</div>
                    </td>
                    <td class="px-4 py-2 whitespace-nowrap">
                        <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                            ${conn.status === 'ESTABLISHED' ? 'bg-green-100 text-green-800' : 
                            conn.status === 'LISTENING' ? 'bg-blue-100 text-blue-800' : 
                            'bg-gray-100 text-gray-800'}">
                            ${conn.status}
                        </span>
                    </td>
                    <td class="px-4 py-2 whitespace-nowrap text-right text-sm">
                        <button onclick="showConnectionDetails('${conn.process}', '${conn.local_address}', '${conn.remote_address || 'N/A'}', '${conn.status}')" 
                                class="text-blue-600 hover:text-blue-900">
                            <i class="fas fa-info-circle"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(row);
            });

            // Update connection count
            const totalConnections = filteredConnections.length;
            document.getElementById('connectionCount').textContent = 
                `Showing ${Math.min(5, totalConnections)} of ${totalConnections} connections`;
        })
        .catch(error => console.error('Error fetching connections:', error));
}

function showConnectionDetails(process, localAddr, remoteAddr, status) {
    const modal = document.getElementById('connectionModal');
    const modalContent = document.getElementById('connectionModalContent');
    
    modalContent.innerHTML = `
        <div class="bg-white p-6 rounded-lg shadow-xl max-w-lg w-full">
            <div class="flex justify-between items-start mb-4">
                <h3 class="text-lg font-semibold text-gray-900">Connection Details</h3>
                <button onclick="closeConnectionModal()" class="text-gray-400 hover:text-gray-500">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="space-y-4">
                <div>
                    <label class="text-sm font-medium text-gray-500">Process</label>
                    <p class="mt-1 text-sm text-gray-900">${process}</p>
                </div>
                <div>
                    <label class="text-sm font-medium text-gray-500">Local Address</label>
                    <p class="mt-1 text-sm text-gray-900">${localAddr}</p>
                </div>
                <div>
                    <label class="text-sm font-medium text-gray-500">Remote Address</label>
                    <p class="mt-1 text-sm text-gray-900">${remoteAddr}</p>
                </div>
                <div>
                    <label class="text-sm font-medium text-gray-500">Status</label>
                    <p class="mt-1">
                        <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                            ${status === 'ESTABLISHED' ? 'bg-green-100 text-green-800' : 
                            status === 'LISTENING' ? 'bg-blue-100 text-blue-800' : 
                            'bg-gray-100 text-gray-800'}">
                            ${status}
                        </span>
                    </p>
                </div>
            </div>
        </div>
    `;
    
    modal.classList.remove('hidden');
}

function closeConnectionModal() {
    const modal = document.getElementById('connectionModal');
    modal.classList.add('hidden');
}

function toggleSystemProcesses() {
    const checkbox = document.getElementById('showSystemProcesses');
    updateDashboardConnections(checkbox.checked);
}

// Initialize network monitoring
function initializeNetworkMonitoring() {
    // Update dashboard network stats every 3 seconds
    setInterval(updateDashboardNetworkStats, 3000);
    setInterval(() => {
        const checkbox = document.getElementById('showSystemProcesses');
        updateDashboardConnections(checkbox ? checkbox.checked : false);
    }, 3000);

    // Initial updates
    updateDashboardNetworkStats();
    updateDashboardConnections(false);

    // Close modal when clicking outside
    const modal = document.getElementById('connectionModal');
    modal.addEventListener('click', (event) => {
        if (event.target === modal) {
            closeModal();
        }
    });

    // Add click handlers for network stats
    document.getElementById('dashboardDownloadSpeed').parentElement.addEventListener('click', () => showSpeedDetails('download'));
    document.getElementById('dashboardUploadSpeed').parentElement.addEventListener('click', () => showSpeedDetails('upload'));
    document.getElementById('dashboardActiveConnections').parentElement.addEventListener('click', () => showConnectionCount());
    document.getElementById('connectedDevices').addEventListener('click', showDeviceDetails);
}

// Start monitoring when the page loads
document.addEventListener('DOMContentLoaded', initializeNetworkMonitoring);
