# Pipeline Issues

## #471: Parallel Entity Detection Fails for Implicit Multi-Entity Queries
Pipeline fails to detect multiple entities when they're implied rather than explicitly listed in query params. Affects rain/weather and trend analysis.

### Details:
1. **Current Behavior**:
   - Fails on queries like "Which driver performs best in the rain?"
   - Cannot handle "What team has improved the most over the last 5 seasons?"
   - Misses multi-entity comparison in "How does Ferrari perform compared to Red Bull in wet conditions?"

2. **Root Causes**:
   - Entity detection only works with explicit lists in params
   - No semantic understanding of comparative terms ("best", "most", "compared")
   - Weather conditions not properly mapped to entity requirements

3. **Impact**:
   - 30% failure rate on ambiguous queries
   - 25% failure rate in API fetch for multi-entity queries
   - All failures manifest as "No parallel entities found" error

4. **Affected Query Types**:
   - Performance comparisons in specific conditions
   - Historical trend analysis across multiple entities
   - Implicit entity comparisons ("best", "fastest", "most improved") 