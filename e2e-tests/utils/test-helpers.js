async function login(page, username, password) {
  await page.goto('/login');
  await page.fill('input[type="text"]', username);
  await page.fill('input[type="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForURL('**/chat');
}

async function logout(page) {
  await page.click('text=Sair');
  await page.waitForURL('**/login');
}

async function uploadFile(page, filePath) {
  await page.goto('/documents');
  const input = await page.locator('input[type="file"]');
  await input.setInputFiles(filePath);
  await page.waitForSelector('text=completed', { timeout: 30000 });
}

async function createChatSession(page) {
  await page.goto('/chat');
  await page.click('text=Nova Conversa');
  await page.waitForSelector('.chat-container');
}

module.exports = {
  login,
  logout,
  uploadFile,
  createChatSession,
};
