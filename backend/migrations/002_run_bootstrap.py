"""Idempotent additive migration for runs created before winner bootstrap v2.

Only adds columns when they are missing; historical runs keep their stored JSON
result and are never recomputed or rewritten.
"""
from sqlalchemy import text
from src.config.database import engine

_ADDITIONS = (
    ('bootstrap_seed', 'ALTER TABLE rank_test_runs ADD COLUMN bootstrap_seed INTEGER NOT NULL DEFAULT 20261113'),
    ('bootstrap_replicates', 'ALTER TABLE rank_test_runs ADD COLUMN bootstrap_replicates INTEGER NOT NULL DEFAULT 9999'),
)


def ensure_run_bootstrap_columns():
    with engine.connect() as conn:
        db_name = conn.execute(text('SELECT DATABASE()')).scalar_one()
        existing = {row[0] for row in conn.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = :schema AND table_name = 'rank_test_runs'"
        ), {'schema': db_name})}
        for column, ddl in _ADDITIONS:
            if column not in existing:
                conn.execute(text(ddl))
        conn.commit()
