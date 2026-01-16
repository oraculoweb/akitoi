#!/usr/bin/env python3
"""
Script to check Supabase database status and display schema information.

This script verifies the database connection and shows information about
the current schema, including tables, indexes, and migration status.
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import inspect, text
from src.akitoi.database.connection import engine


def check_database_connection():
    """Test database connection."""
    print("🔌 Testing database connection...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connected to PostgreSQL")
            print(f"   Version: {version.split(',')[0]}")
            return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def check_tables():
    """Check if all required tables exist."""
    print("\n📊 Checking database schema...")

    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    required_tables = ['profiles', 'links', 'analytics_events']

    print(f"\n   Found {len(existing_tables)} tables:")
    for table_name in existing_tables:
        if table_name in required_tables:
            print(f"   ✅ {table_name}")
        else:
            print(f"   ℹ️  {table_name}")

    missing_tables = set(required_tables) - set(existing_tables)
    if missing_tables:
        print(f"\n   ❌ Missing tables: {', '.join(missing_tables)}")
        print("\n   Run './scripts/init_db.sh' to create the schema")
        return False

    return True


def show_table_info():
    """Show detailed information about each table."""
    print("\n📋 Table Details:")

    inspector = inspect(engine)

    for table_name in ['profiles', 'links', 'analytics_events']:
        if table_name not in inspector.get_table_names():
            continue

        print(f"\n   {table_name.upper()}")
        print("   " + "=" * 50)

        # Get columns
        columns = inspector.get_columns(table_name)
        print(f"   Columns ({len(columns)}):")
        for col in columns:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            col_type = str(col['type'])
            print(f"      - {col['name']:<20} {col_type:<20} {nullable}")

        # Get indexes
        indexes = inspector.get_indexes(table_name)
        if indexes:
            print(f"\n   Indexes ({len(indexes)}):")
            for idx in indexes:
                unique = "UNIQUE" if idx['unique'] else ""
                cols = ", ".join(idx['column_names'])
                print(f"      - {idx['name']:<30} ({cols}) {unique}")

        # Get foreign keys
        foreign_keys = inspector.get_foreign_keys(table_name)
        if foreign_keys:
            print(f"\n   Foreign Keys ({len(foreign_keys)}):")
            for fk in foreign_keys:
                print(f"      - {fk['name']:<30} -> {fk['referred_table']}.{fk['referred_columns'][0]}")


def check_migration_status():
    """Check Alembic migration status."""
    print("\n🔄 Migration Status:")

    try:
        with engine.connect() as conn:
            # Check if alembic_version table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'alembic_version'
                )
            """))
            if not result.scalar():
                print("   ❌ Alembic not initialized")
                print("   Run './scripts/init_db.sh' to initialize")
                return

            # Get current revision
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            row = result.fetchone()
            if row:
                print(f"   ✅ Current revision: {row[0]}")
            else:
                print("   ⚠️  No migrations applied yet")

    except Exception as e:
        print(f"   ❌ Error checking migration status: {e}")


def get_row_counts():
    """Get row counts for each table."""
    print("\n📈 Row Counts:")

    try:
        with engine.connect() as conn:
            for table_name in ['profiles', 'links', 'analytics_events']:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                print(f"   {table_name:<20} {count:>10} rows")
    except Exception as e:
        print(f"   ❌ Error getting row counts: {e}")


def main():
    """Main function."""
    print("=" * 60)
    print("Akitoi - Supabase Database Status Check")
    print("=" * 60)

    # Check DATABASE_URL
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("\n❌ DATABASE_URL not set!")
        print("Please set it in your .env file or environment variables.")
        sys.exit(1)

    # Mask password in URL for display
    display_url = db_url
    if '@' in display_url and ':' in display_url:
        parts = display_url.split('@')
        if len(parts) == 2:
            user_pass = parts[0].split('//')[-1]
            if ':' in user_pass:
                user = user_pass.split(':')[0]
                display_url = display_url.replace(user_pass, f"{user}:****")

    print(f"\n🔗 Database URL: {display_url}")

    # Run checks
    if not check_database_connection():
        sys.exit(1)

    if not check_tables():
        sys.exit(1)

    show_table_info()
    check_migration_status()
    get_row_counts()

    print("\n" + "=" * 60)
    print("✅ Database check complete!")
    print("=" * 60)


if __name__ == '__main__':
    # Load .env file if it exists
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        os.environ.setdefault(key, value)

    main()
