"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-04-19 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('role', sa.String(20), server_default='admin', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )
    op.create_index('idx_users_username', 'users', ['username'])

    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=False),
        sa.Column('file_type', sa.String(50), nullable=False),
        sa.Column('total_chunks', sa.Integer(), server_default='0'),
        sa.Column('status', sa.String(20), server_default='processing', nullable=False),
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_documents_uploaded_by', 'documents', ['uploaded_by'])
    op.create_index('idx_documents_status', 'documents', ['status'])
    op.create_index('idx_documents_uploaded_at', 'documents', ['uploaded_at'])

    # Create document_chunks table
    op.create_table(
        'document_chunks',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(384), nullable=True),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_chunks_document_index', 'document_chunks', ['document_id', 'chunk_index'], unique=True)
    op.create_index('idx_chunks_document_id', 'document_chunks', ['document_id'])
    op.create_index('idx_chunks_embedding_hnsw', 'document_chunks', ['embedding'],
                    postgresql_using='hnsw',
                    postgresql_with={'m': 16, 'ef_construction': 64},
                    postgresql_ops={'embedding': 'vector_cosine_ops'})

    # Create chat_sessions table
    op.create_table(
        'chat_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), server_default='Nova Conversa', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_sessions_user_id', 'chat_sessions', ['user_id'])
    op.create_index('idx_sessions_updated_at', 'chat_sessions', ['updated_at'])

    # Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('sources', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_messages_session_id', 'chat_messages', ['session_id'])
    op.create_index('idx_messages_created_at', 'chat_messages', ['created_at'])
    op.create_index('idx_messages_sources', 'chat_messages', ['sources'], postgresql_using='gin')

    # Create system_config table
    op.create_table(
        'system_config',
        sa.Column('key', sa.String(100), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint('key')
    )

    # Create updated_at trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql'
    """)

    # Create triggers
    op.execute("""
        CREATE TRIGGER update_documents_updated_at
        BEFORE UPDATE ON documents
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column()
    """)
    op.execute("""
        CREATE TRIGGER update_sessions_updated_at
        BEFORE UPDATE ON chat_sessions
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column()
    """)

    # Insert initial data
    op.execute("""
        INSERT INTO users (username, hashed_password, role)
        VALUES ('localuser', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYMyzJ/Iy', 'admin')
    """)

    op.execute("""
        INSERT INTO system_config (key, value, description) VALUES
        ('llm_provider', 'openrouter', 'Provider de LLM'),
        ('llm_model', 'meta-llama/llama-3.2-3b-instruct:free', 'Modelo LLM'),
        ('llm_model_local', 'llama3.2', 'Modelo LLM local'),
        ('embedding_model', 'sentence-transformers/all-MiniLM-L6-v2', 'Modelo de embeddings'),
        ('embedding_dimensions', '384', 'Dimensoes do embedding'),
        ('chunk_size', '512', 'Tamanho do chunk'),
        ('chunk_overlap', '50', 'Sobreposicao entre chunks'),
        ('top_k_retrieval', '5', 'Numero de chunks'),
        ('temperature', '0.7', 'Temperatura do LLM'),
        ('max_tokens', '2048', 'Maximo de tokens'),
        ('system_prompt', 'Voce e um assistente util.', 'Prompt'),
        ('hnsw_m', '16', 'Parametro M'),
        ('hnsw_ef_construction', '64', 'Parametro ef_construction'),
        ('hnsw_ef_search', '100', 'Parametro ef_search'),
        ('file_max_size', '104857600', 'Tamanho maximo'),
        ('allowed_extensions', 'pdf,txt,docx,md', 'Extensoes')
    """)


def downgrade() -> None:
    op.drop_table('system_config')
    op.drop_table('chat_messages')
    op.drop_table('chat_sessions')
    op.drop_table('document_chunks')
    op.drop_table('documents')
    op.drop_table('users')
    op.execute('DROP FUNCTION IF EXISTS update_updated_at_column()')
    op.execute('DROP EXTENSION IF EXISTS pgcrypto')
    op.execute('DROP EXTENSION IF EXISTS vector')
