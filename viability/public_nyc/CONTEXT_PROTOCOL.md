# Supplemental context-delivery experiment

This is a controlled **local simulation**, supplementary to the unmodified-source review. It does not reconstruct an authentic historical deployment. Initial registered context contains the current data dictionary; a subsequent event registers the already retrieved NYC311 fare-program source. Source arrival is replayed, not watched in production.

The conversational reviewer has interpreted the fee rule and bound it to the yellow-trip source field. That interpretation and binding are supplied to the propagation mechanism explicitly. We are testing the mechanical distribution of this derived context, not autonomous document interpretation or independent contract applicability.

Create three local consumer fixtures: a monthly-BI consumer, a trip-review consumer, and a zone-reference consumer. Use the real dbt manifest to discover their upstream dependencies. Introducing the new source must invalidate the old context for the first two, publish replacement contexts with source provenance and the unresolved numeric-precision finding, and leave the unrelated zone-reference context unchanged. Replaying the same event must be idempotent. Source freshness must never turn into a semantic clearance: unresolved findings remain REVIEW_REQUIRED.

The delivery boundary is JSON context files and a simulated consumer freshness check. No Omni, Hex, Snowflake, Databricks, real agent runtime, message transport, or production polling is included.
