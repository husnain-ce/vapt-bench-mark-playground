const { chromium, firefox, webkit } = require("playwright");
const fs = require("fs");
const path = require("path");

const CONFIG = {
  DEBUG_TOKEN: process.env["DEBUG_TOKEN"],
  APPNAME: process.env["APPNAME"],
  APPURL: process.env["APPURL"],
  APPURLREGEX: process.env["APPURLREGEX"] || "^.*$",
  APPLIMITTIME: Number(process.env["APPLIMITTIME"]),
  APPLIMIT: Number(process.env["APPLIMIT"]),
  APPBROWSER: process.env["BROWSER"] || "chromium",
};

console.table(CONFIG);

function sleep(s) {
  return new Promise((resolve) => setTimeout(resolve, s));
}

const browserArgs = {
  headless: (() => {
    const is_x11_exists = fs.existsSync("/tmp/.X11-unix");
    if (process.env["DISPLAY"] !== undefined && is_x11_exists) {
      return false;
    }
    return true;
  })(),
  args: [
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--no-gpu",
    "--disable-default-apps",
    "--disable-translate",
    "--disable-device-discovery-notifications",
    "--disable-software-rasterizer",
    "--disable-xss-auditor",
  ],
  ignoreHTTPSErrors: true,
};

/** @type {import('playwright').Browser} */
let initBrowser = null;

async function getContext() {
  /** @type {import('playwright').BrowserContext} */
  let context = (await chromium.launch(browserArgs)).newContext();
  return context;
}

console.log("Bot started...");

module.exports = {
  name: CONFIG.APPNAME,
  urlRegex: CONFIG.APPURLREGEX,
  rateLimit: {
    windowMs: CONFIG.APPLIMITTIME,
    limit: CONFIG.APPLIMIT,
  },
  bot: async (urlToVisit) => {
    const context = await getContext();
    try {
      const page = await context.newPage();
      await context.addCookies([
        {
          name: "debugtoken",
          httpOnly: false,
          value: CONFIG.DEBUG_TOKEN,
          url: CONFIG.APPURL,
        },
      ]);

      console.log(`bot visiting ${urlToVisit}`);
      await page.goto(urlToVisit, {
        waitUntil: "load",
        timeout: 10 * 1000,
      });
      await sleep(15000);

      console.log("browser close...");
      return true;
    } catch (e) {
      console.error(e);
      return false;
    } finally {
      await context.close();
    }
  },
};
