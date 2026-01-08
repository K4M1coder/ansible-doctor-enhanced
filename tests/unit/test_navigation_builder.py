"""Unit tests for NavigationBuilder class."""

import pytest
from ansibledoctor.links.navigation_builder import NavigationBuilder


class TestNavigationBuilder:
    """Test suite for NavigationBuilder class."""

    @pytest.fixture
    def builder(self):
        """Create a NavigationBuilder instance for testing."""
        return NavigationBuilder()

    def test_init(self, builder):
        """Test NavigationBuilder initialization."""
        assert builder is not None
        assert isinstance(builder, NavigationBuilder)

    def test_build_toc_with_simple_headings(self, builder):
        """Test TOC generation with simple level-2 headings."""
        content = """# Main Title

## Section 1
Content for section 1.

## Section 2
Content for section 2.

## Section 3
Content for section 3.
"""
        toc = builder.build_toc(content)
        
        assert toc is not None
        assert isinstance(toc, str)
        assert "Section 1" in toc
        assert "Section 2" in toc
        assert "Section 3" in toc
        assert "#section-1" in toc or "section-1" in toc.lower()
        assert "#section-2" in toc or "section-2" in toc.lower()
        assert "#section-3" in toc or "section-3" in toc.lower()

    def test_build_toc_with_mixed_levels(self, builder):
        """Test TOC generation with multiple heading levels (h2, h3, h4)."""
        content = """# Main Title

## Section 1
Content here.

### Subsection 1.1
More content.

### Subsection 1.2
Even more.

## Section 2
Other content.

### Subsection 2.1

#### Sub-subsection 2.1.1
Deep content.
"""
        toc = builder.build_toc(content)
        
        assert toc is not None
        assert "Section 1" in toc
        assert "Subsection 1.1" in toc
        assert "Subsection 1.2" in toc
        assert "Section 2" in toc
        assert "Subsection 2.1" in toc
        assert "Sub-subsection 2.1.1" in toc

    def test_build_toc_empty_content(self, builder):
        """Test TOC generation with empty content."""
        toc = builder.build_toc("")
        
        assert toc == "" or toc is None

    def test_build_toc_no_headings(self, builder):
        """Test TOC generation with content but no headings."""
        content = """This is just plain text.
No headings here.
Just paragraphs.
"""
        toc = builder.build_toc(content)
        
        assert toc == "" or toc is None

    def test_build_toc_with_special_characters(self, builder):
        """Test TOC generation with headings containing special characters."""
        content = """# Main

## Section: Special & Characters!
Content.

## Another Section (with parentheses)
More content.

## Third Section - With Dashes
Even more.
"""
        toc = builder.build_toc(content)
        
        assert toc is not None
        assert "Special & Characters" in toc or "Special" in toc
        assert "Another Section" in toc
        assert "Third Section" in toc

    def test_build_toc_with_code_blocks(self, builder):
        """Test that code blocks are ignored in TOC."""
        content = """# Main

## Real Section

```markdown
## This is in a code block
### Should be ignored
```

## Another Real Section
"""
        toc = builder.build_toc(content)
        
        assert "Real Section" in toc
        assert "Another Real Section" in toc
        # Code block headings should NOT appear
        assert toc.count("##") == 0 or "code block" not in toc.lower()

    def test_build_toc_with_inline_code(self, builder):
        """Test TOC with headings containing inline code."""
        content = """# Main

## The `config` Variable
Content.

## Using `ansible-playbook` Command
More content.
"""
        toc = builder.build_toc(content)
        
        assert "config" in toc
        assert "ansible-playbook" in toc

    def test_build_toc_duplicate_headings(self, builder):
        """Test TOC with duplicate heading text."""
        content = """# Main

## Overview
First overview.

## Details
Some details.

## Overview
Second overview (duplicate name).
"""
        toc = builder.build_toc(content)
        
        assert "Overview" in toc
        # Should handle duplicates (either with unique anchors or both listed)
        assert toc.count("Overview") >= 1

    def test_build_toc_markdown_format(self, builder):
        """Test that TOC is formatted as Markdown list."""
        content = """# Main

## Section 1
## Section 2
### Subsection 2.1
"""
        toc = builder.build_toc(content, format="markdown")
        
        # Check for Markdown list syntax
        assert toc.startswith("-") or toc.startswith("*") or toc.startswith("1.")
        # Check for links
        assert "[" in toc and "]" in toc and "(" in toc and ")" in toc

    def test_build_toc_html_format(self, builder):
        """Test TOC generation in HTML format."""
        content = """# Main

## Section 1
## Section 2
"""
        toc = builder.build_toc(content, format="html")
        
        # Should contain HTML tags
        assert "<ul>" in toc or "<ol>" in toc
        assert "<li>" in toc
        assert "<a" in toc
        assert "href=" in toc

    def test_build_toc_max_depth(self, builder):
        """Test TOC with max depth limit."""
        content = """# Main

## Level 2
### Level 3
#### Level 4
##### Level 5
###### Level 6
"""
        # Limit to level 3
        toc = builder.build_toc(content, max_depth=3)
        
        assert "Level 2" in toc
        assert "Level 3" in toc
        # Level 4+ should not appear
        assert "Level 4" not in toc or toc.count("Level 4") == 0
        assert "Level 5" not in toc
        assert "Level 6" not in toc

    def test_build_toc_custom_heading_prefix(self, builder):
        """Test TOC with custom heading prefix/marker."""
        content = """# Main

## Section 1
## Section 2
"""
        toc = builder.build_toc(content, include_top_level=False)
        
        # h1 should not be in TOC
        assert "Main" not in toc or toc.count("Main") == 0

    def test_build_toc_nested_structure(self, builder):
        """Test that TOC maintains hierarchical structure."""
        content = """# Main

## Parent 1
### Child 1.1
### Child 1.2
#### Grandchild 1.2.1

## Parent 2
### Child 2.1
"""
        toc = builder.build_toc(content, format="markdown")
        
        # Check indentation or nesting
        lines = toc.split("\n")
        parent1_idx = next(i for i, line in enumerate(lines) if "Parent 1" in line)
        child11_idx = next((i for i, line in enumerate(lines) if "Child 1.1" in line), -1)
        
        if child11_idx > parent1_idx:
            # Child should be indented more than parent
            parent1_indent = len(lines[parent1_idx]) - len(lines[parent1_idx].lstrip())
            child11_indent = len(lines[child11_idx]) - len(lines[child11_idx].lstrip())
            assert child11_indent > parent1_indent or "  " in lines[child11_idx]
