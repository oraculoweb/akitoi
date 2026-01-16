"""Initial Supabase schema for Akitoi platform

Revision ID: 001
Revises:
Create Date: 2026-01-15 20:25:00.000000

This migration creates the initial database schema optimized for Supabase PostgreSQL,
including profiles, links, and analytics events tables with appropriate indexes.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create initial database schema for Akitoi platform.

    Tables:
    - profiles: User bio hub profiles
    - links: Contact and social media links for profiles
    - analytics_events: Event tracking for views and clicks
    """

    # Create profiles table
    op.create_table(
        'profiles',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=50), nullable=False),
        sa.Column('bio', sa.Text(), nullable=True, server_default=''),
        sa.Column('profile_image_url', sa.String(length=500), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column(
            'theme',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{\"primary_color\": \"#007bff\", \"background_color\": \"#ffffff\", \"text_color\": \"#333333\", \"font_family\": \"Inter, sans-serif\"}'::jsonb")
        ),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('view_count >= 0', name='check_view_count_positive')
    )

    # Create indexes for profiles
    op.create_index('ix_profiles_id', 'profiles', ['id'])
    op.create_index('ix_profiles_slug', 'profiles', ['slug'], unique=True)
    op.create_index('ix_profiles_is_published', 'profiles', ['is_published'])
    op.create_index('idx_profiles_published_created', 'profiles', ['is_published', 'created_at'])
    op.create_index('idx_profiles_view_count', 'profiles', ['view_count'])

    # Create links table
    op.create_table(
        'links',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('profile_id', sa.String(length=36), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('label', sa.String(length=100), nullable=True),
        sa.Column('icon', sa.String(length=100), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('click_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ondelete='CASCADE'),
        sa.CheckConstraint('click_count >= 0', name='check_click_count_positive'),
        sa.CheckConstraint('"order" >= 0', name='check_order_positive')
    )

    # Create indexes for links
    op.create_index('ix_links_id', 'links', ['id'])
    op.create_index('ix_links_profile_id', 'links', ['profile_id'])
    op.create_index('idx_links_profile_order', 'links', ['profile_id', 'order'])
    op.create_index('idx_links_profile_type', 'links', ['profile_id', 'type'])

    # Create analytics_events table
    op.create_table(
        'analytics_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('profile_id', sa.String(length=36), nullable=False),
        sa.Column('link_id', sa.String(length=36), nullable=True),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('event_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['link_id'], ['links.id'], ondelete='SET NULL')
    )

    # Create indexes for analytics_events
    op.create_index('ix_analytics_events_profile_id', 'analytics_events', ['profile_id'])
    op.create_index('ix_analytics_events_event_type', 'analytics_events', ['event_type'])
    op.create_index('ix_analytics_events_created_at', 'analytics_events', ['created_at'])
    op.create_index('idx_analytics_profile_time', 'analytics_events', ['profile_id', 'created_at'])
    op.create_index('idx_analytics_event_type_time', 'analytics_events', ['event_type', 'created_at'])
    op.create_index('idx_analytics_link', 'analytics_events', ['link_id'])

    # Create trigger function to update updated_at timestamp
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    # Create trigger for profiles table
    op.execute("""
        CREATE TRIGGER update_profiles_updated_at
        BEFORE UPDATE ON profiles
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    """
    Drop all tables and functions created in upgrade.
    """
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS update_profiles_updated_at ON profiles;")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")

    # Drop tables (CASCADE will drop foreign key constraints)
    op.drop_table('analytics_events')
    op.drop_table('links')
    op.drop_table('profiles')
