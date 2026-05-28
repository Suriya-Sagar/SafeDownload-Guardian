/**
 * KEYLOGGER SIMULATOR - FOR SECURITY TESTING ONLY
 * DO NOT RUN ON ACTUAL SYSTEMS
 */

class KeyloggerSimulator {
    constructor() {
        this.keys = [];
        this.sensitiveData = [];
        this.isRunning = false;
    }
    
    simulateKeyCapture() {
        console.log("[SIMULATION] Keylogger activated...");
        console.log("[SIMULATION] Capturing keystrokes would include:");
        
        const simulatedKeys = [
            "username: admin",
            "password: P@ssw0rd123",
            "email: victim@example.com",
            "creditcard: 4111-1111-1111-1111",
            "social: 123-45-6789"
        ];
        
        simulatedKeys.forEach(key => {
            console.log(`[SIMULATION] Captured: ${key}`);
            this.keys.push(key);
        });
    }
    
    simulateDataExfiltration() {
        console.log("\n[SIMULATION] Exfiltrating captured data...");
        console.log("[SIMULATION] Would send to C2 server: evil.com/exfil");
        
        // Simulate base64 encoding for exfiltration
        const encoded = btoa(JSON.stringify(this.keys));
        console.log(`[SIMULATION] Data encoded: ${encoded.substring(0, 50)}...`);
        
        // Simulate HTTP POST request
        console.log("[SIMULATION] HTTP POST to: https://malicious-server.com/collect");
    }
    
    simulateFormGrabbing() {
        console.log("\n[SIMULATION] Form grabbing activated...");
        console.log("[SIMULATION] Would capture form submissions from:");
        
        const forms = [
            "login forms",
            "payment forms",
            "registration forms",
            "contact forms"
        ];
        
        forms.forEach(form => {
            console.log(`[SIMULATION] Monitoring: ${form}`);
        });
    }
    
    simulateClipboardMonitoring() {
        console.log("\n[SIMULATION] Clipboard monitoring activated...");
        
        const clipboardData = [
            "Sensitive document content copied",
            "Password copied: SecurePass123",
            "API key copied: sk-1234567890abcdef"
        ];
        
        clipboardData.forEach(data => {
            console.log(`[SIMULATION] Clipboard captured: ${data}`);
            this.sensitiveData.push(data);
        });
    }
    
    run() {
        console.log("=".repeat(60));
        console.log("KEYLOGGER SIMULATION - SECURITY TEST");
        console.log("=".repeat(60));
        console.log("WARNING: This is a simulation. No actual keylogging occurs.");
        console.log("=".repeat(60));
        
        this.simulateKeyCapture();
        this.simulateFormGrabbing();
        this.simulateClipboardMonitoring();
        this.simulateDataExfiltration();
        
        console.log("\n[SIMULATION] Complete - System would be compromised");
        console.log("[SIMULATION] Your sandbox should detect:");
        console.log("  - Keylogging behavior");
        console.log("  - Data exfiltration attempts");
        console.log("  - Form grabbing");
        console.log("  - Clipboard monitoring");
        
        return {
            threat_level: "HIGH",
            type: "Keylogger Simulator",
            behaviors: ["Keylogging", "Data Exfiltration", "Form Grabbing", "Clipboard Monitoring"]
        };
    }
}

// Run simulation
const simulator = new KeyloggerSimulator();
const results = simulator.run();

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { KeyloggerSimulator, results };
}