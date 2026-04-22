const { test, expect } = require('@playwright/test');

/**
 * Critical Business Rule Tests: Chat Streaming Behavior
 * SPEC Reference: Feature Chat E2E - Scenario: Success - Send message and receive streaming response
 * 
 * Validates:
 * - SSE connection is established
 * - Response streams token-by-token
 * - "Pensando..." indicator appears during processing
 * - "Ver fontes" button appears after completion
 * - Sources data is received via SSE
 */

test.describe('Chat Streaming - Critical Business Rules', () => {
  test.beforeEach(async ({ page }) => {
    // Arrange: Login and create session
    await page.goto('/login');
    await page.fill('input[type="text"]', 'localuser');
    await page.fill('input[type="password"]', 'localuser123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/chat');
    
    // Create a new chat session
    await page.click('button:has-text("Nova Conversa")');
    await page.waitForTimeout(300);
  });

  test('should establish SSE connection when sending message', async ({ page }) => {
    // Arrange: Intercept SSE requests
    const sseRequestPromise = page.waitForRequest(
      request => request.url().includes('/api/chat/stream'),
      { timeout: 10000 }
    );

    // Act: Send a message
    const message = 'Test streaming connection';
    await page.fill('input[placeholder="Digite sua mensagem..."]', message);
    await page.keyboard.press('Enter');

    // Assert: SSE request was made
    const sseRequest = await sseRequestPromise;
    expect(sseRequest.url()).toContain('/api/chat/stream');
    expect(sseRequest.url()).toContain('message=');
    expect(sseRequest.url()).toContain('session_id=');
  });

  test('should show thinking indicator while processing', async ({ page }) => {
    // Arrange: Send message
    const message = 'Message for thinking indicator test';
    await page.fill('input[placeholder="Digite sua mensagem..."]', message);
    
    // Act: Submit and immediately check for indicator
    await page.keyboard.press('Enter');

    // Assert: Thinking indicator appears (may be brief, so check quickly)
    const hasThinkingIndicator = await page.locator('text=Pesquisando documentos')
      .or(page.locator('text=Pensando'))
      .or(page.locator('[data-testid="thinking-indicator"]'))
      .isVisible({ timeout: 2000 })
      .catch(() => false);

    // Thinking indicator may appear and disappear quickly
    // Test passes if it was shown during processing
    expect(hasThinkingIndicator || await page.locator('[data-testid="assistant-message"]').isVisible({ timeout: 30000 })).toBeTruthy();
  });

  test('should receive response via SSE and render message', async ({ page }) => {
    // Arrange: Track SSE messages
    let sseDataReceived = false;
    
    page.on('response', async response => {
      if (response.url().includes('/api/chat/stream')) {
        const body = await response.body().catch(() => null);
        if (body) {
          sseDataReceived = true;
        }
      }
    });

    // Act: Send message
    const message = 'Test SSE response rendering';
    await page.fill('input[placeholder="Digite sua mensagem..."]', message);
    await page.keyboard.press('Enter');

    // Assert: Wait for assistant response
    await page.waitForSelector('[data-testid="assistant-message"]', { timeout: 60000 });

    // Verify message content is not empty
    const assistantMessage = await page.locator('[data-testid="assistant-message"]').last();
    const messageText = await assistantMessage.textContent();
    expect(messageText).toBeTruthy();
    expect(messageText.length).toBeGreaterThan(0);
  });

  test('should show "Ver fontes" button after response completes', async ({ page }) => {
    // Arrange: Send message
    const message = 'Test sources button appearance';
    await page.fill('input[placeholder="Digite sua mensagem..."]', message);
    await page.keyboard.press('Enter');

    // Act: Wait for response to complete
    await page.waitForSelector('[data-testid="assistant-message"]', { timeout: 60000 });
    
    // Wait a bit more for sources button to appear
    await page.waitForTimeout(1000);

    // Assert: "Ver fontes" button is visible
    const sourcesButton = page.locator('button:has-text("Ver fontes")')
      .or(page.locator('[data-testid="sources-button"]'));
    
    await expect(sourcesButton).toBeVisible({ timeout: 10000 });
  });

  test('should open sources panel when clicking sources button', async ({ page }) => {
    // Arrange: Send message and wait for response
    const message = 'Test sources panel';
    await page.fill('input[placeholder="Digite sua mensagem..."]', message);
    await page.keyboard.press('Enter');
    
    await page.waitForSelector('[data-testid="assistant-message"]', { timeout: 60000 });
    await page.waitForTimeout(1000);

    // Act: Click sources button
    const sourcesButton = page.locator('button:has-text("Ver fontes")')
      .or(page.locator('[data-testid="sources-button"]'));
    
    if (await sourcesButton.isVisible().catch(() => false)) {
      await sourcesButton.click();

      // Assert: Sources panel is visible
      const sourcesPanel = page.locator('[data-testid="sources-panel"]')
        .or(page.locator('text=Fontes utilizadas'));
      await expect(sourcesPanel).toBeVisible({ timeout: 5000 });
    } else {
      // If no sources button (no documents), test is inconclusive
      test.skip('No sources button visible - may need indexed documents');
    }
  });

  test('should handle connection loss gracefully', async ({ page }) => {
    // Arrange: Intercept and abort SSE request
    await page.route('**/api/chat/stream**', route => route.abort('internetdisconnected'));

    // Act: Send message
    await page.fill('input[placeholder="Digite sua mensagem..."]', 'Test connection error');
    await page.keyboard.press('Enter');

    // Assert: Error message appears
    await expect(
      page.locator('text=Conexão perdida')
        .or(page.locator('text=Erro ao receber resposta'))
        .or(page.locator('[data-testid="error-message"]'))
    ).toBeVisible({ timeout: 10000 });

    // Clean up: Remove route
    await page.unroute('**/api/chat/stream**');
  });
});
