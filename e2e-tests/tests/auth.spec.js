const { test, expect } = require('@playwright/test');

test.describe('Authentication', () => {
  test('should login with valid credentials', async ({ page }) => {
    // Navigate to login
    await page.goto('/login');
    await expect(page).toHaveURL(/\/login$/);
    
    // Fill credentials
    await page.fill('input[type="text"]', 'localuser');
    await page.fill('input[type="password"]', 'localuser123');
    
    // Submit
    await page.click('button[type="submit"]');
    
    // Assert redirect to chat
    await page.waitForURL('**/chat');
    await expect(page).toHaveURL(/\/chat$/);
    
    // Assert token in localStorage
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeTruthy();
  });

  test('should show error with invalid credentials', async ({ page }) => {
    await page.goto('/login');
    
    // Fill invalid credentials
    await page.fill('input[type="text"]', 'wronguser');
    await page.fill('input[type="password"]', 'wrongpassword');
    
    await page.click('button[type="submit"]');
    
    // Assert error message (can be either the text or in error div)
    await expect(page.locator('[data-testid="login-error"]').or(page.locator('text=Erro ao fazer login'))).toBeVisible();
    
    // Assert still on login page
    await expect(page).toHaveURL(/\/login$/);
    
    // Assert no token
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeNull();
  });

  test('should redirect authenticated user from login', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[type="text"]', 'localuser');
    await page.fill('input[type="password"]', 'localuser123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/chat');
    
    // Try to access login again
    await page.goto('/login');
    
    // Should redirect to chat
    await expect(page).toHaveURL(/\/chat$/);
  });

  test('should logout successfully', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[type="text"]', 'localuser');
    await page.fill('input[type="password"]', 'localuser123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/chat');
    
    // Click logout
    await page.click('text=Sair');
    
    // Should redirect to login
    await page.waitForURL('**/login');
    await expect(page).toHaveURL(/\/login$/);
    
    // Token should be removed
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeNull();
  });
});
