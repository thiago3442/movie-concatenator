with open('transcripts/olympic_games.txt', 'r', encoding='utf-8') as f:
    content = f.read()

print("Raw content:")
print(repr(content))
print("\n" + "="*60 + "\n")

print("Split by lines:")
for i, line in enumerate(content.strip().split('\n')):
    print(f"Line {i}: {repr(line)}")
    print(f"  Starts with '\"': {line.startswith(chr(34))}")
    print(f"  Ends with '\"': {line.endswith(chr(34))}")
    print(f"  First char code: {ord(line[0]) if line else 'empty'}")
    print(f"  Last char code: {ord(line[-1]) if line else 'empty'}")
    print()
