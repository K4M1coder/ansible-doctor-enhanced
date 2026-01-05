"""Unit tests for ErrorAggregator."""

from ansibledoctor.exceptions.aggregator import ErrorAggregator


class TestErrorAggregatorAddError:
    """Test ErrorAggregator.add_error() method."""

    def test_add_single_error(self):
        """Test adding a single error."""
        aggregator = ErrorAggregator()

        aggregator.add_error(
            code="E101",
            message="YAML syntax error",
            file_path="roles/web/tasks/main.yml",
            line=15,
            column=3,
        )

        assert aggregator.has_errors()
        assert aggregator._error_count == 1
        assert len(aggregator.errors) == 1
        assert aggregator.errors[0].code == "E101"
        assert aggregator.errors[0].message == "YAML syntax error"
        assert aggregator.errors[0].file_path == "roles/web/tasks/main.yml"
        assert aggregator.errors[0].line == 15
        assert aggregator.errors[0].column == 3

    def test_add_multiple_errors(self):
        """Test adding multiple different errors."""
        aggregator = ErrorAggregator()

        aggregator.add_error(code="E101", message="Error 1")
        aggregator.add_error(code="E102", message="Error 2")
        aggregator.add_error(code="E201", message="Error 3")

        assert aggregator._error_count == 3
        assert len(aggregator.errors) == 3

    def test_deduplicate_identical_errors(self):
        """Test that identical errors are deduplicated."""
        aggregator = ErrorAggregator()

        # Add same error twice
        aggregator.add_error(
            code="E101",
            message="YAML syntax error",
            file_path="roles/web/tasks/main.yml",
            line=15,
        )
        aggregator.add_error(
            code="E101",
            message="YAML syntax error",
            file_path="roles/web/tasks/main.yml",
            line=15,
        )

        # Should only store once
        assert aggregator._error_count == 1
        assert len(aggregator.errors) == 1

    def test_different_lines_not_deduplicated(self):
        """Test that errors on different lines are not deduplicated."""
        aggregator = ErrorAggregator()

        aggregator.add_error(
            code="E101",
            message="YAML syntax error",
            file_path="roles/web/tasks/main.yml",
            line=15,
        )
        aggregator.add_error(
            code="E101",
            message="YAML syntax error",
            file_path="roles/web/tasks/main.yml",
            line=20,
        )

        assert aggregator._error_count == 2
        assert len(aggregator.errors) == 2


class TestErrorAggregatorMemoryBounds:
    """Test ErrorAggregator memory bounds (max 1000 errors)."""

    def test_cap_at_max_errors(self):
        """Test that error collection is capped at max_errors."""
        aggregator = ErrorAggregator(max_errors=10)

        # Add 15 errors (line numbers start at 1)
        for i in range(1, 16):
            aggregator.add_error(
                code="E101",
                message=f"Error {i}",
                line=i,  # Different lines to avoid deduplication
            )

        # Should cap at 10
        assert aggregator._error_count == 15  # Counter tracks all
        assert len(aggregator.errors) == 10  # Storage is capped
        assert aggregator._max_errors_reached

    def test_max_errors_flag_not_set_under_limit(self):
        """Test that max_errors_reached flag is not set when under limit."""
        aggregator = ErrorAggregator(max_errors=100)

        # Add 50 errors (line numbers start at 1)
        for i in range(1, 51):
            aggregator.add_error(code="E101", message=f"Error {i}", line=i)

        assert not aggregator._max_errors_reached
        assert aggregator._error_count == 50
        assert len(aggregator.errors) == 50


class TestErrorAggregatorWarnings:
    """Test ErrorAggregator warning handling."""

    def test_add_warning(self):
        """Test adding warnings."""
        aggregator = ErrorAggregator()

        aggregator.add_warning(
            code="W103",
            message="Undocumented variable",
            file_path="roles/web/defaults/main.yml",
            line=5,
        )

        assert aggregator.has_warnings()
        assert aggregator._warning_count == 1
        assert len(aggregator.warnings) == 1
        assert aggregator.warnings[0].code == "W103"
        assert aggregator.warnings[0].severity == "warning"

    def test_warnings_separate_from_errors(self):
        """Test that warnings and errors are tracked separately."""
        aggregator = ErrorAggregator()

        aggregator.add_error(code="E101", message="Error")
        aggregator.add_warning(code="W103", message="Warning")

        assert aggregator._error_count == 1
        assert aggregator._warning_count == 1
        assert len(aggregator.errors) == 1
        assert len(aggregator.warnings) == 1

    def test_add_warning_converts_error_code(self):
        """Test that add_warning converts E codes to W codes."""
        aggregator = ErrorAggregator()

        aggregator.add_warning(code="E103", message="Should become W103")

        assert aggregator.warnings[0].code == "W103"


class TestErrorAggregatorReporting:
    """Test ErrorAggregator report generation."""

    def test_get_report(self):
        """Test generating error report."""
        aggregator = ErrorAggregator()

        aggregator.add_error(code="E101", message="Error 1")
        aggregator.add_warning(code="W103", message="Warning 1")

        report = aggregator.get_report(correlation_id="test-123")

        assert report.correlation_id == "test-123"
        assert report.error_count == 1
        assert report.warning_count == 1
        assert len(report.errors) == 1
        assert len(report.warnings) == 1
        assert not report.partial_success

    def test_get_report_with_partial_success(self):
        """Test report with partial_success flag."""
        aggregator = ErrorAggregator()

        aggregator.add_error(code="E101", message="Error")

        report = aggregator.get_report(correlation_id="test-123", partial_success=True)

        assert report.partial_success

    def test_get_errors_by_file(self):
        """Test grouping errors by file."""
        aggregator = ErrorAggregator()

        aggregator.add_error(code="E101", message="Error 1", file_path="file1.yml")
        aggregator.add_error(code="E102", message="Error 2", file_path="file1.yml")
        aggregator.add_error(code="E101", message="Error 3", file_path="file2.yml")

        grouped = aggregator.get_errors_by_file()

        assert len(grouped) == 2
        assert "file1.yml" in grouped
        assert "file2.yml" in grouped
        assert len(grouped["file1.yml"]) == 2
        assert len(grouped["file2.yml"]) == 1

    def test_clear(self):
        """Test clearing aggregator."""
        aggregator = ErrorAggregator()

        aggregator.add_error(code="E101", message="Error")
        aggregator.add_warning(code="W103", message="Warning")

        assert aggregator.has_errors()
        assert aggregator.has_warnings()

        aggregator.clear()

        assert not aggregator.has_errors()
        assert not aggregator.has_warnings()
        assert aggregator._error_count == 0
        assert aggregator._warning_count == 0
        assert len(aggregator.errors) == 0
        assert len(aggregator.warnings) == 0


class TestErrorAggregatorRecoverySuggestions:
    """Test automatic recovery suggestion integration."""

    def test_auto_fetches_recovery_suggestion(self):
        """Should automatically fetch recovery suggestion when not provided."""
        aggregator = ErrorAggregator()

        # Add error without recovery suggestion - should auto-fetch
        aggregator.add_error("E101", "YAML syntax error", file_path="test.yml")

        report = aggregator.get_report(correlation_id="test-auto-fetch")
        assert len(report.errors) == 1
        entry = report.errors[0]

        # Verify recovery suggestion was auto-fetched
        assert entry.recovery_suggestion is not None
        assert len(entry.recovery_suggestion) > 0
        assert (
            "yaml" in entry.recovery_suggestion.lower()
            or "syntax" in entry.recovery_suggestion.lower()
        )

        # Verify doc URL was also auto-fetched
        assert entry.doc_url is not None
        assert entry.doc_url.startswith("https://")

    def test_respects_provided_recovery_suggestion(self):
        """Should use provided recovery suggestion instead of auto-fetching."""
        aggregator = ErrorAggregator()
        custom_suggestion = "Custom fix for this specific error"

        aggregator.add_error("E101", "YAML syntax error", recovery_suggestion=custom_suggestion)

        report = aggregator.get_report(correlation_id="test-custom")
        entry = report.errors[0]

        # Should use custom suggestion, not auto-fetched one
        assert entry.recovery_suggestion == custom_suggestion

    def test_auto_fetches_for_multiple_errors(self):
        """Should auto-fetch suggestions for multiple errors."""
        aggregator = ErrorAggregator()

        aggregator.add_error("E101", "YAML error")
        aggregator.add_error("E201", "Missing meta")
        aggregator.add_error("E301", "Role dependency issue")

        report = aggregator.get_report(correlation_id="test-multi")

        # All should have auto-fetched suggestions
        for entry in report.errors:
            assert entry.recovery_suggestion is not None
            assert len(entry.recovery_suggestion) > 0


class TestErrorAggregatorFileTracking:
    """Test file processing tracking for partial success (Phase 5 - T046)."""

    def test_track_file_processing(self):
        """Should track total, successful, and failed file counts."""
        aggregator = ErrorAggregator()

        # Mark files being processed
        aggregator.mark_file_start("file1.yml")
        aggregator.mark_file_start("file2.yml")
        aggregator.mark_file_start("file3.yml")

        # Mark outcomes
        aggregator.mark_file_success("file1.yml")
        aggregator.mark_file_failure("file2.yml")
        aggregator.mark_file_success("file3.yml")

        report = aggregator.get_report(correlation_id="test-file-tracking")

        assert report.total_files == 3
        assert report.successful_files == 2
        assert report.failed_files == 1

    def test_mark_file_success_implies_start(self):
        """Marking success should automatically count as start."""
        aggregator = ErrorAggregator()

        # Directly mark as success without calling mark_file_start
        aggregator.mark_file_success("file1.yml")

        report = aggregator.get_report(correlation_id="test-implicit-start")

        assert report.total_files == 1
        assert report.successful_files == 1

    def test_mark_file_failure_implies_start(self):
        """Marking failure should automatically count as start."""
        aggregator = ErrorAggregator()

        # Directly mark as failure without calling mark_file_start
        aggregator.mark_file_failure("file1.yml")

        report = aggregator.get_report(correlation_id="test-implicit-start-fail")

        assert report.total_files == 1
        assert report.failed_files == 1

    def test_duplicate_file_start_only_counted_once(self):
        """Same file marked multiple times should only count once."""
        aggregator = ErrorAggregator()

        # Mark same file multiple times
        aggregator.mark_file_start("file1.yml")
        aggregator.mark_file_start("file1.yml")
        aggregator.mark_file_start("file1.yml")

        report = aggregator.get_report(correlation_id="test-dedupe")

        assert report.total_files == 1

    def test_file_tracking_in_text_output(self):
        """File counts should appear in text output (T048)."""
        aggregator = ErrorAggregator()

        aggregator.mark_file_start("file1.yml")
        aggregator.mark_file_start("file2.yml")
        aggregator.mark_file_start("file3.yml")
        aggregator.mark_file_success("file1.yml")
        aggregator.mark_file_failure("file2.yml")
        aggregator.mark_file_success("file3.yml")

        report = aggregator.get_report(correlation_id="test-text-output", partial_success=True)
        text = report.to_text()

        # Should include file count in output
        assert "Files Processed: 2 of 3 successful" in text

    def test_clear_resets_file_tracking(self):
        """Clearing aggregator should reset file counts."""
        aggregator = ErrorAggregator()

        aggregator.mark_file_success("file1.yml")
        aggregator.mark_file_failure("file2.yml")

        aggregator.clear()

        report = aggregator.get_report(correlation_id="test-clear")

        assert report.total_files == 0
        assert report.successful_files == 0
        assert report.failed_files == 0


class TestErrorSorting:
    """Test error sorting by file path and line number (T063 - Phase 7)."""

    def test_errors_sorted_by_file_path(self):
        """Test that errors are sorted by file path alphabetically."""
        aggregator = ErrorAggregator()

        # Add errors in random file order
        aggregator.add_error(
            code="E101", message="Error in main", file_path="roles/web/tasks/main.yml", line=10
        )
        aggregator.add_error(
            code="E102",
            message="Error in handlers",
            file_path="roles/web/handlers/main.yml",
            line=5,
        )
        aggregator.add_error(
            code="E103",
            message="Error in defaults",
            file_path="roles/web/defaults/main.yml",
            line=1,
        )

        report = aggregator.get_report(correlation_id="test-sort")

        # Should be sorted: defaults < handlers < tasks
        assert report.errors[0].file_path == "roles/web/defaults/main.yml"
        assert report.errors[1].file_path == "roles/web/handlers/main.yml"
        assert report.errors[2].file_path == "roles/web/tasks/main.yml"

    def test_errors_sorted_by_line_within_same_file(self):
        """Test that errors in same file are sorted by line number."""
        aggregator = ErrorAggregator()

        # Add errors in same file, random line order
        aggregator.add_error(code="E101", message="Error at line 50", file_path="test.yml", line=50)
        aggregator.add_error(code="E102", message="Error at line 10", file_path="test.yml", line=10)
        aggregator.add_error(code="E103", message="Error at line 30", file_path="test.yml", line=30)

        report = aggregator.get_report(correlation_id="test-sort")

        # Should be sorted by line: 10 < 30 < 50
        assert report.errors[0].line == 10
        assert report.errors[1].line == 30
        assert report.errors[2].line == 50

    def test_errors_without_file_path_at_end(self):
        """Test that errors without file path are sorted to the end."""
        aggregator = ErrorAggregator()

        aggregator.add_error(code="E101", message="Error with file", file_path="test.yml", line=10)
        aggregator.add_error(code="E102", message="Error without file")
        aggregator.add_error(
            code="E103", message="Another with file", file_path="other.yml", line=5
        )

        report = aggregator.get_report(correlation_id="test-sort")

        # Errors with file paths should come first, sorted
        assert report.errors[0].file_path == "other.yml"
        assert report.errors[1].file_path == "test.yml"
        assert report.errors[2].file_path is None

    def test_errors_without_line_number_sorted_by_file_only(self):
        """Test that errors without line numbers are sorted by file path only."""
        aggregator = ErrorAggregator()

        aggregator.add_error(code="E101", message="With line", file_path="test.yml", line=20)
        aggregator.add_error(code="E102", message="Without line", file_path="test.yml")
        aggregator.add_error(
            code="E103", message="Another with line", file_path="test.yml", line=10
        )

        report = aggregator.get_report(correlation_id="test-sort")

        # All in same file, those with line numbers sorted first
        assert report.errors[0].line == 10
        assert report.errors[1].line == 20
        # Error without line number should be last
        assert report.errors[2].line is None

    def test_warnings_sorted_separately(self):
        """Test that warnings are sorted independently from errors."""
        aggregator = ErrorAggregator()

        # Add warnings in random order
        aggregator.add_warning(code="W101", message="Warning B", file_path="b.yml", line=10)
        aggregator.add_warning(code="W102", message="Warning A", file_path="a.yml", line=5)

        report = aggregator.get_report(correlation_id="test-sort")

        # Warnings should be sorted by file
        assert report.warnings[0].file_path == "a.yml"
        assert report.warnings[1].file_path == "b.yml"
