const { test, expect } = require('@playwright/test');

test.describe('Chat', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="text"]', 'localuser');
    await page.fill('input[type="password"]', 'localuser123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/chat');
  });

  test('should display chat page', async ({ page }) => {
    await page.goto('/chat');
    await expect(page).toHaveURL(/\/chat$/);
    await expect(page.locator('[data-testid="chat-container"]')).toBeVisible();
    await expect(page.locator('text=Nova Conversa')).toBeVisible();
  });

  test('should create new chat session', async ({ page }) => {
    await page.goto('/chat');
    
    await page.click('text=Nova Conversa');
    
    // Should show chat container
    await expect(page.locator('[data-testid="chat-container"]')).toBeVisible();
  });

  test('should show chat sessions in sidebar', async ({ page }) => {
    await page.goto('/chat');
    
    // Create multiple sessions
    await page.click('text=Nova Conversa');
    await page.waitForTimeout(500);
    
    // Should have at least one session
    const sessions = await page.locator('[data-testid="chat-session"]').count();
    expect(sessions).toBeGreaterThanOrEqual(1);
  });

  test('should require authentication', async ({ page }) => {
    await page.evaluate(() => localStorage.clear());
    await page.goto('/chat');
    await expect(page).toHaveURL(/\/login$/);
  });

  test('should send message and display it', async ({ page }) => {
    await page.goto('/chat');
    await page.click('text=Nova Conversa');
    
    const message = 'Olá, este é um teste';
    await page.fill('input[placeholder="Digite sua mensagem..."]', message);
    await page.keyboard.press('Enter');
    
    // User message should appear
    await expect(page.locator(`text=${message}`)).toBeVisible();
  });

  test('should show delete button on session hover', async ({ page }) => {
    await page.goto('/chat');
    await page.click('text=Nova Conversa');
    
    // Hover over session
    const session = page.locator('[data-testid="chat-session"]').first();
    await session.hover();
    
    // Delete button should be visible
    await expect(page.locator('[data-testid="delete-session"]').first()).toBeVisible();
  });
});
