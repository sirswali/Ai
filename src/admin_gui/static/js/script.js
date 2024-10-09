// Existing code...

// System Health Monitoring functions
function updateSystemHealth() {
    sendAjaxRequest('/api/system-health', 'GET', {}, 
        (data) => {
            document.getElementById('cpuUsage').textContent = `${data.cpu_usage}%`;
            document.getElementById('memoryUsage').textContent = `${data.memory_usage}%`;
            document.getElementById('diskUsage').textContent = `${data.disk_usage}%`;
        },
        (error) => showNotification('Error fetching system health data', 'error')
    );
}

function updateSystemLogs() {
    sendAjaxRequest('/api/system-logs', 'GET', {}, 
        (data) => {
            const logsContainer = document.getElementById('systemLogs');
            logsContainer.innerHTML = data.logs.map(log => `<p class="mb-2">${log}</p>`).join('');
        },
        (error) => showNotification('Error fetching system logs', 'error')
    );
}

// Existing code...

// Add event listeners when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Existing event listeners...

    // System Health Monitoring
    if (document.getElementById('cpuUsage')) {
        updateSystemHealth();
        updateSystemLogs();
        setInterval(() => {
            updateSystemHealth();
            updateSystemLogs();
        }, 5000); // Update every 5 seconds
    }
});

// Existing code...