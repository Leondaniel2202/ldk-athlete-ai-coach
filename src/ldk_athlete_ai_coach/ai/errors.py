"""Explicit AI integration errors."""

from __future__ import annotations


class AIConfigurationError(RuntimeError):
    """Raised when AI integration is not configured or unavailable."""


class AIProviderError(RuntimeError):
    """Raised when the AI provider call fails or returns invalid output."""
