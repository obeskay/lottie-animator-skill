#!/usr/bin/env node
/**
 * Render a Lottie file to PNG frames and a labelled contact sheet.
 *
 * This is what turns "the JSON parses" into "I have seen the animation".
 * The linter catches structure; only a render catches a hero that never
 * appears, a loop that jumps, or motion that leaves the canvas.
 *
 *   node scripts/render.mjs examples/panda-loader.json
 *   node scripts/render.mjs a.json --at 0,50,100 --out /tmp/shots
 *   node scripts/render.mjs a.json --frames 0,12,24 --bg "#0b0f19"
 *
 * Requires `npm install` (puppeteer-core + lottie-web) and a local Chrome.
 */
import { createRequire } from 'node:module';
import { mkdir, readFile, writeFile, rm } from 'node:fs/promises';
import { existsSync, realpathSync } from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { pathToFileURL } from 'node:url';

const require = createRequire(import.meta.url);

const CHROME_CANDIDATES = [
  process.env.PUPPETEER_EXECUTABLE_PATH,
  process.env.CHROME_PATH,
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Chromium.app/Contents/MacOS/Chromium',
  '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
  '/usr/bin/google-chrome',
  '/usr/bin/google-chrome-stable',
  '/usr/bin/chromium',
  '/usr/bin/chromium-browser',
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
];

function fail(message, hint) {
  console.error(`render: ${message}`);
  if (hint) console.error(`  ${hint}`);
  process.exit(2);
}

function parseArgs(argv) {
  const opts = {
    at: [0, 25, 50, 75, 100],
    frames: null,
    out: null,
    bg: null,
    scale: 1,
    width: null,
    strip: true,
    keepFrames: true,
    onion: false,
  };
  const positional = [];
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    const value = () => {
      const next = argv[i + 1];
      if (next === undefined) fail(`${arg} needs a value`);
      i += 1;
      return next;
    };
    switch (arg) {
      case '--at':
        opts.at = value().split(',').map(Number);
        break;
      case '--frames':
        opts.frames = value().split(',').map(Number);
        break;
      case '--out':
        opts.out = value();
        break;
      case '--bg':
        opts.bg = value();
        break;
      case '--scale':
        opts.scale = Number(value());
        break;
      case '--width':
        opts.width = Number(value());
        break;
      case '--no-strip':
        opts.strip = false;
        break;
      case '--strip-only':
        opts.keepFrames = false;
        break;
      case '--onion':
        opts.onion = true;
        break;
      case '-h':
      case '--help':
        console.log(HELP);
        process.exit(0);
        break;
      default:
        if (arg.startsWith('-')) fail(`unknown option ${arg}`);
        positional.push(arg);
    }
  }
  if (positional.length !== 1) fail('expected exactly one Lottie JSON path', HELP);
  if (opts.onion && !opts.frames && !argv.includes('--at')) {
    opts.at = Array.from({ length: 12 }, (_, i) => (i * 100) / 11);
  }
  opts.input = positional[0];
  return opts;
}

const HELP = `Usage: node scripts/render.mjs <file.json> [options]

  --at A,B,C      timeline percentages to capture (default 0,25,50,75,100)
  --frames A,B,C  explicit frame numbers (overrides --at)
  --out DIR       output directory (default .lottie-preview/<name>)
  --bg VALUE      checker | transparent | any CSS color (default: the file's
                  meta.tc, the ground it was designed on, else checker)
  --width N       render width in px (default the composition width)
  --scale N       device pixel ratio (default 1)
  --no-strip      skip the contact sheet
  --strip-only    write only the contact sheet, not the individual frames
  --onion         also write onion.png: sampled frames stacked, oldest faintest.
                  Spacing between ghosts is the easing; their path is the arc.
                  Samples 12 frames unless --at or --frames is given.`;

export function resolveChrome() {
  for (const candidate of CHROME_CANDIDATES) {
    if (candidate && existsSync(candidate)) return candidate;
  }
  return null;
}

export function backgroundCss(bg) {
  if (bg === 'transparent') return 'background:transparent';
  if (bg === 'checker') {
    // A checkerboard makes transparent regions obvious instead of guessable.
    return `background-color:#ffffff;background-image:
      linear-gradient(45deg,#d9dde5 25%,transparent 25%),
      linear-gradient(-45deg,#d9dde5 25%,transparent 25%),
      linear-gradient(45deg,transparent 75%,#d9dde5 75%),
      linear-gradient(-45deg,transparent 75%,#d9dde5 75%);
      background-size:16px 16px;
      background-position:0 0,0 8px,8px -8px,-8px 0`;
  }
  return `background:${bg}`;
}

async function main() {
  const opts = parseArgs(process.argv.slice(2));

  let puppeteer;
  let lottiePath;
  try {
    puppeteer = (await import('puppeteer-core')).default;
    lottiePath = require.resolve('lottie-web/build/player/lottie.min.js');
  } catch {
    fail(
      'missing dependencies',
      'Run `npm install` in the repository root (installs puppeteer-core and lottie-web).',
    );
  }

  const executablePath = resolveChrome();
  if (!executablePath) {
    fail(
      'no Chrome/Chromium found',
      'Install Chrome, or set CHROME_PATH to the browser executable.',
    );
  }

  const inputPath = path.resolve(opts.input);
  let animation;
  try {
    animation = JSON.parse(await readFile(inputPath, 'utf8'));
  } catch (error) {
    fail(`cannot read ${opts.input}: ${error.message}`);
  }

  // A generator records the ground it designed for in meta.tc; judge the art on
  // it unless asked otherwise. Only a plain hex colour is trusted into the CSS.
  const themeColor = animation.meta && animation.meta.tc;
  if (!opts.bg) opts.bg = /^#[0-9a-f]{3,8}$/i.test(themeColor || '') ? themeColor : 'checker';

  const ip = Number(animation.ip ?? 0);
  const op = Number(animation.op ?? 0);
  const fr = Number(animation.fr ?? 30);
  if (!(op > ip) || !(fr > 0)) {
    fail('composition has no valid time range (check ip, op, fr)');
  }

  const lastFrame = op - 1;
  const frames = opts.frames
    ? opts.frames.map((f) => clamp(f, ip, lastFrame))
    : opts.at.map((pct) => clamp(ip + ((op - ip) * pct) / 100, ip, lastFrame));

  const compWidth = Number(animation.w) || 512;
  const compHeight = Number(animation.h) || 512;
  const width = opts.width || compWidth;
  const height = Math.round((width / compWidth) * compHeight);

  const outDir = opts.out
    ? path.resolve(opts.out)
    : path.resolve('.lottie-preview', path.basename(inputPath, '.json'));
  await mkdir(outDir, { recursive: true });

  const lottieSource = await readFile(lottiePath, 'utf8');

  const browser = await puppeteer.launch({
    executablePath,
    headless: 'shell',
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--force-color-profile=srgb'],
  });

  const results = [];
  try {
    const page = await browser.newPage();
    await page.setViewport({ width, height, deviceScaleFactor: opts.scale });
    const pageErrors = [];
    page.on('pageerror', (error) => pageErrors.push(String(error)));

    await page.setContent(
      `<!doctype html><html><head><meta charset="utf-8"><style>
        html,body{margin:0;padding:0;${backgroundCss(opts.onion ? 'transparent' : opts.bg)}}
        #stage{width:${width}px;height:${height}px}
        #stage svg{display:block}
      </style></head><body><div id="stage"></div></body></html>`,
      { waitUntil: 'domcontentloaded' },
    );
    await page.addScriptTag({ content: lottieSource });

    const loaded = await page.evaluate(async (data) => {
      // eslint-disable-next-line no-undef
      if (typeof lottie === 'undefined') return 'lottie-web failed to load';
      try {
        // eslint-disable-next-line no-undef
        window.__anim = lottie.loadAnimation({
          container: document.getElementById('stage'),
          renderer: 'svg',
          loop: false,
          autoplay: false,
          animationData: data,
        });
        // The SVG tree is built asynchronously. Seeking before DOMLoaded
        // captures an empty document on the first frame.
        await new Promise((resolve) => {
          if (window.__anim.isLoaded) return resolve();
          window.__anim.addEventListener('DOMLoaded', resolve);
          setTimeout(resolve, 2000);
        });
        // Seeking to the frame the player is already parked on is a no-op, so
        // asking for frame 0 first would never paint. Park it elsewhere.
        window.__anim.goToAndStop(Math.max(0, (data.op || 1) - 1), true);
        return null;
      } catch (error) {
        return String(error);
      }
    }, animation);
    if (loaded) fail(`lottie-web could not load the animation: ${loaded}`);

    const stage = await page.$('#stage');
    const shot = { omitBackground: opts.onion || opts.bg === 'transparent' };
    // What the stage looks like with nothing on it. A frame that matches it
    // pixel for pixel is empty, whatever the DOM holds: a layer hidden behind
    // its track matte still has geometry, and so does the matte itself.
    const blank = await stageBlank(page, stage, shot);
    for (const frame of frames) {
      await page.evaluate(seekFrame, frame);
      const drawn = await page.evaluate(inspectFrame, '#stage svg');
      if (drawn.error) fail(`could not inspect frame ${frame}: ${drawn.error}`);

      const label = `frame-${String(Math.round(frame)).padStart(4, '0')}`;
      const file = path.join(outDir, `${label}.png`);
      const png = await stage.screenshot({ path: file, ...shot });
      if (Buffer.from(png).equals(blank)) Object.assign(drawn, { painted: 0, coverage: 0, clipped: false, offCanvas: false });
      results.push({
        frame: Math.round(frame),
        time: ((frame - ip) / fr).toFixed(3),
        file,
        ...drawn,
      });
    }

    if (opts.onion) {
      const onionPath = path.join(outDir, 'onion.png');
      await renderOnion(page, results, { width, height, bg: opts.bg, name: animation.nm || path.basename(inputPath) });
      await page.screenshot({ path: onionPath, fullPage: true });
      results.onion = onionPath;
    }

    if (opts.strip) {
      const stripPath = path.join(outDir, 'filmstrip.png');
      await renderStrip(page, results, { width, height, bg: opts.bg, name: animation.nm || path.basename(inputPath) });
      await page.screenshot({ path: stripPath, fullPage: true });
      results.strip = stripPath;
    }

    if (pageErrors.length) {
      console.error('render: the player reported errors:');
      for (const error of pageErrors) console.error(`  ${error}`);
    }

    if (!opts.keepFrames) {
      await Promise.all(results.map((r) => rm(r.file, { force: true })));
    }
  } finally {
    await browser.close();
  }

  report(results, outDir, opts);
}

/**
 * A screenshot of the element with its content hidden: the empty frame, pixel
 * for pixel, on whatever ground surrounds it.
 */
export async function stageBlank(page, element, shot = {}) {
  await element.evaluate((el) => { el.style.visibility = 'hidden'; });
  const png = await element.screenshot(shot);
  await element.evaluate((el) => { el.style.visibility = ''; });
  return Buffer.from(png);
}

/**
 * Runs inside the page. Seeks to a frame and lets the renderer flush.
 * lottie-web builds its SVG lazily, so measuring in the same tick as the seek
 * reads a stale document.
 */
async function seekFrame(frame) {
  window.__anim.goToAndStop(frame, true);
  await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
}

/**
 * Runs inside the page. Reports what is actually on screen using the same
 * layout Chrome uses for the screenshot, so the numbers and the picture agree.
 */
export function inspectFrame(selector) {
  const svg = document.querySelector(selector);
  if (!svg) return { error: 'no SVG was rendered' };
  const stage = svg.getBoundingClientRect();
  if (!stage.width || !stage.height) return { error: 'the stage has no size' };

  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  let painted = 0;

  for (const node of svg.querySelectorAll('path,rect,circle,ellipse,image,text')) {
    // Matte and mask geometry is a stencil, not paint.
    if (node.closest('defs,mask,clipPath')) continue;
    const rect = node.getBoundingClientRect();
    if (!rect.width && !rect.height) continue;
    // Skip nodes that occupy space but paint nothing: no paint, or faded out by
    // their own opacity or any ancestor's (layer and group opacity live there).
    const hasFill = node.getAttribute('fill') && node.getAttribute('fill') !== 'none';
    const hasStroke = node.getAttribute('stroke') && node.getAttribute('stroke') !== 'none';
    const fillOpacity = Number(node.getAttribute('fill-opacity') ?? 1);
    const strokeOpacity = Number(node.getAttribute('stroke-opacity') ?? 1);
    let inherited = 1;
    for (let el = node; el && el !== svg; el = el.parentElement) {
      inherited *= Number(getComputedStyle(el).opacity);
    }
    if (inherited <= 0.01) continue;
    if (!((hasFill && fillOpacity > 0.01) || (hasStroke && strokeOpacity > 0.01))) continue;
    painted += 1;
    const box = paintedBox(node, rect, hasStroke);
    minX = Math.min(minX, box[0] - stage.x);
    minY = Math.min(minY, box[1] - stage.y);
    maxX = Math.max(maxX, box[2] - stage.x);
    maxY = Math.max(maxY, box[3] - stage.y);
  }

  /**
   * The box of what a path actually covers. getBoundingClientRect() boxes the
   * element's local bounding box after transforming it, so a circle rotated 45
   * degrees reports a square 1.41 times wider than the circle: a spinning ring
   * was flagged as clipped on every frame that was not a quarter turn. Walking
   * the outline through the screen matrix measures the shape itself.
   */
  function paintedBox(node, rect, hasStroke) {
    const fallback = [rect.left, rect.top, rect.right, rect.bottom];
    if (typeof node.getTotalLength !== 'function') return fallback;
    const matrix = node.getScreenCTM();
    const length = node.getTotalLength();
    if (!matrix || !(length > 0)) return fallback;
    const samples = Math.min(160, Math.max(24, Math.ceil(length / 3)));
    let x0 = Infinity; let y0 = Infinity; let x1 = -Infinity; let y1 = -Infinity;
    for (let k = 0; k <= samples; k += 1) {
      const point = node.getPointAtLength((length * k) / samples);
      const x = matrix.a * point.x + matrix.c * point.y + matrix.e;
      const y = matrix.b * point.x + matrix.d * point.y + matrix.f;
      x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y);
    }
    const width = hasStroke ? Number(node.getAttribute('stroke-width') ?? 1) : 0;
    const pad = (width / 2) * Math.sqrt(Math.abs(matrix.a * matrix.d - matrix.b * matrix.c));
    return [x0 - pad, y0 - pad, x1 + pad, y1 + pad];
  }

  if (!painted) return { painted: 0, coverage: 0, bbox: null, clipped: false, offCanvas: false };

  const bbox = [minX, minY, maxX, maxY].map((n) => Math.round(n));
  const coverage = ((maxX - minX) * (maxY - minY)) / (stage.width * stage.height);
  return {
    painted,
    coverage: Math.min(coverage, 1),
    bbox,
    // Content that runs past an edge is being cropped by the canvas.
    clipped: minX < -0.5 || minY < -0.5 || maxX > stage.width + 0.5 || maxY > stage.height + 0.5,
    offCanvas: maxX <= 0 || maxY <= 0 || minX >= stage.width || minY >= stage.height,
  };
}

async function renderStrip(page, results, { width, height, bg, name }) {
  const images = [];
  for (const result of results) {
    images.push({
      src: `data:image/png;base64,${(await readFile(result.file)).toString('base64')}`,
      caption: `frame ${result.frame} · ${result.time}s · ${result.painted} shapes`,
      painted: result.painted > 0,
      clipped: result.clipped,
      offCanvas: result.offCanvas,
    });
  }
  const cellWidth = Math.min(width, 320);
  await page.setViewport({
    width: Math.max(360, images.length * (cellWidth + 16) + 32),
    height: Math.round((cellWidth / width) * height) + 96,
    deviceScaleFactor: 1,
  });
  await page.setContent(
    `<!doctype html><html><head><meta charset="utf-8"><style>
      body{margin:0;padding:16px;background:#141210;color:#d8d0c3;
        font:12px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace}
      h1{font-size:13px;margin:0 0 12px;font-weight:600}
      .row{display:flex;gap:16px;align-items:flex-start}
      figure{margin:0}
      .frame{width:${cellWidth}px;${backgroundCss(bg)};border:1px solid #2e2a26;border-radius:4px;overflow:hidden}
      .frame img{display:block;width:100%}
      figcaption{margin-top:6px;color:#8a8178}
      .empty{color:#f59e0b}
    </style></head><body>
      <h1>${escapeHtml(name)}</h1>
      <div class="row">${images
        .map(
          (image) => `<figure><div class="frame"><img src="${image.src}"></div>
            <figcaption>${escapeHtml(image.caption)}${
              !image.painted ? '<br><span class="empty">EMPTY FRAME</span>' : ''
            }${image.offCanvas ? '<br><span class="empty">off canvas</span>' : ''}${
              image.clipped && !image.offCanvas ? '<br><span class="empty">clipped</span>' : ''
            }
            </figcaption></figure>`,
        )
        .join('')}</div></body></html>`,
    { waitUntil: 'domcontentloaded' },
  );
}

async function renderOnion(page, results, { width, height, bg, name }) {
  const n = results.length;
  const layers = [];
  for (let i = 0; i < n; i += 1) {
    const src = `data:image/png;base64,${(await readFile(results[i].file)).toString('base64')}`;
    // Quadratic ramp: the last pose reads solid, early ones stay legible but quiet.
    const opacity = n === 1 ? 1 : 0.1 + 0.9 * (i / (n - 1)) ** 2;
    layers.push(`<img src="${src}" style="opacity:${opacity.toFixed(3)}">`);
  }
  await page.setViewport({ width: width + 32, height: height + 72, deviceScaleFactor: 1 });
  await page.setContent(
    `<!doctype html><html><head><meta charset="utf-8"><style>
      body{margin:0;padding:16px;background:#141210;color:#d8d0c3;
        font:12px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace}
      h1{font-size:13px;margin:0 0 12px;font-weight:600}
      .stage{position:relative;width:${width}px;height:${height}px;${backgroundCss(bg)};border-radius:4px;overflow:hidden}
      .stage img{position:absolute;inset:0;width:100%;height:100%}
      p{margin:8px 0 0;color:#8a8178}
    </style></head><body>
      <h1>${escapeHtml(name)} · onion skin</h1>
      <div class="stage">${layers.join('')}</div>
      <p>${n} frames, frame ${results[0].frame} faintest to ${results[n - 1].frame} solid</p>
    </body></html>`,
    { waitUntil: 'domcontentloaded' },
  );
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

function clamp(value, low, high) {
  return Math.max(low, Math.min(high, value));
}

function report(results, outDir, opts) {
  const empty = results.filter((r) => r.painted === 0);
  for (const result of results) {
    const flags = [];
    if (result.painted === 0) flags.push('EMPTY');
    if (result.offCanvas) flags.push('entirely off canvas');
    else if (result.clipped) flags.push('clipped by canvas');
    console.log(
      `  frame ${String(result.frame).padStart(4)}  ${result.time}s  ` +
        `${String(result.painted).padStart(3)} shapes  ` +
        `${(result.coverage * 100).toFixed(0)}% of canvas` +
        `${flags.length ? `  <- ${flags.join(', ')}` : ''}`,
    );
  }
  if (results.onion) console.log(`\nonion skin: ${results.onion}`);
  if (results.strip) console.log(`${results.onion ? '' : '\n'}filmstrip: ${results.strip}`);
  else console.log(`\nframes in: ${outDir}`);

  if (empty.length === results.length) {
    console.error('\nrender: every sampled frame is empty. The file loads but shows nothing.');
    process.exitCode = 1;
  } else if (empty.length) {
    console.error(`\nrender: ${empty.length} of ${results.length} sampled frames paint nothing.`);
  }
  console.log('\nNow look at the filmstrip. Check the hero reads, the loop closes, and nothing clips.');
}

// Importable: make-gifs.mjs reuses the browser setup and the frame inspection.
// Compare real paths: run through the skill's symlink, argv[1] is the link and
// import.meta.url the file it points to, and main() would silently never run.
if (process.argv[1] && import.meta.url === pathToFileURL(realpathSync(process.argv[1])).href) {
  main().catch((error) => {
    console.error(`render: ${error.stack || error}`);
    process.exit(2);
  });
}
