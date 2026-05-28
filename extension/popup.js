// Popup script for Chrome extension

document.addEventListener('DOMContentLoaded', () => {
  loadStats();
  loadRecentDownloads();
  
  // Open dashboard button
  document.getElementById('openDashboard').addEventListener('click', () => {
    chrome.tabs.create({ url: 'http://127.0.0.1:5000' });
  });
  
  // Settings link
  document.getElementById('optionsLink').addEventListener('click', (e) => {
    e.preventDefault();
    chrome.runtime.openOptionsPage();
  });
});

function loadStats() {
  // Get stats from storage
  chrome.storage.local.get(['totalBlocked', 'totalAnalyzed', 'totalSanitized'], (result) => {
    document.getElementById('totalBlocked').textContent = result.totalBlocked || 0;
    document.getElementById('totalAnalyzed').textContent = result.totalAnalyzed || 0;
    document.getElementById('totalSanitized').textContent = result.totalSanitized || 0;
  });
}

function loadRecentDownloads() {
  chrome.storage.local.get(['recentDownloads'], (result) => {
    const downloads = result.recentDownloads || [];
    const listDiv = document.getElementById('downloadsList');
    
    if (downloads.length === 0) {
      listDiv.innerHTML = '<div class="empty-state">No recent downloads<br><small>Downloads will appear here</small></div>';
      return;
    }
    
    let html = '';
    downloads.slice(-5).reverse().forEach(download => {
      let statusColor = '#48bb78';
      if (download.risk > 70) statusColor = '#f56565';
      else if (download.risk > 40) statusColor = '#ed8936';
      
      html += `
        <div class="download-item">
          <span class="download-name">📄 ${download.filename}</span>
          <span class="download-status" style="background: ${statusColor}20; color: ${statusColor}">
            Risk: ${download.risk}
          </span>
        </div>
      `;
    });
    
    listDiv.innerHTML = html;
  });
}

// Listen for updates from background
chrome.runtime.onMessage.addListener((message) => {
  if (message.type === 'statsUpdated') {
    loadStats();
    loadRecentDownloads();
  }
});