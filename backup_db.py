"""
Simple PostgreSQL backup script using psycopg2.

Usage:
    Local:  python backup_db.py
    Render: python backup_db.py --source render --output render_backup.sql
"""
import os
import sys
import argparse
import psycopg2
from io import StringIO
import datetime


def get_connection(source):
    if source == "render":
        database_url = os.environ.get("DATABASE_URL")
        if database_url:
            return psycopg2.connect(database_url)
        raise RuntimeError("DATABASE_URL not set for render source")
    else:
        return psycopg2.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            port=int(os.environ.get("DB_PORT", "5432")),
            dbname=os.environ.get("DB_NAME", "gamerock"),
            user=os.environ.get("DB_USER", "gamerock_user"),
            password=os.environ.get("DB_PASSWORD", "gamerock_password"),
        )


def get_enum_types(conn):
    """Get all enum types with their values."""
    cur = conn.cursor()
    cur.execute("""
        SELECT
            t.typname AS type_name,
            array_agg(e.enumlabel ORDER BY e.enumsortorder) AS values
        FROM pg_type t
        JOIN pg_enum e ON e.enumtypid = t.oid
        JOIN pg_namespace n ON n.oid = t.typnamespace
        WHERE n.nspname = 'public'
          AND t.typtype = 'e'
        GROUP BY t.typname
        ORDER BY t.typname;
    """)
    enums = cur.fetchall()
    cur.close()
    return enums


def get_tables_sorted(conn):
    """Get tables sorted by FK dependency (parent tables first)."""
    cur = conn.cursor()
    cur.execute("""
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY tablename;
    """)
    all_tables = [row[0] for row in cur.fetchall()]
    cur.close()

    # Get FK relationships
    cur = conn.cursor()
    cur.execute("""
        SELECT
            rel1.relname AS table_name,
            rel2.relname AS referenced_table
        FROM pg_constraint c
        JOIN pg_class rel1 ON c.conrelid = rel1.oid
        JOIN pg_namespace nsp1 ON nsp1.oid = c.connamespace
        JOIN pg_class rel2 ON c.confrelid = rel2.oid
        WHERE c.contype = 'f'
          AND nsp1.nspname = 'public';
    """)
    fk_pairs = cur.fetchall()
    cur.close()

    # Topological sort: tables with no FK deps come first
    deps = {t: set() for t in all_tables}
    for table_name, referenced_table in fk_pairs:
        if table_name in deps and referenced_table in deps:
            deps[table_name].add(referenced_table)

    result = []
    visited = set()
    in_progress = set()

    def visit(table):
        if table in visited or table in in_progress:
            return
        in_progress.add(table)
        for dep in sorted(deps.get(table, [])):
            visit(dep)
        in_progress.discard(table)
        visited.add(table)
        result.append(table)

    for t in all_tables:
        visit(t)

    return result


def get_table_create_sql(conn, table):
    """Build CREATE TABLE statement for a given table."""
    cur = conn.cursor()
    cur.execute("""
        SELECT
            a.attname AS column_name,
            format_type(a.atttypid, a.atttypmod) AS data_type,
            a.attnotnull AS not_null,
            pg_get_expr(d.adbin, d.adrelid) AS column_default
        FROM pg_attribute a
        LEFT JOIN pg_attrdef d ON (a.attrelid, a.attnum) = (d.adrelid, d.adnum)
        JOIN pg_class c ON a.attrelid = c.oid
        WHERE c.relname = %s
          AND a.attnum > 0
          AND NOT a.attisdropped
        ORDER BY a.attnum;
    """, (table,))
    columns = cur.fetchall()

    col_defs = []
    for col_name, data_type, not_null, col_default in columns:
        col_def = f'    "{col_name}" {data_type}'
        if col_default:
            col_def += f' DEFAULT {col_default}'
        if not_null:
            col_def += ' NOT NULL'
        col_defs.append(col_def)

    # Primary key
    cur.execute("""
        SELECT a.attname
        FROM pg_index i
        JOIN pg_attribute a ON i.indrelid = a.attrelid AND a.attnum = ANY(i.indkey)
        JOIN pg_class c ON i.indrelid = c.oid
        WHERE i.indisprimary AND c.relname = %s
        ORDER BY a.attnum;
    """, (table,))
    pk_cols = [row[0] for row in cur.fetchall()]
    if pk_cols:
        pk_str = ", ".join(f'"{c}"' for c in pk_cols)
        col_defs.append(f'    PRIMARY KEY ({pk_str})')

    # Foreign keys
    cur.execute("""
        SELECT kcu.column_name,
               ccu.table_name AS foreign_table,
               ccu.column_name AS foreign_column,
               con.conname AS constraint_name
        FROM pg_constraint con
        JOIN pg_class c ON con.conrelid = c.oid
        JOIN pg_namespace n ON n.oid = c.relnamespace
        JOIN information_schema.key_column_usage kcu
            ON kcu.table_name = c.relname
            AND kcu.table_schema = n.nspname
            AND kcu.constraint_name = con.conname
        JOIN information_schema.constraint_column_usage ccu
            ON ccu.constraint_name = con.conname
            AND ccu.table_schema = n.nspname
        WHERE c.relname = %s
          AND con.contype = 'f'
          AND n.nspname = 'public'
        ORDER BY kcu.ordinal_position;
    """, (table,))
    fk_cols = []
    fk_map = {}
    for col_name, foreign_table, foreign_column, constraint_name in cur.fetchall():
        if constraint_name not in fk_map:
            fk_map[constraint_name] = []
        fk_map[constraint_name].append((col_name, foreign_table, foreign_column))

    for constraint_name, cols in fk_map.items():
        col_str = ", ".join(f'"{c}"' for c, _, _ in cols)
        ref_col_str = ", ".join(f'"{fc}"' for _, _, fc in cols)
        ref_table = cols[0][1]
        col_defs.append(
            f'    CONSTRAINT "{constraint_name}" '
            f'FOREIGN KEY ({col_str}) REFERENCES "{ref_table}" ({ref_col_str}) '
            f'ON DELETE SET NULL'
        )

    cur.close()
    return f'CREATE TABLE "{table}" (\n' + ",\n".join(col_defs) + "\n);"


def dump_database(conn, output_file, source_name):
    tables = get_tables_sorted(conn)
    cur = conn.cursor()
    out = StringIO()

    out.write(f"-- PostgreSQL database dump ({source_name})\n")
    out.write("-- Generated by backup_db.py\n")
    out.write(f"-- Dumped at: {datetime.datetime.now().isoformat()}\n")
    out.write(f"-- Tables: {', '.join(tables)}\n\n")

    out.write("SET statement_timeout = 0;\n")
    out.write("SET lock_timeout = 0;\n")
    out.write("SET client_encoding = 'UTF8';\n")
    out.write("SET standard_conforming_strings = on;\n")
    out.write("SET check_function_bodies = false;\n")
    out.write("SET xmloption = content;\n")
    out.write("SET client_min_messages = warning;\n")
    out.write("SET row_security = off;\n\n")
    out.write("SET search_path = public;\n\n")

    # DROP statements in reverse dependency order
    out.write("-- Drop existing tables (reverse dependency order)\n")
    for table in reversed(tables):
        out.write(f'DROP TABLE IF EXISTS "{table}" CASCADE;\n')
    out.write("\n")

    # DROP enum types
    enums = get_enum_types(conn)
    if enums:
        out.write("-- Drop enum types\n")
        for enum_name, enum_vals in enums:
            out.write(f'DROP TYPE IF EXISTS "{enum_name}" CASCADE;\n')
        out.write("\n")

    # CREATE enum types
    if enums:
        out.write("-- Create enum types (must be before tables that reference them)\n")
        for enum_name, enum_vals in enums:
            vals_str = ", ".join(f"'{v}'" for v in enum_vals)
            out.write(f'CREATE TYPE "{enum_name}" AS ENUM ({vals_str});\n')
        out.write("\n")

    # CREATE TABLE statements
    out.write("-- Create tables\n")
    for table in tables:
        create_sql = get_table_create_sql(conn, table)
        out.write(create_sql + "\n\n")

    # Indexes
    cur.execute("""
        SELECT indexdef
        FROM pg_indexes
        WHERE schemaname = 'public'
          AND indexdef LIKE '%USING%'
          AND indexdef NOT LIKE '%PRIMARY KEY%'
        ORDER BY indexname;
    """)
    indexes = cur.fetchall()
    if indexes:
        out.write("-- Indexes\n")
        for idx in indexes:
            out.write(f"{idx[0]};\n")
        out.write("\n")

    # Sequences
    cur.execute("""
        SELECT c.relname
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relkind = 'S' AND n.nspname = 'public';
    """)
    sequences = cur.fetchall()
    for seq in sequences:
        seq_name = seq[0]
        if seq_name.endswith('_id_seq'):
            table_name = seq_name[:-4]
            out.write(
                f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), "
                f"COALESCE((SELECT MAX(id) FROM {table_name}), 1), true);\n"
            )
    if sequences:
        out.write("\n")

    # Data
    out.write("-- Data dump\n")
    total_rows = 0
    for table in tables:
        cur.execute(f'SELECT * FROM "{table}" LIMIT 1')
        if not cur.description:
            out.write(f"-- Table \"{table}\": no columns\n\n")
            continue

        columns = [desc[0] for desc in cur.description]
        col_str = ", ".join(f'"{c}"' for c in columns)

        cur.execute(f'SELECT {col_str} FROM "{table}"')
        rows = cur.fetchall()
        total_rows += len(rows)

        if not rows:
            out.write(f"-- Table \"{table}\": 0 rows\n\n")
            continue

        out.write(f"-- Data for table \"{table}\"\n")
        for row in rows:
            values = []
            for val in row:
                if val is None:
                    values.append("NULL")
                elif isinstance(val, bool):
                    values.append("TRUE" if val else "FALSE")
                elif isinstance(val, (int, float)):
                    values.append(str(val))
                elif isinstance(val, bytes):
                    values.append(f"'\\x{val.hex()}'::bytea")
                else:
                    escaped = str(val).replace("'", "''")
                    values.append(f"'{escaped}'")
            values_str = ", ".join(values)
            out.write(f'INSERT INTO "{table}" ({col_str}) VALUES ({values_str});\n')
        out.write("\n")

    out.write("SET statement_timeout = 0;\n")
    out.write("SET lock_timeout = 0;\n")
    cur.close()

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(out.getvalue())
    print(f"Dumped {len(tables)} tables ({total_rows} rows) to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="PostgreSQL database backup utility"
    )
    parser.add_argument(
        "--source", "-s",
        choices=["local", "render"],
        default="local",
        help="Database source (default: local)"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output file path"
    )
    args = parser.parse_args()

    output = args.output or f"gamerock_{args.source}_dump.sql"

    try:
        conn = get_connection(args.source)
        print(f"Connected to database: {conn.get_dsn_parameters().get('dbname')}")
        dump_database(conn, output, args.source)
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
