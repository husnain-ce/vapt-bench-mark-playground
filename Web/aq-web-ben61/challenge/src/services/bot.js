const path = require('path');
const puppeteer = require('puppeteer');

async function visitUserWebsite(targetUrl, userDirCode) {
  const userDataDir = path.join('/tmp', userDirCode);
  const bot_username = process.env.BOT_USERNAME || 'superbot';
  const bot_pwd = process.env.BOT_PWD || 'superbot';
  process.env.HOME = "/tmp/";
  
  const args = [
    `--user-data-dir=${userDataDir}`,
    "--disable-dev-shm-usage",
    "--no-sandbox"
  ];

  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: "/usr/bin/google-chrome",
    args,
    ignoreDefaultArgs: ["--disable-client-side-phishing-detection", "--disable-component-update", "--force-color-profile=srgb"]
  });

  const page = await browser.newPage();
  page.setDefaultNavigationTimeout(15000);

  console.log("[BOT] - Bot is login into the app...");
  await page.goto("http://localhost:3000/login");
  await page.waitForSelector("[name=password]");
  await page.type("[name=username]", bot_username);
  await page.type("[name=password]", bot_pwd);
  await page.keyboard.press("Enter");
  console.log("[BOT] - Bot logged in !");
  await new Promise(r => setTimeout(r, 1000));

  try {
    console.log("[BOT] - Bot will check if the website can be scrapped");
    await page.goto(targetUrl);
    await browser.close();
  } finally {
    await browser.close();
  }
  return;
}

module.exports = { visitUserWebsite };