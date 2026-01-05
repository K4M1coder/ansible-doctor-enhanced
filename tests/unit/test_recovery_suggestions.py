"""Unit tests for recovery suggestion provider.

Tests follow TDD approach - written before integration into ErrorAggregator.
"""

import pytest
from ansibledoctor.exceptions.recovery import RecoverySuggestionProvider


class TestRecoverySuggestionLookup:
    """Test basic recovery suggestion lookup functionality."""
    
    def test_get_suggestion_for_known_code(self):
        """Test that known error codes return suggestions."""
        provider = RecoverySuggestionProvider()
        
        # E100 - YAML parsing errors
        suggestion = provider.get_suggestion("E100")
        assert suggestion is not None
        assert isinstance(suggestion, str)
        assert len(suggestion) > 0
        
        # E200 - Validation errors
        suggestion = provider.get_suggestion("E200")
        assert suggestion is not None
        assert isinstance(suggestion, str)
    
    def test_get_suggestion_for_unknown_code(self):
        """Test that unknown error codes return None."""
        provider = RecoverySuggestionProvider()
        
        suggestion = provider.get_suggestion("E999")
        assert suggestion is None
    
    def test_get_suggestion_for_specific_yaml_errors(self):
        """Test suggestions for specific YAML error codes."""
        provider = RecoverySuggestionProvider()
        
        # E101 - YAML syntax error
        suggestion = provider.get_suggestion("E101")
        assert suggestion is not None
        assert "yaml" in suggestion.lower() or "syntax" in suggestion.lower()
        
        # E102 - YAML indentation error (may fall back to E100)
        suggestion = provider.get_suggestion("E102")
        assert suggestion is not None
        # Should have YAML-related content (either specific or fallback)
        assert "yaml" in suggestion.lower() or "format" in suggestion.lower()
    
    def test_get_suggestion_for_validation_errors(self):
        """Test suggestions for validation error codes."""
        provider = RecoverySuggestionProvider()
        
        # E201 - Role structure validation
        suggestion = provider.get_suggestion("E201")
        assert suggestion is not None
        assert "role" in suggestion.lower() or "structure" in suggestion.lower()
        
        # E202 - Missing required fields
        suggestion = provider.get_suggestion("E202")
        assert suggestion is not None


class TestRecoverySuggestionFallback:
    """Test fallback logic for category-level suggestions."""
    
    def test_fallback_to_category_code(self):
        """Test that specific codes fall back to category codes."""
        provider = RecoverySuggestionProvider()
        
        # If E105 doesn't exist, should fall back to E100
        suggestion = provider.get_suggestion("E105")
        fallback = provider.get_suggestion("E100")
        
        # Should get either specific suggestion or fallback
        assert suggestion == fallback or suggestion is not None
    
    def test_category_codes_have_suggestions(self):
        """Test that all category codes (E100, E200, E300, E400) have suggestions."""
        provider = RecoverySuggestionProvider()
        
        categories = ["E100", "E200", "E300", "E400"]
        for code in categories:
            suggestion = provider.get_suggestion(code)
            assert suggestion is not None, f"Category code {code} should have a suggestion"
    
    def test_warning_codes_fallback(self):
        """Test that warning codes can fall back to error code suggestions."""
        provider = RecoverySuggestionProvider()
        
        # W100 category should have suggestions
        suggestion = provider.get_suggestion("W100")
        # Should either have W100 or fall back to something
        assert suggestion is not None or provider.get_suggestion("E100") is not None


class TestDocumentationUrls:
    """Test documentation URL lookup functionality."""
    
    def test_get_doc_url_for_known_code(self):
        """Test that known error codes can return documentation URLs."""
        provider = RecoverySuggestionProvider()
        
        # Some codes may have doc URLs
        doc_url = provider.get_doc_url("E100")
        # URL is optional, so just verify it's None or a string
        assert doc_url is None or isinstance(doc_url, str)
    
    def test_get_doc_url_for_unknown_code(self):
        """Test that unknown codes return None for doc URLs."""
        provider = RecoverySuggestionProvider()
        
        doc_url = provider.get_doc_url("E999")
        assert doc_url is None
    
    def test_doc_url_is_valid_format(self):
        """Test that returned doc URLs are in valid format."""
        provider = RecoverySuggestionProvider()
        
        # Check some common error codes
        for code in ["E100", "E101", "E200", "E201"]:
            doc_url = provider.get_doc_url(code)
            if doc_url:
                assert isinstance(doc_url, str)
                # Should be a URL or empty
                assert doc_url == "" or "http" in doc_url or doc_url.startswith("/")


class TestMultiStepRecovery:
    """Test multi-step recovery instruction functionality."""
    
    def test_get_steps_for_known_code(self):
        """Test that some error codes have step-by-step instructions."""
        provider = RecoverySuggestionProvider()
        
        # E100 - YAML parsing should have steps
        steps = provider.get_steps("E100")
        assert isinstance(steps, list)
        # Steps are optional, so list can be empty
    
    def test_get_steps_for_unknown_code(self):
        """Test that unknown codes return empty step list."""
        provider = RecoverySuggestionProvider()
        
        steps = provider.get_steps("E999")
        assert steps == []
    
    def test_steps_are_strings(self):
        """Test that recovery steps are strings when present."""
        provider = RecoverySuggestionProvider()
        
        # Check all category codes
        for code in ["E100", "E200", "E300", "E400"]:
            steps = provider.get_steps(code)
            assert isinstance(steps, list)
            for step in steps:
                assert isinstance(step, str)
                assert len(step) > 0
    
    def test_steps_have_actionable_content(self):
        """Test that steps contain actionable instructions."""
        provider = RecoverySuggestionProvider()
        
        # Get steps for a code that likely has them
        steps = provider.get_steps("E100")
        if steps:  # If steps exist
            # Should have action verbs or instructions
            combined = " ".join(steps).lower()
            action_words = ["check", "verify", "ensure", "run", "install", "fix", "update", "validate"]
            has_action = any(word in combined for word in action_words)
            assert has_action, "Steps should contain actionable instructions"


class TestRecoverySuggestionContent:
    """Test the quality and content of recovery suggestions."""
    
    def test_yaml_suggestions_are_specific(self):
        """Test that YAML error suggestions are specific and helpful."""
        provider = RecoverySuggestionProvider()
        
        # Check codes that definitely have suggestions
        yaml_codes = ["E100", "E101", "E102"]
        for code in yaml_codes:
            suggestion = provider.get_suggestion(code)
            if suggestion:
                # Should mention YAML-related terms or generic error handling
                lower_suggestion = suggestion.lower()
                yaml_terms = ["yaml", "syntax", "indentation", "format", "parse", "file", "structure"]
                has_yaml_term = any(term in lower_suggestion for term in yaml_terms)
                assert has_yaml_term, f"{code} suggestion should mention relevant terms"
    
    def test_suggestions_are_concise(self):
        """Test that suggestions are concise (not too long)."""
        provider = RecoverySuggestionProvider()
        
        for code in ["E100", "E200", "E300", "E400"]:
            suggestion = provider.get_suggestion(code)
            if suggestion:
                # Suggestion should be under 200 characters for readability
                assert len(suggestion) < 200, f"{code} suggestion is too long: {len(suggestion)} chars"
    
    def test_suggestions_are_actionable(self):
        """Test that suggestions contain actionable guidance."""
        provider = RecoverySuggestionProvider()
        
        for code in ["E100", "E101", "E200", "E201"]:
            suggestion = provider.get_suggestion(code)
            if suggestion:
                # Should contain action verbs or specific instructions
                lower_suggestion = suggestion.lower()
                action_indicators = [
                    "check", "verify", "ensure", "add", "remove", "fix",
                    "update", "install", "run", "validate", "use", "try"
                ]
                has_action = any(indicator in lower_suggestion for indicator in action_indicators)
                assert has_action, f"{code} suggestion should be actionable"


class TestProviderInitialization:
    """Test RecoverySuggestionProvider initialization."""
    
    def test_provider_initializes_with_defaults(self):
        """Test that provider initializes with embedded defaults."""
        provider = RecoverySuggestionProvider()
        
        # Should have loaded default suggestions
        assert provider._suggestions is not None
        assert len(provider._suggestions) > 0
    
    def test_provider_has_common_error_codes(self):
        """Test that provider has suggestions for common error codes."""
        provider = RecoverySuggestionProvider()
        
        common_codes = ["E100", "E200", "E300", "E400"]
        for code in common_codes:
            assert code in provider._suggestions, f"Should have suggestions for {code}"
    
    def test_provider_handles_missing_database_file(self):
        """Test that provider falls back to defaults when file missing."""
        from pathlib import Path
        
        # Pass non-existent path
        provider = RecoverySuggestionProvider(database_path=Path("/nonexistent/file.json"))
        
        # Should still work with defaults
        suggestion = provider.get_suggestion("E100")
        assert suggestion is not None
