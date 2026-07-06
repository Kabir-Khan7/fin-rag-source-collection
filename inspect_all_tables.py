"""
Temporary script to inspect all staging tables in the fin_model database.

Lists every base table, its columns, types, lengths, nullability, and
whether a primary key exists. Run once to inform the multi-table model
design, then delete.
"""

from sqlalchemy import text

from app.database.engine import engine


def inspect_all_tables() -> None:
    """Inspect all user tables in the database and report their structure."""
    with engine.connect() as connection:
        # 1. List all base tables in the database.
        print("=" * 70)
        print("ALL TABLES in fin_model")
        print("=" * 70)
        tables = connection.execute(
            text(
                """
                SELECT TABLE_SCHEMA, TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
                """
            )
        )
        table_list = [(row[0], row[1]) for row in tables]
        for schema, name in table_list:
            print(f"  {schema}.{name}")

        # 2. For each table, show columns and primary key.
        for schema, name in table_list:
            print("\n" + "=" * 70)
            print(f"TABLE: {schema}.{name}")
            print("=" * 70)

            columns = connection.execute(
                text(
                    """
                    SELECT COLUMN_NAME, DATA_TYPE,
                           CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = :tname AND TABLE_SCHEMA = :tschema
                    ORDER BY ORDINAL_POSITION
                    """
                ),
                {"tname": name, "tschema": schema},
            )
            print("  COLUMNS:")
            for col in columns:
                length = f"({col[2]})" if col[2] else ""
                if col[2] == -1:
                    length = "(MAX)"
                nullable = "NULL" if col[3] == "YES" else "NOT NULL"
                print(f"    {col[0]:<28} {col[1]}{length:<10} {nullable}")

            pk = connection.execute(
                text(
                    """
                    SELECT COLUMN_NAME
                    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                    WHERE TABLE_NAME = :tname AND TABLE_SCHEMA = :tschema
                        AND CONSTRAINT_NAME LIKE 'PK%'
                    """
                ),
                {"tname": name, "tschema": schema},
            )
            pk_cols = [row[0] for row in pk]
            print("  PRIMARY KEY:", ", ".join(pk_cols) if pk_cols else "⚠️  NONE")


if __name__ == "__main__":
    inspect_all_tables()