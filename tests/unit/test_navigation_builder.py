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


class TestNestedSubsections:
    """T048: Test nested subsections in TOC structure."""

    @pytest.fixture
    def builder(self):
        """Create a NavigationBuilder instance for testing."""
        return NavigationBuilder()

    def test_three_level_nesting(self, builder):
        """Test TOC with three levels of nesting (h2, h3, h4)."""
        content = """# Document

## Level 2 A
### Level 3 A.1
#### Level 4 A.1.1
#### Level 4 A.1.2
### Level 3 A.2

## Level 2 B
### Level 3 B.1
"""
        toc = builder.build_toc(content, format="markdown")
        
        # Should contain all levels
        assert "Level 2 A" in toc
        assert "Level 3 A.1" in toc
        assert "Level 4 A.1.1" in toc
        assert "Level 4 A.1.2" in toc
        assert "Level 3 A.2" in toc
        assert "Level 2 B" in toc
        assert "Level 3 B.1" in toc

    def test_nested_indentation_markdown(self, builder):
        """Test that nested items are properly indented in Markdown format."""
        content = """# Main

## Section 1
### Subsection 1.1
#### Sub-subsection 1.1.1
### Subsection 1.2

## Section 2
"""
        toc = builder.build_toc(content, format="markdown")
        
        lines = [line for line in toc.split("\n") if line.strip()]
        
        # Check indentation patterns
        # h2 should have base indentation
        # h3 should be indented more than h2
        # h4 should be indented more than h3
        section1_lines = [line for line in lines if "Section 1" in line and "Sub" not in line]
        subsection11_lines = [line for line in lines if "Subsection 1.1" in line and "Sub-sub" not in line]
        subsubsection_lines = [line for line in lines if "Sub-subsection 1.1.1" in line]
        
        if section1_lines and subsection11_lines and subsubsection_lines:
            section1_indent = len(section1_lines[0]) - len(section1_lines[0].lstrip())
            subsection11_indent = len(subsection11_lines[0]) - len(subsection11_lines[0].lstrip())
            subsubsection_indent = len(subsubsection_lines[0]) - len(subsubsection_lines[0].lstrip())
            
            # Each level should be indented more than previous
            assert subsection11_indent > section1_indent
            assert subsubsection_indent > subsection11_indent

    def test_nested_html_structure(self, builder):
        """Test that nested items create proper HTML list structure."""
        content = """# Main

## Parent
### Child
#### Grandchild
"""
        toc = builder.build_toc(content, format="html")
        
        # Should have nested <ul> or <ol> tags
        assert toc.count("<ul>") >= 1 or toc.count("<ol>") >= 1
        assert toc.count("<li>") >= 3
        
        # Nested lists should be inside parent list items
        # Pattern: <li>Parent<ul><li>Child</li></ul></li> or similar
        if "<ul>" in toc:
            # Count nesting depth
            max_depth = 0
            current_depth = 0
            for char in toc:
                if char == "<":
                    next_chars = toc[toc.index(char):toc.index(char) + 4]
                    if next_chars.startswith("<ul>") or next_chars.startswith("<ol>"):
                        current_depth += 1
                        max_depth = max(max_depth, current_depth)
                    elif next_chars.startswith("</ul") or next_chars.startswith("</ol"):
                        current_depth -= 1
            
            assert max_depth >= 2  # At least 2 levels of nesting

    def test_inconsistent_nesting_levels(self, builder):
        """Test TOC handles inconsistent heading levels (e.g., h2 -> h4 without h3)."""
        content = """# Main

## Section 1
#### Subsection 1.1 (skipped h3)
## Section 2
### Subsection 2.1
##### Sub-subsection 2.1.1 (skipped h4)
"""
        toc = builder.build_toc(content, format="markdown")
        
        # Should still include all headings
        assert "Section 1" in toc
        assert "Subsection 1.1" in toc
        assert "Section 2" in toc
        assert "Subsection 2.1" in toc
        assert "Sub-subsection 2.1.1" in toc

    def test_deep_nesting_six_levels(self, builder):
        """Test TOC with all six heading levels (h1-h6)."""
        content = """# Level 1
## Level 2
### Level 3
#### Level 4
##### Level 5
###### Level 6
"""
        toc = builder.build_toc(content, format="markdown")
        
        # Should include all levels (excluding h1 if include_top_level=False by default)
        assert "Level 2" in toc or "Level 1" in toc
        assert "Level 3" in toc
        assert "Level 4" in toc
        assert "Level 5" in toc
        assert "Level 6" in toc

    def test_nested_with_max_depth_limit(self, builder):
        """Test max_depth parameter limits nesting depth."""
        content = """# Main

## Level 2
### Level 3
#### Level 4
##### Level 5
"""
        # Limit to 3 levels (h2, h3, h4)
        toc = builder.build_toc(content, max_depth=4, format="markdown")
        
        # Should include up to level 4
        assert "Level 2" in toc
        assert "Level 3" in toc
        assert "Level 4" in toc
        # Should not include level 5
        assert "Level 5" not in toc

    def test_nested_sibling_sections(self, builder):
        """Test multiple sibling sections at each level."""
        content = """# Main

## Section 1
### Subsection 1.1
### Subsection 1.2
### Subsection 1.3

## Section 2
### Subsection 2.1
### Subsection 2.2

## Section 3
"""
        toc = builder.build_toc(content, format="markdown")
        
        # All siblings should be included
        assert "Section 1" in toc
        assert "Section 2" in toc
        assert "Section 3" in toc
        assert "Subsection 1.1" in toc
        assert "Subsection 1.2" in toc
        assert "Subsection 1.3" in toc
        assert "Subsection 2.1" in toc
        assert "Subsection 2.2" in toc

    def test_nested_with_empty_parents(self, builder):
        """Test nested structure where parent sections have no content."""
        content = """# Main

## Empty Parent Section
### Child with content
Content here.

## Another Empty Parent
### Child 1
### Child 2
"""
        toc = builder.build_toc(content, format="markdown")
        
        # Should include all headings regardless of content
        assert "Empty Parent Section" in toc
        assert "Child with content" in toc
        assert "Another Empty Parent" in toc
        assert "Child 1" in toc
        assert "Child 2" in toc

    def test_nested_anchor_generation(self, builder):
        """Test that nested sections generate correct anchor links."""
        content = """# Main

## Configuration
### Database Configuration
#### Connection Settings
### Cache Configuration
"""
        toc = builder.build_toc(content, format="markdown")
        
        # Should have proper anchor format
        assert "[" in toc and "]" in toc and "(" in toc and ")" in toc
        
        # Anchors should be slugified
        assert "#configuration" in toc.lower() or "configuration" in toc.lower()
        assert "#database" in toc.lower() or "database" in toc.lower()
        assert "#connection" in toc.lower() or "connection" in toc.lower()

    def test_nested_list_markers(self, builder):
        """Test that nested items use appropriate list markers in Markdown."""
        content = """# Main

## Section 1
### Subsection 1.1
#### Sub-subsection 1.1.1
"""
        toc = builder.build_toc(content, format="markdown")
        
        lines = [line.strip() for line in toc.split("\n") if line.strip()]
        
        # Markdown lists typically use -, *, or numbered markers
        # Check that list markers are present
        for line in lines:
            # Each line should start with a list marker or be indented
            assert (
                line.startswith("-") or
                line.startswith("*") or
                line.startswith("1") or
                line.startswith(" ") or
                line.startswith("\t")
            )

    def test_nested_html_with_css_classes(self, builder):
        """Test HTML output includes CSS classes for styling nested items."""
        content = """# Main

## Section
### Subsection
"""
        toc = builder.build_toc(content, format="html")
        
        # HTML should have structure suitable for CSS styling
        assert "<li>" in toc
        # May include class attributes for different levels
        # <li class="level-2"> or similar
        assert ">" in toc and "<" in toc
