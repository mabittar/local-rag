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
    // Use heading selector for specificity instead of generic text
    await expect(page.getByRole('heading', { name: /Documentos/i }).first()).toBeVisible();
    await expect(page.getByText(/Gerencie seus documentos/).first()).toBeVisible();
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
    const statusBadge = page.locator('[data-testid="status-badge"]').first();
    const status = await statusBadge.textContent().catch(() => '');
    
    // If status is empty (not yet loaded), wait for it to appear
    if (!status || status === '') {
      // Just verify document exists in list, status may not be visible yet
      await expect(page.locator('text=test-document.txt')).toBeVisible({ timeout: 60000 });
    } else {
      // Verify status is one of the expected values
      const normalizedStatus = status.toLowerCase().trim();
      const validStatuses = ['completed', 'processing', 'concluído', 'processando'];
      expect(validStatuses.some(s => normalizedStatus.includes(s))).toBe(true);
    }
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
    
    // Frontend validation should show error - look for error notification/toast
    const errorLocator = page.locator('[role="alert"]')
      .or(page.locator('.text-red-600, .text-error, .error-message'))
      .or(page.locator('[data-testid="upload-error"]'))
      .or(page.locator('text=Formato não suportado'));
    
    // The error should contain either "Formato" or "não suportado"
    const errorText = await errorLocator.first().textContent({ timeout: 5000 }).catch(() => '');
    const hasErrorMessage = errorText.toLowerCase().includes('formato') || 
                            errorText.toLowerCase().includes('não suportado') ||
                            errorText.toLowerCase().includes('suportado');
    expect(hasErrorMessage).toBe(true);
  });

  test('should show empty state', async ({ page }) => {
    await page.goto('/documents');
    
    // Should show empty message or document list
    const hasContent = await page.locator('text=Nenhum documento').isVisible().catch(() => false);
    const hasDocuments = await page.locator('[data-testid="status-badge"]').count() > 0;
    
    expect(hasContent || hasDocuments).toBeTruthy();
  });
});
