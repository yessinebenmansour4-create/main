// Dump the virtual camera (#cam / #shake transforms) for every master frame, so the AI
// restoration only processes the part of each frame that is actually on screen.
// Usage: node scripts/export_camera.mjs <puppeteer-core dir> <chrome binary> <out.json>
import { createRequire } from "module";
import path from "path";
import { fileURLToPath } from "url";

const [pptrDir, chrome, out] = process.argv.slice(2);
const require = createRequire(import.meta.url);
const puppeteer = require(pptrDir);
const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));

const browser = await puppeteer.launch({ executablePath: chrome, args: ["--no-sandbox", "--allow-file-access-from-files"] });
const page = await browser.newPage();
await page.evaluateOnNewDocument(() => { window.__timelines = {}; });
await page.goto("file://" + path.join(root, "index.html"), { waitUntil: "load" });
const frames = await page.evaluate(() => {
  const tl = window.__timelines.main, g = window.gsap, res = [];
  for (let n = 0; n < 1167; n++) {
    tl.seek(n / 30, false);
    res.push([n, g.getProperty("#cam", "x"), g.getProperty("#cam", "y"), g.getProperty("#cam", "scale"),
              g.getProperty("#shake", "x"), g.getProperty("#shake", "y")]);
  }
  return res;
});
(await import("fs")).writeFileSync(out, JSON.stringify(frames));
console.log(`camera frames: ${frames.length}`);
await browser.close();
