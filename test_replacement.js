// Test the LINEBREAK replacement logic
const testText = 'Yo, this YOLO\'s the new king on the scene|||LINEBREAK|||one look at the image, it knows what I mean!|||LINEBREAK|||Detects objects fast, no need to re-process';

console.log('Original text:');
console.log(testText);
console.log('\nLength:', testText.length);

console.log('\nSearching for |||LINEBREAK|||:');
console.log('Contains separator?', testText.includes('|||LINEBREAK|||'));
console.log('Regex test:', /\|\|\|LINEBREAK\|\|\|/.test(testText));

console.log('\nAfter replacement:');
const processed = testText.replace(/\|\|\|LINEBREAK\|\|\|/g, '<br />');
console.log(processed);

console.log('\nDifference in length:', processed.length - testText.length);
