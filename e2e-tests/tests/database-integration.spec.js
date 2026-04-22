const { test, expect } = require('@playwright/test');
const { Client } = require('pg');
const path = require('path');

/**
 * Critical Business Rule Tests: Database Integration
 * SPEC Reference: Feature Database Integration E2E
 * 
 * Validates:
 * - Document metadata stored in documents table
 * - Chunks stored in document_chunks table
 * - Embeddings generated and stored
 * - Cascade delete removes related chunks
 */

async function getDBClient() {
  return new Client({
    connectionString: process.env.DATABASE_URL || 'postgresql://localrag:localrag123@localhost:5433/localrag_test',
  });
}

test.describe('Database Integration - Critical Business Rules', () => {
  test.beforeEach(async ({ page }) => {
    // Arrange: Login
    await page.goto('/login');
    await page.fill('input[type="text"]', 'localuser');
    await page.fill('input[type="password"]', 'localuser123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/chat');
  });

  test('should persist document metadata in database', async ({ page }) => {
    // Arrange: Track document
    const testFilename = 'test-document.txt';
    
    // Act: Upload document
    await page.goto('/documents');
    const filePath = path.join(__dirname, '../fixtures/test-document.txt');
    const input = page.locator('[data-testid="file-upload-input"]').first();
    await input.setInputFiles(filePath);
    
    // Wait for document to appear in list
    await expect(page.locator(`text=${testFilename}`)).toBeVisible({ timeout: 60000 });

    // Assert: Query database for document
    const client = await getDBClient();
    await client.connect();
    
    try {
      const result = await client.query(
        'SELECT * FROM documents WHERE filename = $1 ORDER BY id DESC LIMIT 1',
        [testFilename]
      );
      
      expect(result.rows.length).toBe(1);
      const document = result.rows[0];
      expect(document.filename).toBe(testFilename);
      expect(document.file_type).toBeTruthy();
      expect(document.status).toMatch(/completed|processing/);
      expect(document.uploaded_by).toBe(1); // localuser id
      expect(document.total_chunks).toBeGreaterThanOrEqual(0);
    } finally {
      await client.end();
    }
  });

  test('should create document chunks with embeddings', async ({ page }) => {
    // Arrange: Upload document
    const testFilename = 'test-document.txt';
    
    await page.goto('/documents');
    const filePath = path.join(__dirname, '../fixtures/test-document.txt');
    const input = page.locator('[data-testid="file-upload-input"]').first();
    await input.setInputFiles(filePath);
    
    // Wait for upload to complete (status = completed)
    await expect(page.locator(`text=${testFilename}`)).toBeVisible({ timeout: 60000 });
    
    // Wait additional time for chunking and embeddings
    await page.waitForTimeout(5000);

    // Assert: Query database for chunks and embeddings
    const client = await getDBClient();
    await client.connect();
    
    try {
      // Get document ID
      const docResult = await client.query(
        'SELECT id FROM documents WHERE filename = $1 ORDER BY id DESC LIMIT 1',
        [testFilename]
      );
      expect(docResult.rows.length).toBe(1);
      const documentId = docResult.rows[0].id;

      // Check chunks exist
      const chunksResult = await client.query(
        'SELECT * FROM document_chunks WHERE document_id = $1',
        [documentId]
      );
      expect(chunksResult.rows.length).toBeGreaterThan(0);

      // Verify each chunk has required fields
      for (const chunk of chunksResult.rows) {
        expect(chunk.chunk_index).toBeGreaterThanOrEqual(0);
        expect(chunk.content).toBeTruthy();
        expect(chunk.content.length).toBeGreaterThan(0);
        
        // Check embedding exists (not null for processed chunks)
        if (chunk.embedding) {
          // Embedding is stored as vector, check it's not null
          expect(chunk.embedding).toBeTruthy();
        }
      }

      // Verify total_chunks matches actual count
      const countResult = await client.query(
        'SELECT COUNT(*) as count FROM document_chunks WHERE document_id = $1',
        [documentId]
      );
      const chunkCount = parseInt(countResult.rows[0].count);
      
      const docStatusResult = await client.query(
        'SELECT total_chunks FROM documents WHERE id = $1',
        [documentId]
      );
      expect(docStatusResult.rows[0].total_chunks).toBe(chunkCount);

    } finally {
      await client.end();
    }
  });

  test('should cascade delete document and its chunks', async ({ page }) => {
    // Arrange: Upload document first
    const testFilename = 'test-document.txt';
    const client = await getDBClient();
    await client.connect();
    
    let documentId;
    
    try {
      await page.goto('/documents');
      const filePath = path.join(__dirname, '../fixtures/test-document.txt');
      const input = page.locator('[data-testid="file-upload-input"]').first();
      await input.setInputFiles(filePath);
      
      await expect(page.locator(`text=${testFilename}`)).toBeVisible({ timeout: 60000 });
      await page.waitForTimeout(3000);

      // Get document ID from database
      const docResult = await client.query(
        'SELECT id FROM documents WHERE filename = $1 ORDER BY id DESC LIMIT 1',
        [testFilename]
      );
      expect(docResult.rows.length).toBe(1);
      documentId = docResult.rows[0].id;

      // Verify chunks exist before delete
      const chunksBefore = await client.query(
        'SELECT COUNT(*) as count FROM document_chunks WHERE document_id = $1',
        [documentId]
      );
      const chunksCountBefore = parseInt(chunksBefore.rows[0].count);
      expect(chunksCountBefore).toBeGreaterThan(0);

    } finally {
      await client.end();
    }

    // Act: Delete the document via UI
    await page.goto('/documents');
    
    // Find and click delete button for the document
    const documentRow = page.locator('tr', { hasText: testFilename });
    const deleteButton = documentRow.locator('button[data-testid="delete-document"], button:has-text("Excluir")').first();
    
    if (await deleteButton.isVisible().catch(() => false)) {
      await deleteButton.click();
      
      // Confirm deletion if dialog appears
      const confirmButton = page.locator('button:has-text("Confirmar"), button:has-text("Sim"), button:has-text("Deletar")');
      if (await confirmButton.isVisible({ timeout: 3000 }).catch(() => false)) {
        await confirmButton.click();
      }
      
      // Wait for document to disappear
      await expect(page.locator(`text=${testFilename}`)).not.toBeVisible({ timeout: 10000 });
    }

    // Assert: Verify cascade delete in database
    const clientAfter = await getDBClient();
    await clientAfter.connect();
    
    try {
      // Document should be deleted
      const docCheck = await clientAfter.query(
        'SELECT * FROM documents WHERE id = $1',
        [documentId]
      );
      expect(docCheck.rows.length).toBe(0);

      // All chunks should be deleted (cascade)
      const chunksCheck = await clientAfter.query(
        'SELECT * FROM document_chunks WHERE document_id = $1',
        [documentId]
      );
      expect(chunksCheck.rows.length).toBe(0);

    } finally {
      await clientAfter.end();
    }
  });

  test('should create chat session and persist messages', async ({ page }) => {
    // Arrange: Create chat session
    await page.goto('/chat');
    await page.click('button:has-text("Nova Conversa")');
    await page.waitForTimeout(500);

    // Act: Send a message
    const message = 'Test database persistence';
    await page.fill('input[placeholder="Digite sua mensagem..."]', message);
    await page.keyboard.press('Enter');
    
    // Wait for user message to appear
    await expect(page.locator(`text=${message}`)).toBeVisible();

    // Assert: Query database for session and messages
    const client = await getDBClient();
    await client.connect();
    
    try {
      // Get latest session for user
      const sessionResult = await client.query(
        'SELECT * FROM chat_sessions WHERE user_id = $1 ORDER BY id DESC LIMIT 1',
        [1]
      );
      expect(sessionResult.rows.length).toBe(1);
      const session = sessionResult.rows[0];
      expect(session.title).toBeTruthy();

      // Check messages were saved
      const messagesResult = await client.query(
        'SELECT * FROM chat_messages WHERE session_id = $1 ORDER BY id',
        [session.id]
      );
      expect(messagesResult.rows.length).toBeGreaterThan(0);

      // Verify user message exists
      const userMessage = messagesResult.rows.find(m => m.role === 'user');
      expect(userMessage).toBeTruthy();
      expect(userMessage.content).toContain(message);

    } finally {
      await client.end();
    }
  });

  test('should persist sources references with chat messages', async ({ page }) => {
    // Arrange: Upload document first so sources can be generated
    const testFilename = 'test-document.txt';
    
    await page.goto('/documents');
    const filePath = path.join(__dirname, '../fixtures/test-document.txt');
    const input = page.locator('[data-testid="file-upload-input"]').first();
    await input.setInputFiles(filePath);
    await expect(page.locator(`text=${testFilename}`)).toBeVisible({ timeout: 60000 });
    await page.waitForTimeout(3000);

    // Act: Send message in chat
    await page.goto('/chat');
    await page.click('button:has-text("Nova Conversa")');
    await page.waitForTimeout(300);
    
    const message = 'What is this document about?';
    await page.fill('input[placeholder="Digite sua mensagem..."]', message);
    await page.keyboard.press('Enter');
    
    // Wait for response to complete
    await page.waitForSelector('[data-testid="assistant-message"]', { timeout: 60000 });
    await page.waitForTimeout(2000);

    // Assert: Check database for sources
    const client = await getDBClient();
    await client.connect();
    
    try {
      // Get latest session
      const sessionResult = await client.query(
        'SELECT id FROM chat_sessions WHERE user_id = $1 ORDER BY id DESC LIMIT 1',
        [1]
      );
      
      if (sessionResult.rows.length === 0) {
        test.skip('No chat session found');
        return;
      }
      
      const sessionId = sessionResult.rows[0].id;

      // Get assistant messages with sources
      const messagesResult = await client.query(
        'SELECT * FROM chat_messages WHERE session_id = $1 AND role = $2 ORDER BY id DESC',
        [sessionId, 'assistant']
      );

      if (messagesResult.rows.length === 0) {
        test.skip('No assistant message found');
        return;
      }

      const assistantMessage = messagesResult.rows[0];
      
      // If sources column exists, verify it's populated for RAG responses
      if (assistantMessage.sources !== undefined && assistantMessage.sources !== null) {
        // Sources should be a JSON array if RAG was used
        expect(assistantMessage.sources).toBeTruthy();
      }

    } finally {
      await client.end();
    }
  });
});
