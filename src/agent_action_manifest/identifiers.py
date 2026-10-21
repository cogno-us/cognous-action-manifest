"""Exact-identifier predicate shared by the validator and the OpenAPPA helper.

Identities and targets are compared as exact strings and are never normalized.
A literal target such as ``*`` is an ordinary string, not a wildcard.
"""

from __future__ import annotations


def is_exact_identifier(value: object) -> bool:
    """Reject blank, whitespace-padded and control-character spellings."""
    return (isinstance(value, str) and bool(value) and value == value.strip()
            and not any(ord(char) < 32 or ord(char) == 127 for char in value))
