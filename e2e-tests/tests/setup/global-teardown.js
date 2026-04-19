const { Client } = require('pg');

async function globalTeardown() {
  console.log('Tearing down test database...');
  
  const client = new Client({
    connectionString: process.env.DATABASE_URL || 'postgresql://localrag:localrag123@localhost:5433/localrag_test',
  });

  try {
    await client.connect();
    await client.query('TRUNCATE TABLE chat_messages, chat_sessions, document_chunks, documents, users CASCADE');
    console.log('Test database cleaned');
  } catch (error) {
    console.error('Error cleaning test database:', error);
  } finally {
    await client.end();
  }
}

module.exports = globalTeardown;
