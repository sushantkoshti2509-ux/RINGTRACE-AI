# RINGTRACE AI — Security, Privacy, and Ethical AI Specification

## 1. Regulatory Context & Compliance Alignment
RINGTRACE AI is engineered in alignment with Indian data protection and cybersecurity mandates:
- **Digital Personal Data Protection Act, 2023 (DPDP Act):** Strict purpose limitation, data minimization, and protection against unauthorized identifier disclosure.
- **RBI Digital Payment Security Controls & Fraud Risk Management Directions:** Requirement for comprehensive fraud monitoring without violating customer financial confidentiality.

## 2. Privacy Architecture: Private Set Intersection (PSI)

### 2.1 The Challenge
When mule rings move money across multiple banks, each institution possesses only a fragmented glimpse of the total flow. Direct pooling of transaction ledgers is prohibited under banking secrecy and data privacy laws.

### 2.2 Commutative Diffie-Hellman Protocol
RINGTRACE AI employs a two-round commutative Diffie-Hellman Private Set Intersection protocol using the standard RFC 3526 2048-bit MODP group:
1. **Canonical Tokenization:** Canonical national IDs (such as PAN) are pre-hashed using HMAC-SHA256 with institutional salts:
   $$t = \text{HMAC}_{salt}(\text{CANONICAL\_ID})$$
2. **First Round Exponentiation:** Bank A generates private random key $k_A$ and sends $\{H(x)^{k_A} \pmod p\}$ to Bank B.
3. **Second Round Exponentiation:** Bank B applies its private key $k_B$ to the received set, yielding $\{H(x)^{k_A k_B} \pmod p\}$. Similarly, Bank A applies $k_A$ to Bank B's elements, yielding $\{H(y)^{k_B k_A} \pmod p\}$.
4. **Commutative Matching:** Because $k_A k_B \equiv k_B k_A \pmod p$, matching items produce identical group elements.

### 2.3 Mathematical Privacy Guarantees
- **Computational Hardness:** Decoupling or inverting group elements requires solving the Discrete Logarithm Problem (DLP) in a 2048-bit group, which is computationally infeasible.
- **Data Minimization:** Only elements belonging to the intersection $S_A \cap S_B$ are identified. Elements exclusive to Bank A or Bank B remain completely unrevealed.
- **Ledger Confidentiality:** No account numbers, transaction amounts, timestamps, or balances are shared during PSI.

## 3. Ethical AI & Human-in-the-Loop Safeguards
1. **Strict Non-Automation:** The system never executes automated fund freezing, payment blocking, or customer blacklisting.
2. **Transparent Reason Codes:** Every alert contains both SHAP model feature attributions and independent graph telemetry.
3. **Audit Logging:** Every case disposition (Pending, Under Review, Escalated, Closed) and investigator note is logged with timestamps and user roles.
4. **False Positive Mitigation:** Continuous evaluation against legitimate customer archetypes (gig workers, merchants, first-time users) to prevent discriminatory bias.
