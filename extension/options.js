// Options script for Chrome extension

const DEFAULT_FILE_TYPES = [
  '.exe', '.dll', '.scr', '.bat', '.ps1', '.vbs', '.js', '.py',
  '.php', '.rb', '.pl', '.sh', '.zip', '.rar', '.7z', '.doc',
  '.docx', '.xls', '.xlsx', '.pdf', '.jar', '.msi', '.apk', '.deb'
];

document.addEventListener('DOMContentLoaded', () => {
  loadSettings();
  renderFileTypes();
  
  document.getElementById('saveBtn').addEventListener('click', saveSettings);
  document.getElementById('testBtn').addEventListener('click', testConnection);
  document.getElementById('resetBtn').addEventListener('click', resetSettings);
});

function loadSettings() {
  chrome.storage.sync.get({
    backendUrl: 'http://127.0.0.1:5000',
    apiKey: '',
    enabled: true,
    notifications: true,
    autoOpen: true,
    fileTypes: DEFAULT_FILE_TYPES
  }, (items) => {
    document.getElementById('backendUrl').value = items.backendUrl;
    document.getElementById('apiKey').value = items.apiKey;
    document.getElementById('enabled').checked = items.enabled;
    document.getElementById('notifications').checked = items.notifications;
    document.getElementById('autoOpen').checked = items.autoOpen;
    
    // Check file type checkboxes
    items.fileTypes.forEach(ext => {
      const checkbox = document.getElementById(`ext_${ext}`);
      if (checkbox) checkbox.checked = true;
    });
  });
}

function renderFileTypes() {
  const container = document.getElementById('fileTypes');
  container.innerHTML = '';
  
  DEFAULT_FILE_TYPES.forEach(ext => {
    const div = document.createElement('div');
    div.className = 'file-type-item';
    
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.id = `ext_${ext}`;
    checkbox.value = ext;
    
    const label = document.createElement('label');
    label.htmlFor = `ext_${ext}`;
    label.textContent = ext;
    
    div.appendChild(checkbox);
    div.appendChild(label);
    container.appendChild(div);
  });
}

function getSelectedFileTypes() {
  const checkboxes = document.querySelectorAll('#fileTypes input[type="checkbox"]:checked');
  return Array.from(checkboxes).map(cb => cb.value);
}

function saveSettings() {
  const settings = {
    backendUrl: document.getElementById('backendUrl').value,
    apiKey: document.getElementById('apiKey').value,
    enabled: document.getElementById('enabled').checked,
    notifications: document.getElementById('notifications').checked,
    autoOpen: document.getElementById('autoOpen').checked,
    fileTypes: getSelectedFileTypes()
  };
  
  chrome.storage.sync.set(settings, () => {
    showStatus('Settings saved successfully!', 'success');
    
    // Update background script
    chrome.runtime.sendMessage({
      type: 'updateSettings',
      settings: settings
    });
  });
}

async function testConnection() {
  const backendUrl = document.getElementById('backendUrl').value;
  
  showStatus('Testing connection...', 'info');
  
  try {
    const response = await fetch(`${backendUrl}/api/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      showStatus('✅ Connection successful!', 'success');
    } else {
      showStatus(`❌ Server returned: ${response.status}`, 'error');
    }
  } catch (error) {
    showStatus(`❌ Connection failed: ${error.message}`, 'error');
  }
}

function resetSettings() {
  chrome.storage.sync.set({
    backendUrl: 'http://127.0.0.1:5000',
    apiKey: '',
    enabled: true,
    notifications: true,
    autoOpen: true,
    fileTypes: DEFAULT_FILE_TYPES
  }, () => {
    loadSettings();
    showStatus('Settings reset to defaults', 'success');
  });
}

function showStatus(message, type) {
  const status = document.getElementById('statusMessage');
  status.textContent = message;
  status.className = `status-message status-${type}`;
  
  setTimeout(() => {
    status.style.display = 'none';
  }, 3000);
}