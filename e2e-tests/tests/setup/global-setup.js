const { Client } = require('pg');
const fs = require('fs');
const path = require('path');

async function globalSetup() {
  console.log('Setting up test database...');
  
  const client = new Client({
    connectionString: process.env.DATABASE_URL || 'postgresql://localrag:localrag123@localhost:5433/localrag_test',
  });

  try {
    await client.connect();
    
    // Check if tables exist, if not initialize schema
    console.log('Checking database schema...');
    const tableCheck = await client.query(`
      SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'users'
      );
    `);
    
    if (!tableCheck.rows[0].exists) {
      console.log('Initializing database schema...');
      const initSqlPath = path.join(__dirname, '../../../init_db.sql');
      if (fs.existsSync(initSqlPath)) {
        const initSql = fs.readFileSync(initSqlPath, 'utf8');
        await client.query(initSql);
        console.log('Schema initialized from init_db.sql');
      } else {
        // Create basic schema
        await client.query(`
          CREATE EXTENSION IF NOT EXISTS vector;
          CREATE EXTENSION IF NOT EXISTS pgcrypto;
          
          CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            role VARCHAR(20) DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
          );
          
          CREATE TABLE documents (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            file_path VARCHAR(500) NOT NULL,
            file_size BIGINT,
            file_type VARCHAR(50),
            total_chunks INTEGER DEFAULT 0,
            status VARCHAR(20) DEFAULT 'processing',
            uploaded_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
          );
          
          CREATE TABLE document_chunks (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            embedding vector(384),
            page_number INTEGER
          );
          
          CREATE TABLE chat_sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title VARCHAR(255) DEFAULT 'Nova Conversa',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
          );
          
          CREATE TABLE chat_messages (
            id SERIAL PRIMARY KEY,
            session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
            role VARCHAR(20) NOT NULL,
            content TEXT NOT NULL,
            sources JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
          );
          
          CREATE INDEX ON document_chunks USING hnsw (embedding vector_cosine_ops);
        `);
        console.log('Basic schema created');
      }
    }
    
    // Clean existing data
    console.log('Cleaning database...');
    await client.query('TRUNCATE TABLE chat_messages, chat_sessions, document_chunks, documents, users CASCADE');
    
    // Create test user with pre-computed hash
    console.log('Creating test user...');
    const hashedPassword = '$2b$12$3XtOBtt5WQn1i3lOaoUOAuGT9bjSAAQTJsXiuk5iiF08mnkYRTOUi';
    await client.query(
      'INSERT INTO users (id, username, hashed_password, role) VALUES ($1, $2, $3, $4)',
      [1, 'localuser', hashedPassword, 'admin']
    );
    
    console.log('Test database setup complete');
  } catch (error) {
    console.error('Error setting up test database:', error);
    throw error;
  } finally {
    await client.end();
  }
}

module.exports = globalSetup;
