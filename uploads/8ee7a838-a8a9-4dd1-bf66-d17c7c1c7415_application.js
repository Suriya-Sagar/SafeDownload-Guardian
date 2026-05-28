// Dangerous JavaScript with eval()
console.log("Loading JavaScript application");

// UNSAFE: eval with user input
function processUserInput(input) {
    try {
        // DANGEROUS: Arbitrary code execution
        const result = eval(input);
        console.log("Result:", result);
        return result;
    } catch (error) {
        console.error("Error:", error);
        return null;
    }
}

// UNSAFE: setTimeout with string
function delayedCode() {
    setTimeout("console.log('Executed from string')", 1000);
}

// UNSAFE: document.write with user content
function displayContent(content) {
    document.write(content);
}

// Potential XSS
function updateElement(id, html) {
    document.getElementById(id).innerHTML = html;
}

// Usage
window.onload = function() {
    console.log("App loaded");
    
    // Get user input (simulated)
    const userCode = prompt("Enter JavaScript code to execute:");
    if (userCode) {
        processUserInput(userCode);
    }
};
