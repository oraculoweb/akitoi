#!/bin/bash
# Supabase database initialization script

set -e  # Exit on error

echo "🚀 Akitoi - Supabase Database Initialization"
echo "============================================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file based on .env.example"
    echo ""
    echo "Steps:"
    echo "1. cp .env.example .env"
    echo "2. Update DATABASE_URL with your Supabase connection string"
    echo "3. Run this script again"
    exit 1
fi

# Load environment variables
echo "📋 Loading environment variables..."
export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ Error: DATABASE_URL not set in .env file!"
    exit 1
fi

echo "✅ Environment variables loaded"
echo ""

# Check database connection
echo "🔌 Testing database connection..."
python3 -c "
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text('SELECT version()'))
        version = result.scalar()
        print('✅ Database connection successful')
        print(f'📊 PostgreSQL version: {version.split(\",\")[0]}')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    exit 1
fi

echo ""

# Run migrations
echo "⬆️  Running Alembic migrations..."
echo "This will create all necessary tables and indexes in Supabase"
echo ""

alembic upgrade head

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Database initialized successfully!"
    echo ""
    echo "📊 Your Supabase database now has:"
    echo "   - profiles table (with indexes)"
    echo "   - links table (with indexes)"
    echo "   - analytics_events table (with indexes)"
    echo "   - Automatic timestamp triggers"
    echo ""
    echo "🎉 You're ready to start using Akitoi!"
    echo ""
    echo "Next steps:"
    echo "1. Start the API: ./scripts/run_dev.sh"
    echo "2. Visit http://localhost:8000/docs for API documentation"
else
    echo ""
    echo "❌ Migration failed!"
    echo "Please check the error messages above."
    exit 1
fi
