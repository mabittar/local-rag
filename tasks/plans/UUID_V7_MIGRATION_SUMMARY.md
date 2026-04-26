# UUID v7 Migration - Summary

**Date**: 21/04/2026  
**PostgreSQL Version**: 18.3  
**Status**: Completed  

---

## Overview

Migrated `document_chunks` table from `gen_random_uuid()` (UUID v4) to UUID v7 format using the `uuid_utils` Python library for better temporal ordering and improved database performance.

---

## Changes Made

### 1. Database Schema (init_db.sql)

**Before:**
```sql
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- ...
);
```

**After:**
```sql
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY,
    -- ...
);
```

**Rationale:**
- Removed server-side `DEFAULT gen_random_uuid()` 
- UUID generation moved to application layer using `uuid_utils.uuid7()`
- Ensures consistent UUID v7 format across all environments

---

### 2. Backend Model (app/models/document.py)

**Before:**
```python
id: UUID = Field(default_factory=uuid_utils.uuid7(), primary_key=True)
created_at: Optional[datetime] = Field(
    default=None, sa_column=Column(DateTime(timezone=True), server_default="now()")
)
```

**After:**
```python
id: UUID = Field(default_factory=uuid_utils.uuid7, primary_key=True)
created_at: Optional[datetime] = Field(
    default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True))
)
```

**Key Fixes:**
1. **Function Reference**: Changed `uuid_utils.uuid7()` → `uuid_utils.uuid7` (passes callable, not result)
2. **DateTime Default**: Changed `server_default="now()"` → `default_factory=datetime.utcnow` for SQLite compatibility

---

## UUID v7 Benefits

1. **Temporal Ordering**: UUIDs are sortable by creation time (unlike v4)
2. **Database Performance**: Better index locality when ordered by ID
3. **Sequential Access**: Range queries by time are more efficient
4. **Compatibility**: PostgreSQL 18+ supports UUID operations natively

---

## Test Results

All 19 backend tests passing:

| Category | Tests | Status |
|----------|-------|--------|
| Authentication | 4 | PASS |
| Chat | 6 | PASS |
| Documents | 9 | PASS |

```bash
cd backend && pytest tests/ -v
# 19 passed, 27 warnings in 5.21s
```

---

## Technical Notes

### PostgreSQL Extensions

The container uses PostgreSQL 18 with `pgcrypto` extension already enabled:
- `gen_random_uuid()` was available via pgcrypto
- UUID v7 requires application-level generation (Python library)

### uuid_utils Library

Uses `uuid-utils` package which provides:
- `uuid7()` - Time-ordered UUID (RFC 4122bis)
- `uuid7str()` - String representation
- Monotonic clock support for high-frequency generation

---

## Migration Path for Production

If you have existing data with UUID v4:

1. **Backup existing data**
2. **Create new table with v7 schema**
3. **Migrate data** (keeping old IDs as-is, only new IDs use v7)
4. **Or**: Keep existing v4 IDs, only new records get v7

UUID v7 and v4 are interoperable - both are valid UUID type.

---

## Files Modified

```
init_db.sql                          # Schema definition
backend/app/models/document.py       # Model definition
```

---

## Verification

```python
# Verify UUID v7 generation
import uuid_utils
uid = uuid_utils.uuid7()
print(uid)  # e.g., 018f3b4e-7a3d-7e1a-8b2c-9d4e5f6a7b8c
#         ^^^^^^^^ timestamp prefix (48 bits)
```

All tests pass successfully.
