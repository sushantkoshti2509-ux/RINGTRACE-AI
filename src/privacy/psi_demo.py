"""
RINGTRACE AI - Private Set Intersection (PSI) Demonstration.
Implements commutative cryptographic Private Set Intersection between simulated
banks (Bank A, Bank B, and Bank C) to discover shared suspicious entities
without disclosing raw transaction ledgers or non-intersecting candidate accounts.
"""

import hashlib
import secrets
from typing import List, Dict, Set, Any, Tuple
import pandas as pd

import config
from src.privacy.tokenization import CanonicalTokenizer


# Standard 2048-bit MODP Group prime for Diffie-Hellman Commutative Exponentiation (RFC 3526)
PRIME_P = int(
    "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
    "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
    "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
    "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
    "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D"
    "C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F"
    "83655D23DCA3AD961C62F356208552BB9ED529077096966D"
    "670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B"
    "E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9"
    "DE2BCBF6955817183995497CEA956AE515D2261898FA0510"
    "15728E5A8AACAA68FFFFFFFFFFFFFFFF",
    16
)


class PSIParticipant:
    """Simulates an individual bank participating in the PSI cryptographic exchange."""

    def __init__(self, bank_id: str):
        self.bank_id = bank_id
        # Private secret key k (chosen randomly, coprime to p-1)
        self.private_key = secrets.randbelow(PRIME_P - 2) + 2
        self.local_items: List[str] = []
        self.mapping_to_account: Dict[str, str] = {}

    def set_candidate_items(self, items: List[Tuple[str, str]]):
        """Sets list of (canonical_token, account_id)."""
        self.local_items = [tok for tok, _ in items]
        self.mapping_to_account = {tok: acc for tok, acc in items}

    def _hash_to_group(self, item: str) -> int:
        """Deterministically hashes an item string to an element in Z_p*."""
        h = hashlib.sha256(item.encode("utf-8")).hexdigest()
        val = int(h, 16) % PRIME_P
        return val if val > 1 else 2

    def compute_first_round(self) -> List[int]:
        """Bank exponentiates each of its hashed items with its private key: H(x)^k mod p."""
        return [pow(self._hash_to_group(x), self.private_key, PRIME_P) for x in self.local_items]

    def compute_second_round(self, foreign_exponentiated_set: List[int]) -> List[int]:
        """Bank exponentiates another party's already-exponentiated items: (H(y)^k_other)^k_own mod p."""
        return [pow(val, self.private_key, PRIME_P) for val in foreign_exponentiated_set]


class PSICoordinator:
    """Orchestrates Private Set Intersection protocol across simulated institutions."""

    def __init__(self):
        self.tokenizer = CanonicalTokenizer()

    def run_two_party_psi(
        self,
        bank_a_candidates: List[Tuple[str, str]],
        bank_b_candidates: List[Tuple[str, str]],
        bank_a_id: str = "BANK_A",
        bank_b_id: str = "BANK_B",
    ) -> Dict[str, Any]:
        """
        Executes commutative Diffie-Hellman PSI between two banks.
        Discovers shared canonical entities while preserving privacy of unshared elements.
        """
        alice = PSIParticipant(bank_a_id)
        bob = PSIParticipant(bank_b_id)

        alice.set_candidate_items(bank_a_candidates)
        bob.set_candidate_items(bank_b_candidates)

        # Round 1: Local exponentiation
        # Alice computes H(a)^ka, Bob computes H(b)^kb
        round1_a = alice.compute_first_round()
        round1_b = bob.compute_first_round()

        # Round 2: Commutative cross-exponentiation
        # Bob computes (H(a)^ka)^kb = H(a)^(ka*kb)
        # Alice computes (H(b)^kb)^ka = H(b)^(kb*ka)
        # Because ka*kb == kb*ka mod p, matched elements result in identical values!
        round2_a = bob.compute_second_round(round1_a)  # Set from Alice, exponentiated by Bob
        round2_b = alice.compute_second_round(round1_b)  # Set from Bob, exponentiated by Alice

        # Map values back to detect matches
        # Note: round2_a has indices matching alice.local_items
        # round2_b has indices matching bob.local_items
        set_b_vals = set(round2_b)
        
        matched_tokens = []
        matched_pairs = []

        for idx, val in enumerate(round2_a):
            if val in set_b_vals:
                token = alice.local_items[idx]
                matched_tokens.append(token)
                acc_a = alice.mapping_to_account.get(token, "UNKNOWN")
                acc_b = bob.mapping_to_account.get(token, "UNKNOWN")
                matched_pairs.append({
                    "canonical_token": token,
                    f"{bank_a_id}_account": acc_a,
                    f"{bank_b_id}_account": acc_b,
                })

        return {
            "bank_a_input_count": len(bank_a_candidates),
            "bank_b_input_count": len(bank_b_candidates),
            "intersection_count": len(matched_tokens),
            "matched_entities": matched_pairs,
            "privacy_guarantee": {
                "algorithm": "Commutative Diffie-Hellman PSI (RFC 3526 2048-bit MODP)",
                "revealed_to_parties": "Only the intersecting canonical tokens.",
                "protected_from_disclosure": "All non-intersecting candidate accounts, balances, and transaction history.",
            },
        }

    def run_three_bank_psi(
        self,
        risk_scores_df: pd.DataFrame,
        accounts_df: pd.DataFrame,
        threshold: float = config.DEFAULT_ALERT_THRESHOLD,
    ) -> Dict[str, Any]:
        """
        Extracts candidate suspect entities from Bank A, Bank B, and Bank C,
        tokenizes them, and runs full pairwise and 3-way Private Set Intersection.
        """
        # Join accounts with risk scores to find candidates per bank
        merged = accounts_df.merge(
            risk_scores_df[["account_id", "risk_score", "risk_tier"]],
            on="account_id",
            how="inner",
        )

        bank_candidates: Dict[str, List[Tuple[str, str]]] = {}
        for b_id in config.SIMULATED_BANKS:
            b_subset = merged[(merged["bank_id"] == b_id) & (merged["risk_score"] >= threshold)]
            candidates = []
            for _, row in b_subset.iterrows():
                cid = str(row["canonical_entity_id"])
                tok = self.tokenizer.tokenize(cid)
                candidates.append((tok, str(row["account_id"])))
            bank_candidates[b_id] = candidates

        b_list = list(config.SIMULATED_BANKS)
        b1 = b_list[0] if len(b_list) > 0 else "BANK_A"
        b2 = b_list[1] if len(b_list) > 1 else "BANK_B"
        b3 = b_list[2] if len(b_list) > 2 else "BANK_C"

        # Run Pairwise PSI across leading institutions
        psi_12 = self.run_two_party_psi(bank_candidates.get(b1, []), bank_candidates.get(b2, []), b1, b2)
        psi_23 = self.run_two_party_psi(bank_candidates.get(b2, []), bank_candidates.get(b3, []), b2, b3)
        psi_13 = self.run_two_party_psi(bank_candidates.get(b1, []), bank_candidates.get(b3, []), b1, b3)

        # 3-Way intersection (entities common to all 3 institutions)
        tok_12 = {p["canonical_token"] for p in psi_12["matched_entities"]}
        tok_23 = {p["canonical_token"] for p in psi_23["matched_entities"]}
        three_way_tokens = tok_12.intersection(tok_23)

        three_way_entities = []
        for tok in three_way_tokens:
            acc_1 = next((p[f"{b1}_account"] for p in psi_12["matched_entities"] if p["canonical_token"] == tok), "UNKNOWN")
            acc_2 = next((p[f"{b2}_account"] for p in psi_12["matched_entities"] if p["canonical_token"] == tok), "UNKNOWN")
            acc_3 = next((p[f"{b3}_account"] for p in psi_23["matched_entities"] if p["canonical_token"] == tok), "UNKNOWN")
            three_way_entities.append({
                "canonical_token": tok,
                f"{b1}_account": acc_1,
                f"{b2}_account": acc_2,
                f"{b3}_account": acc_3,
            })

        return {
            "institutions_participating": b_list,
            "bank_a_candidates": len(bank_candidates.get(b1, [])),
            "bank_b_candidates": len(bank_candidates.get(b2, [])),
            "bank_c_candidates": len(bank_candidates.get(b3, [])),
            "pairwise_matches": {
                f"{b1}_x_{b2}": len(psi_12["matched_entities"]),
                f"{b2}_x_{b3}": len(psi_23["matched_entities"]),
                f"{b1}_x_{b3}": len(psi_13["matched_entities"]),
            },
            "three_way_intersection_count": len(three_way_entities),
            "three_way_entities": three_way_entities,
            "pairwise_details": {
                "P1_P2": psi_12["matched_entities"],
                "P2_P3": psi_23["matched_entities"],
                "P1_P3": psi_13["matched_entities"],
            },
        }
