import pytest

from scripts.migration_preflight import (
    EXPECTED_USER_COLUMNS,
    ColumnSpec,
    SchemaState,
    validate_legacy_user_schema,
)


def _state():
    schema = {
        "user_id": ColumnSpec("bigint", False),
        "username": ColumnSpec("character varying", True, 128),
        "full_name": ColumnSpec("character varying", False, 128),
        "language_code": ColumnSpec("character varying", False, 4),
        "banned": ColumnSpec("boolean", False),
        "active": ColumnSpec("boolean", False),
        "last_active": ColumnSpec("timestamp without time zone", False),
        "created_at": ColumnSpec("timestamp without time zone", False),
    }
    return SchemaState(
        tables=frozenset({"user"}),
        user_columns=EXPECTED_USER_COLUMNS,
        user_count=10,
        user_primary_key=("user_id",),
        user_column_specs=tuple(schema.items()),
    )


def test_legacy_schema_contract():
    validate_legacy_user_schema(_state())


def test_schema_contract_rejects_missing_column():
    state = _state()
    broken = SchemaState(
        tables=state.tables,
        user_columns=state.user_columns - {"language_code"},
        user_count=state.user_count,
        user_primary_key=state.user_primary_key,
        user_column_specs=state.user_column_specs,
    )
    with pytest.raises(RuntimeError, match="missing required columns"):
        validate_legacy_user_schema(broken)
