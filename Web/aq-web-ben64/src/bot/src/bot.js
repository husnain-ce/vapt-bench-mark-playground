// Force puppeteer to store everything to /tmp/
process.env.HOME = "/tmp";

const { delay, handleTargetCreated, handleTargetDestroyed, logMainInfo, logMainError } = require("./utils");
const puppeteer = require("puppeteer");

// Banner
const tips = ["Every console.log usage on the bot will be sent back to you :)", "There is a small race window (~10ms) when a new tab is opened where console.log won't return output :("];
console.log(`==========\nTips: ${tips[Math.floor(Math.random() * tips.length)]}\n==========`);

// Spawn the bot and navigate to the user provided link.
async function goto(html) {
	logMainInfo("Starting the browser...");
	const browser = await puppeteer.launch({
		headless: "new",
		ignoreHTTPSErrors: true,
		args: [
			"--no-sandbox",
			"--disable-gpu",
			"--disable-jit",
			"--disable-wasm",
			"--disable-dev-shm-usage",
		],
		executablePath: "/usr/bin/chromium-browser"
	});

	// Hook tabs events
	browser.on("targetcreated", handleTargetCreated.bind(browser));
	browser.on("targetdestroyed", handleTargetDestroyed.bind(browser));

	/* ** CHALLENGE LOGIC ** */
	const [page] = await browser.pages(); // Reuse the page created by the browser.
	await handleTargetCreated(page.target()); // Since it was created before the event listener was set, we need to hook it up manually.
	await page.setDefaultNavigationTimeout(5000);

	logMainInfo("Going to the app...");
	await browser.setCookie({
		name: "flag",
		value: process.env.FLAG,
		domain: "under-the-beamers-app.internal:5000",
		path: "/",
		httpOnly: false
	});

	logMainInfo("Going to the user provided link...");
	try { await page.goto(`http://under-the-beamers-app.internal:5000/?html=${encodeURIComponent(html)}`) } catch {}
	await delay(2000);

	logMainInfo("Leaving o/");
	await browser.close();
	return;
}

// Handle TCP data
process.stdin.on("data", (data) => {
	const html = data.toString().trim();

	if (!html || html.length > 500) {
		logMainError("You provided an invalid HTML. It should be a non empty string with a length of less than 500 characters.");
		process.exit(1);
	}

	goto(html)
	.then(() => process.exit(0))
	.catch((error) => {
		if (process.env.ENVIRONMENT === "development") {
			console.error(error);
		}
		process.exit(1);
	});
});