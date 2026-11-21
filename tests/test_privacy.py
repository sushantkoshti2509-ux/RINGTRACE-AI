"""
Unit tests for Cryptographic Tokenization and Commutative Diffie-Hellman PSI Protocol.
"""

import pytest
from src.privacy.tokenization import CanonicalTokenizer
from src.privacy.psi_demo import PSICoordinator, PSIParticipant, PRIME_P


def test_canonical_tokenizer():
    tokenizer = CanonicalTokenizer(salt="TEST_SALT_123")
    tok1 = tokenizer.tokenize("PAN_ABCDE1234F")
    tok2 = tokenizer.tokenize("PAN_ABCDE1234F")
    tok3 = tokenizer.tokenize("PAN_DIFFERENT999")

    # Deterministic output
    assert tok1 == tok2
    # Distinct output for different inputs
    assert tok1 != tok3
    # SHA-256 hex length
    assert len(tok1) == 64


def test_commutative_psi_two_party():
    coordinator = PSICoordinator()

    # Bank A has {Alice, Bob, Charlie}
    bank_a_candidates = [
        ("TOKEN_ALICE", "ACC_A_001"),
        ("TOKEN_BOB", "ACC_A_002"),
        ("TOKEN_CHARLIE", "ACC_A_003"),
    ]

    # Bank B has {Bob, Charlie, David}
    bank_b_candidates = [
        ("TOKEN_BOB", "ACC_B_101"),
        ("TOKEN_CHARLIE", "ACC_B_102"),
        ("TOKEN_DAVID", "ACC_B_103"),
    ]

    result = coordinator.run_two_party_psi(
        bank_a_candidates, bank_b_candidates, bank_a_id="BANK_A", bank_b_id="BANK_B"
    )

    # Intersection must be Bob and Charlie (2 elements)
    assert result["intersection_count"] == 2
    matched_tokens = {m["canonical_token"] for m in result["matched_entities"]}
    assert matched_tokens == {"TOKEN_BOB", "TOKEN_CHARLIE"}
    assert "TOKEN_ALICE" not in matched_tokens
    assert "TOKEN_DAVID" not in matched_tokens


def test_commutative_math_property():
    # Verify ka * kb mod p property
    p1 = PSIParticipant("P1")
    p2 = PSIParticipant("P2")

    test_val = 12345678901234567890
    # P1 first, then P2
    step1_a = pow(test_val, p1.private_key, PRIME_P)
    final_a = pow(step1_a, p2.private_key, PRIME_P)

    # P2 first, then P1
    step1_b = pow(test_val, p2.private_key, PRIME_P)
    final_b = pow(step1_b, p1.private_key, PRIME_P)

    assert final_a == final_b
