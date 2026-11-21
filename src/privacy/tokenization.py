"""
RINGTRACE AI - Cryptographic Tokenization Module.
Implements secure pseudonymization of canonical entity identifiers using HMAC-SHA256
with salted key derivation to protect customer privacy before cross-bank computation.
"""

import hmac
import hashlib
from typing import List, Dict
import config


class CanonicalTokenizer:
    """Provides cryptographic pseudonymization for canonical entity IDs."""

    def __init__(self, salt: str = config.PSI_SHARED_SALT):
        self.salt = salt.encode("utf-8")

    def tokenize(self, canonical_id: str) -> str:
        """
        Generates a deterministic, salted cryptographic pseudonym for a canonical entity ID.
        Ensures raw entity IDs (e.g. PAN / National Tax IDs) are never transmitted in plaintext.
        """
        canonical_bytes = canonical_id.strip().encode("utf-8")
        h = hmac.new(self.salt, canonical_bytes, hashlib.sha256)
        return h.hexdigest()

    def tokenize_account_list(self, accounts: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Tokenizes canonical identifiers for a list of account records."""
        tokenized = []
        for acc in accounts:
            raw_cid = acc.get("canonical_entity_id", "")
            tok = self.tokenize(raw_cid)
            item = acc.copy()
            item["tokenized_id"] = tok
            tokenized.append(item)
        return tokenized
