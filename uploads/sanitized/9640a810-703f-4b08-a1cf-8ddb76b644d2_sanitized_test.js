for (let i = 0; i < str.length; i++) {
    let char = str[i];
    if (char >= 'a' && char <= 'z') {
      result += char.toUpperCase();
    } else {
      result += char;
    }
  }
  return result;
}

main();