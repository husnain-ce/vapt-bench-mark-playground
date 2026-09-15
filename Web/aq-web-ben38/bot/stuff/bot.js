#!/usr/bin/env node
const puppeteer = require('puppeteer')
const flag = process.env.FLAG ?? 'ASIS{test-flag}'

async function sleep(n){
	return new Promise((r)=>setTimeout(r,n))
}

async function visit(url){
	let browser
	try {
		browser = await puppeteer.launch({
		    browser: 'firefox',
		    executablePath: "/opt/firefox/firefox",
		    headless: true
		})

		let page = await browser.newPage()
		// Restrict connections to ports between 10000-65535
		// This isn't related to the intended solution
		try{
			await page.goto('about:config',{timeout: 500})
		} catch {}
		await page.click('#warningButton')
		await sleep(200)
		await page.type('#about-config-search', 'network.security.ports.banned');
		await sleep(200)
		await page.click('input[value="String"]')
		await sleep(200)
		await page.click('button[data-l10n-id="about-config-pref-add-button"]')
		await sleep(200)
		await page.type('input[aria-label="network.security.ports.banned"]', '10000-65535')
		await sleep(200)
		await page.click('button[data-l10n-id="about-config-pref-save-button"]')
		await sleep(500)
		await page.close()
		page = await browser.newPage();
		await page.goto('https://web/')
		await page.setCookie({
			httpOnly: false,
			name: 'flag',
			value: flag,
			sameSite: 'Lax',
			secure: true
		})
		await page.close()
		page = await browser.newPage()
		await page.goto(url, {timeout: 2000, waitUntil: 'domcontentloaded'})
		await new Promise((r)=>setTimeout(r,3000))
		await page.close()
	} catch(e) {
		console.log(e)
	}
	try{ await browser.close() } catch {}
}

visit(JSON.parse(process.argv[2]))
