# RINGTRACE AI — Data Dictionary & Schema Specification

## 1. Accounts Table (`data/processed/accounts.csv`)

| Column Name | Data Type | Description | Allowed Values / Example |
|---|---|---|---|
| `account_id` | String (Primary Key) | Unique account identifier within institution | `BNKA_ACC_00012` |
| `bank_id` | String | Originating simulated institution | `BANK_A`, `BANK_B`, `BANK_C` |
| `canonical_entity_id` | String | Underlying canonical individual ID (e.g. PAN/National ID) | `PAN_CANONICAL_001045` |
| `profile_type` | String | Customer behavioral profile | `SALARIED`, `GIG_WORKER`, `MERCHANT`, `STUDENT_FIRST_TIME`, `REGULAR_P2P`, `MULE_SUSPECT` |
| `account_age_days` | Integer | Age of account in days | 1 to 2000 |
| `initial_balance` | Float | Starting ledger balance in INR | >= 0.0 |
| `is_mule` | Integer (0/1) | Ground-truth simulation label | `0` (Legitimate), `1` (Mule) |
| `ring_id` | String | Ground-truth mule ring identifier | `NONE`, `RING_001`, `RING_002` |
| `ring_role` | String | Role played within fraud network | `LEGITIMATE`, `INITIAL_RECIPIENT`, `INTERMEDIATE_LAYER`, `CASHOUT_COLLECTOR` |

---

## 2. Transactions Table (`data/processed/transactions.csv`)

| Column Name | Data Type | Description | Allowed Values / Example |
|---|---|---|---|
| `transaction_id` | String (Primary Key) | Unique transaction identifier | `TX_0001245` |
| `timestamp` | Datetime (ISO 8601) | Exact date and time of transaction | `2026-11-16 14:22:10` |
| `sender_account` | String (Foreign Key) | Originating sender account | `BNKA_ACC_00012` |
| `receiver_account` | String (Foreign Key) | Destination recipient account | `BNKB_MULE_02_01` |
| `sender_bank` | String | Originating institution | `BANK_A`, `BANK_B`, `BANK_C` |
| `receiver_bank` | String | Destination institution | `BANK_A`, `BANK_B`, `BANK_C` |
| `amount` | Float | Transaction amount in INR | > 0.0 (Strictly positive) |
| `transaction_type` | String | UPI payment category | `UPI_P2P`, `UPI_MERCHANT`, `UPI_CROSS_BANK` |
| `is_suspicious` | Integer (0/1) | Ground-truth simulation label | `0` (Normal), `1` (Suspicious) |
| `ring_id` | String | Associated fraud ring scenario | `NONE`, `RING_001` |

---

## 3. Mule Rings Table (`data/synthetic/mule_rings.csv`)

| Column Name | Data Type | Description | Example |
|---|---|---|---|
| `ring_id` | String (Primary Key) | Unique ring identifier | `RING_001` |
| `scenario_type` | String | Fraud ring movement archetype | `RAPID_PASS_THROUGH`, `FAN_OUT_SPLITTER`, `FAN_IN_COLLECTOR`, `CROSS_BANK_CHAIN`, `CIRCULAR_LAYERING` |
| `accounts` | String (Delimited) | Semicolon-separated member account IDs | `BNKA_MULE_01_01;BNKB_MULE_01_02;BNKC_MULE_01_03` |
| `total_amount` | Float | Total funds routed through ring | `185000.00` |
| `hop_count` | Integer | Diameter / path length of ring | 2 to 6 |
| `duration_minutes` | Integer | Total elapsed laundering window | 15 to 180 |
| `cross_bank_count` | Integer | Number of inter-bank transfers | >= 1 |

---

## 4. Features Table (`data/processed/features.csv`)

| Feature Column | Description |
|---|---|
| `account_id` | Unique account identifier |
| `in_degree`, `out_degree` | Total incoming / outgoing transactions |
| `fan_in_distinct`, `fan_out_distinct` | Distinct sender / receiver accounts |
| `total_amount_in`, `total_amount_out` | Cumulative transaction volume |
| `pass_through_ratio` | Ratio of outgoing to incoming funds: `total_out / total_in` |
| `net_flow_ratio` | Directional flow normalized between -1.0 and +1.0 |
| `turnover_rate` | Fund turnover relative to account balance |
| `min_turnaround_time_sec` | Fastest turnaround between receiving and forwarding funds |
| `avg_turnaround_time_sec` | Mean turnaround time in seconds |
| `velocity_1h_max`, `velocity_24h_max` | Maximum transaction bursts in 1-hour and 24-hour windows |
| `cross_bank_tx_ratio` | Fraction of activity involving partner banks |
| `pagerank` | Network centrality score |
| `clustering_coeff` | Local network transitivity |
