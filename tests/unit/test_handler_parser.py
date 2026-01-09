"""Unit tests for handler parser (Spec 001, User Story 5)."""

from ansibledoctor.parser.handler_parser import HandlerParser


class TestHandlerParser:
    """Test HandlerParser functionality."""

    def test_parse_handlers_main_yml(self, tmp_path):
        """T105: HandlerParser parses handlers/main.yml."""
        # Arrange
        handlers_dir = tmp_path / "handlers"
        handlers_dir.mkdir()
        handlers_file = handlers_dir / "main.yml"
        handlers_file.write_text(
            """---
- name: restart apache
  service:
    name: apache2
    state: restarted

- name: reload nginx
  service:
    name: nginx
    state: reloaded
  tags: [web, reload]
"""
        )

        # Act
        parser = HandlerParser(str(tmp_path))
        handlers = parser.parse()

        # Assert
        assert len(handlers) == 2
        assert handlers[0].name == "restart apache"
        assert handlers[1].name == "reload nginx"

    def test_extract_handler_name_tags_listen(self, tmp_path):
        """T106: HandlerParser extracts handler name, tags, listen directive."""
        # Arrange
        handlers_dir = tmp_path / "handlers"
        handlers_dir.mkdir()
        handlers_file = handlers_dir / "main.yml"
        handlers_file.write_text(
            """---
- name: restart service
  service:
    name: myservice
    state: restarted
  listen: "restart myservice"
  tags: [critical, restart]
"""
        )

        # Act
        parser = HandlerParser(str(tmp_path))
        handlers = parser.parse()

        # Assert
        assert len(handlers) == 1
        handler = handlers[0]
        assert handler.name == "restart service"
        assert handler.listen == "restart myservice"
        assert "critical" in handler.tags
        assert "restart" in handler.tags

    def test_follow_includes_in_handlers(self, tmp_path):
        """T107: HandlerParser follows includes (include_tasks in handlers)."""
        # Arrange
        handlers_dir = tmp_path / "handlers"
        handlers_dir.mkdir()

        # Main handlers file with include
        main_file = handlers_dir / "main.yml"
        main_file.write_text(
            """---
- name: main handler
  debug:
    msg: "main"

- include_tasks: web.yml
"""
        )

        # Included file
        web_file = handlers_dir / "web.yml"
        web_file.write_text(
            """---
- name: included handler
  debug:
    msg: "included"
"""
        )

        # Act
        parser = HandlerParser(str(tmp_path))
        handlers = parser.parse()

        # Assert
        assert len(handlers) == 2
        assert handlers[0].name == "main handler"
        assert handlers[1].name == "included handler"

    def test_handler_with_no_tags(self, tmp_path):
        """Test handler without tags returns empty tags list."""
        # Arrange
        handlers_dir = tmp_path / "handlers"
        handlers_dir.mkdir()
        handlers_file = handlers_dir / "main.yml"
        handlers_file.write_text(
            """---
- name: simple handler
  debug:
    msg: "no tags"
"""
        )

        # Act
        parser = HandlerParser(str(tmp_path))
        handlers = parser.parse()

        # Assert
        assert len(handlers) == 1
        assert handlers[0].tags == []

    def test_no_handlers_directory_returns_empty(self, tmp_path):
        """Test role without handlers/ directory returns empty list."""
        # Act
        parser = HandlerParser(str(tmp_path))
        handlers = parser.parse()

        # Assert
        assert handlers == []

    def test_empty_handlers_file_returns_empty(self, tmp_path):
        """Test empty handlers/main.yml returns empty list."""
        # Arrange
        handlers_dir = tmp_path / "handlers"
        handlers_dir.mkdir()
        handlers_file = handlers_dir / "main.yml"
        handlers_file.write_text("---\n")

        # Act
        parser = HandlerParser(str(tmp_path))
        handlers = parser.parse()

        # Assert
        assert handlers == []
