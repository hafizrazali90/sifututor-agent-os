#!/usr/bin/env python3
"""Shared tokenizer for path and text keyword matching across signals.

Splits on path separators, punctuation, and whitespace, and also inserts a
boundary before an uppercase letter that follows a lowercase letter or
digit -- so a camelCase/PascalCase identifier such as
"InvoiceRefundService.php" tokenizes into its constituent words
("invoice", "refund", "service", "php") instead of one fused token that no
keyword list could ever match.
"""

from __future__ import annotations

import re

_CAMEL_BOUNDARY = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
_NON_WORD = re.compile(r"[^a-z0-9]+")


def tokens(text: str) -> set[str]:
    """Return the lowercase word-token set for one string (path or prose)."""
    segmented = _CAMEL_BOUNDARY.sub("_", text)
    return {token for token in _NON_WORD.split(segmented.lower()) if token}
