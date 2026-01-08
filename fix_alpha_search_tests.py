"""Fix alphabetical index tests - they don't use ["items"] wrapper."""
import re
from pathlib import Path

test_file = Path("tests/integration/test_index_navigation.py")
content = test_file.read_text()

# For alphabetical index tests only (lines 20-100), remove the ["items"] additions
# Match patterns like index["A"]["items"] and change back to index["A"]
content = re.sub(
    r'index\["([A-Z#])"\]\["items"\]',
    r'index["\1"]',
    content
)

# For search index tests (lines 350-453), also remove ["items"]  
# Match patterns in search context
lines = content.split('\n')
in_search_test = False
for i, line in enumerate(lines):
    if 'class TestSearchIndex' in line:
        in_search_test = True
    elif 'class Test' in line and in_search_test:
        in_search_test = False
    
    if in_search_test and '["items"]' in line:
        # Search index returns Dict[str, List], not Dict[str, Dict]
        lines[i] = line.replace('["items"]', '')

content = '\n'.join(lines)

test_file.write_text(content)
print("Fixed alphabetical and search index tests")
