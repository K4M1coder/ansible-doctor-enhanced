"""Script to fix test_index_navigation.py imports and item creation."""
import re
from pathlib import Path

test_file = Path("tests/integration/test_index_navigation.py")
content = test_file.read_text()

# Replace IndexGenerator with DefaultIndexGenerator
content = content.replace(
    "from ansibledoctor.generator.indexes import IndexGenerator",
    "from ansibledoctor.generator.indexes import DefaultIndexGenerator"
)

content = content.replace(
    "generator = IndexGenerator()",
    "generator = DefaultIndexGenerator(output_dir=tmp_path)"
)

# Fix the items - replace _make_index_item("key": value) with _make_index_item(key=value)
# This handles the case where the regex replaced {} with _make_index_item() but kept the quotes
content = re.sub(
    r'_make_index_item\("(\w+)":\s*',
    r'_make_index_item(\1=',
    content
)

# Also fix subsequent parameters in the same call
content = re.sub(
    r',\s*"(\w+)":\s*',
    r', \1=',
    content
)

# Save
test_file.write_text(content)
print("Fixed all syntax issues")


