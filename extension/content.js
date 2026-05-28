// Content script for page interaction
// Can be used to detect download links and add custom UI if needed

console.log('File Security Guard content script loaded');

// Listen for messages from the page
window.addEventListener('message', (event) => {
  if (event.source !== window) return;
  
  if (event.data.type && event.data.type === 'FSG_DOWNLOAD_DETECTED') {
    console.log('Download detected from page:', event.data.url);
  }
});

// Optionally add a small indicator to download links
function addIndicatorToLinks() {
  const links = document.querySelectorAll('a[href]');
  links.forEach(link => {
    const href = link.href.toLowerCase();
    const isDownloadable = /\.(exe|zip|msi|dmg|pkg|apk)$/.test(href);
    
    if (isDownloadable && !link.hasAttribute('data-fsg-processed')) {
      link.setAttribute('data-fsg-processed', 'true');
      
      // Add a small shield icon to indicate protection
      const indicator = document.createElement('span');
      indicator.style.marginLeft = '4px';
      indicator.style.fontSize = '12px';
      indicator.innerHTML = '🛡️';
      indicator.title = 'Protected by File Security Guard';
      
      link.appendChild(indicator);
    }
  });
}

// Run after page loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', addIndicatorToLinks);
} else {
  addIndicatorToLinks();
}

// Re-run when DOM changes
const observer = new MutationObserver(addIndicatorToLinks);
observer.observe(document.body, { childList: true, subtree: true });