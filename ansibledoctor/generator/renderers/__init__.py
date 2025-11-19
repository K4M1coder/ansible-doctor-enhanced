"""Renderers package for different output formats."""
from ansibledoctor.generator.renderers.html import HtmlRenderer
from ansibledoctor.generator.renderers.markdown import MarkdownRenderer

__all__ = ["HtmlRenderer", "MarkdownRenderer"]
