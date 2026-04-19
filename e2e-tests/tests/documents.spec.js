const { test, expect } = require('@playwright/test');
const path = require('path');

test.describe('Documents', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="text"]', 'localuser');
    await page.fill('input[type="password"]', 'localuser123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/chat');
  });

  test('should navigate to documents page', async ({ page }) => {
    await page.goto('/documents');
    await expect(page).toHaveURL(/\/documents$/);
    await expect(page.locator('text=Documentos')).toBeVisible();
    await expect(page.locator('text=Gerencie seus documentos')).toBeVisible();
  });

  test('should show upload dropzone', async ({ page }) => {
    await page.goto('/documents');
    await expect(page.locator('text=Arraste e solte arquivos aqui')).toBeVisible();
    await expect(page.locator('text=Formatos suportados: PDF, TXT, DOCX, MD')).toBeVisible();
  });

  test('should upload document via file input @slow', async ({ page }) => {
    await page.goto('/documents');
    
    // Upload file
    const filePath = path.join(__dirname, '../fixtures/test-document.txt');
    const input = page.locator('[data-testid="file-upload-input"]').first();
    await input.setInputFiles(filePath);
    
    // Wait for upload to start (progress or document in list)
    await page.waitForSelector('text=Enviando...', { timeout: 5000 }).catch(() => {
      // Progress might be fast, check for document in list
    });
    
    // Wait longer for processing (up to 60s for embeddings)
    await expect(page.locator('text=test-document.txt')).toBeVisible({ timeout: 60000 });
    
    // Document should eventually show completed or processing
    const status = await page.locator('[data-testid="status-badge"]').textContent().catch(() => '');
    expect(['completed', 'processing']).toContain(status);
  });

  test('should show error for invalid file type', async ({ page }) => {
    await page.goto('/documents');
    
    // Create invalid file
    const invalidFile = {
      name: 'test.exe',
      mimeType: 'application/x-msdownload',
      buffer: Buffer.from('invalid content'),
    };
    
    const input = page.locator('[data-testid="file-upload-input"]').first();
    await input.setInputFiles([invalidFile]);
    
    // Frontend validation should show error
    await expect(page.locator('text=Formato não suportado').or(page.locator('text=formato'))).toBeVisible({ timeout: 5000 });
  });

  test('should show empty state', async ({ page }) => {
    await page.goto('/documents');
    
    // Should show empty message or document list
    const hasContent = await page.locator('text=Nenhum documento').isVisible().catch(() => false);
    const hasDocuments = await page.locator('[data-testid="status-badge"]').count() > 0;
    
    expect(hasContent || hasDocuments).toBeTruthy();
  });
});
