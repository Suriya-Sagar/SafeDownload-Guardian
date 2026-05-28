// Background service worker for Chrome extension

// Configuration
let config = {
  backendUrl: 'http://127.0.0.1:5000',
  enabled: true,
  notifications: true,
  autoOpen: true
};

// Track downloads to avoid loops
const processedDownloads = new Set();

// Load saved settings
chrome.storage.sync.get(['backendUrl', 'enabled', 'notifications', 'autoOpen'], (result) => {
  if (result.backendUrl) config.backendUrl = result.backendUrl;
  if (result.enabled !== undefined) config.enabled = result.enabled;
  if (result.notifications !== undefined) config.notifications = result.notifications;
  if (result.autoOpen !== undefined) config.autoOpen = result.autoOpen;
  console.log('File Security Guard active with config:', config);
});

// Listen for download events
chrome.downloads.onCreated.addListener(async (downloadItem) => {
  try {
    // Skip if extension is disabled
    if (!config.enabled) return;
    
    // Skip if this is a download from our own backend
    if (downloadItem.url.includes(config.backendUrl)) {
      console.log('Skipping our own download:', downloadItem.url);
      return;
    }
    
    // Skip if already processed
    if (processedDownloads.has(downloadItem.id)) {
      processedDownloads.delete(downloadItem.id);
      return;
    }
    
    console.log('🔍 Intercepting download:', downloadItem.url);
    
    // Get filename
    const filename = downloadItem.filename || getFilenameFromUrl(downloadItem.url);
    
    // Cancel the download immediately
    try {
      await chrome.downloads.cancel(downloadItem.id);
      await chrome.downloads.erase({ id: downloadItem.id });
      console.log('✅ Download cancelled and removed');
    } catch (e) {
      console.log('Note: Download already completed or cancelled');
    }
    
    // Show notification
    if (config.notifications) {
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon192.png',
        title: 'File Security Guard',
        message: `Analyzing: ${filename}`,
        priority: 2
      });
    }
    
    // Send to backend for analysis
    console.log('📤 Sending to backend:', config.backendUrl);
    
    const response = await fetch(`${config.backendUrl}/api/analyze-url`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        url: downloadItem.url,
        filename: filename
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('📥 Backend response:', data);
    
    if (data.success) {
      console.log('✅ Analysis started with ID:', data.analysis_id);
      
      // Store analysis info
      chrome.storage.local.set({
        [`analysis_${data.analysis_id}`]: {
          filename: filename,
          url: downloadItem.url,
          timestamp: Date.now()
        }
      });
      
      // Auto-open dashboard if enabled
      if (config.autoOpen) {
        setTimeout(() => {
          chrome.tabs.create({ url: `${config.backendUrl}/?analysis=${data.analysis_id}` });
        }, 1000);
      }
      
      if (config.notifications) {
        chrome.notifications.create({
          type: 'basic',
          iconUrl: 'icons/icon192.png',
          title: 'Analysis Started',
          message: `${filename} is being analyzed in the sandbox`,
          priority: 2
        });
      }
    } else if (data.decision === 'allow') {
      // File type not monitored, open directly
      console.log('File type not monitored, opening directly');
      window.open(downloadItem.url, '_blank');
    }
    
  } catch (error) {
    console.error('❌ Error intercepting download:', error);
    
    if (config.notifications) {
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon192.png',
        title: 'File Security Guard - Error',
        message: `Could not analyze: ${error.message}`,
        priority: 2
      });
    }
  }
});

// Helper function to get filename from URL
function getFilenameFromUrl(url) {
  try {
    const urlObj = new URL(url);
    let filename = urlObj.pathname.split('/').pop();
    if (!filename || filename === '') {
      filename = 'download.bin';
    }
    return decodeURIComponent(filename);
  } catch {
    return 'download.bin';
  }
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'getConfig') {
    sendResponse(config);
  } else if (message.type === 'updateConfig') {
    config = { ...config, ...message.config };
    chrome.storage.sync.set(config);
    sendResponse({ success: true });
  }
  return true;
});

// Handle extension installation
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('File Security Guard installed');
    chrome.tabs.create({ url: 'http://127.0.0.1:5000' });
    
    // Initialize storage
    chrome.storage.local.set({
      totalAnalyzed: 0,
      totalBlocked: 0,
      totalSanitized: 0,
      recentDownloads: []
    });
  }
});