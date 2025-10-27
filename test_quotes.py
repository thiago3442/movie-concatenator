import re

with open('transcripts/olympic_games.txt', 'r', encoding='utf-8') as f:
    content = f.read()

print("First 200 characters:")
print(repr(content[:200]))
print("\n" + "="*60 + "\n")

# Show the actual quote characters
for i, char in enumerate(content[:50]):
    if char in '"""\'':
        print(f"Position {i}: {repr(char)} (Unicode: U+{ord(char):04X})")

print("\n" + "="*60 + "\n")

# Test different patterns
patterns = [
    (r'"([^"]+)"', 'ASCII double quotes'),
    (r'"([^"]+)"', 'Left/right smart quotes'),
    (r'[""]([^""]+)[""]', 'Either smart quote'),
]

for pattern, desc in patterns:
    sentences = re.findall(pattern, content)
    print(f"{desc}: Found {len(sentences)} sentences")
    if sentences:
        print(f"  First: {sentences[0][:50]}...")
