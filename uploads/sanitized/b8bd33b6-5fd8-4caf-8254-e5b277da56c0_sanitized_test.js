// REMOVED: const request = require('request'); // Reason: Network communication detected - potential data exfiltration
// REMOVED: const https = require('https'); // Reason: Network communication detected - potential data exfiltration
// REMOVED: const fs = require('fs'); // Reason: File system access potentially used for malicious purposes
// REMOVED: function pay() { // Reason: Ransomware indicator
// REMOVED:   console.log("Payment instructions..."); // Reason: Ransomware indicator
// REMOVED: }
// REMOVED: function keylogger() { // Reason: Keylogger indicator
// REMOVED:   // Keylogging code here // Reason: Keylogger indicator
// REMOVED: }
// REMOVED: function sendData(data) { // Reason: Data exfiltration
// REMOVED:   // Network request to send data // Reason: Data exfiltration
// REMOVED: }
// REMOVED: function reverseShell() { // Reason: Reverse shell connection
// REMOVED:   // Reverse shell code here // Reason: Reverse shell connection
// REMOVED: }
// REMOVED: function decodeAndExecute(encodedString) { // Reason: Base64 decode and exec/eval
// REMOVED:   // Decode and execute code // Reason: Base64 decode and exec/eval
// REMOVED: }
// REMOVED: eval(decodedString); // Reason: Executing arbitrary code
// REMOVED: setTimeout(function() { // Reason: Hidden function execution
// REMOVED:   // Malicious code // Reason: Hidden function execution
// REMOVED: }, 5000);

function fibonacci(n) {
  if (n <= 1) {
    return n;
  } else {
    return fibonacci(n - 1) + fibonacci(n - 2);
  }
}

function calculateSum(a, b) {
  return a + b;
}

function greetUser(name) {
  console.log("Hello, " + name + "!");
}

// Example usage
let number = 10;
console.log("Fibonacci of " + number + " is: " + fibonacci(number));

let num1 = 5;
let num2 = 3;
console.log("Sum of " + num1 + " and " + num2 + " is: " + calculateSum(num1, num2));

let userName = "Alice";
greetUser(userName);