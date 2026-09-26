#!/usr/bin/env node
/**
 * Build the README's GIFs from the example Lotties, in a real lottie-web.
 *
 *   node scripts/make-gifs.mjs                 every example, the hero and the palette board
 *   node scripts/make-gifs.mjs heart-like      one example
 *   node scripts/make-gifs.mjs --boards        only the hero, the palette board and the social card
 *
 * Needs ffmpeg on PATH, python3, and the npm devDependencies.
 *
 * Presentation rules, applied here rather than baked into the animations:
 *
 *   - Each example sits on the ground it was designed for (meta.tc).
 *   - An entrance starts on its first painted frame, because in a looping GIF
 *     the empty canvas it legitimately starts on is a flash on every repeat,
 *     and holds its final pose before repeating, or it reads as a twitch.
 *     A loop (the linter's rule: loop, loader, spinner, pulse, idle or cycle in
 *     the name) plays whole, and the frame that duplicates the first is dropped.
 *   - A board runs every cell on one clock, long enough for each cell to finish.
 */
import { execFileSync } from 'node:child_process';
import { mkdtempSync, rmSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { createRequire } from 'node:module';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import puppeteer from 'puppeteer-core';
import { resolveChrome, stageBlank } from './render.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const EXAMPLES = join(ROOT, 'examples');
const ASSETS = join(ROOT, 'assets');
const require = createRequire(import.meta.url);
const LOTTIE = readFileSync(require.resolve('lottie-web/build/player/lottie.min.js'), 'utf8');

const FPS = 30;
const HOLD = 0.9; // seconds an entrance rests on its final pose
const LOOP_WORDS = /loop|loader|loading|spinner|pulse|idle|cycle/i;

// The README's first image: eight examples on eight grounds, the dark ones on a diagonal.
const HERO = [
  'heart-like', 'location-ping', 'success-check', 'weather-sun',
  'typing-dots', 'toggle-switch', 'bouncing-ball', 'paper-plane',
];
// One animation in every palette.
const PALETTE_DEMO = 'success-check';

function python(args) {
  return execFileSync('python3', args, { cwd: ROOT, encoding: 'utf8' }).trim();
}

function load(file, label, extra = {}) {
  const data = JSON.parse(readFileSync(file, 'utf8'));
  const tc = data.meta && data.meta.tc;
  return {
    data,
    label,
    bg: /^#[0-9a-f]{3,8}$/i.test(tc || '') ? tc : '#F3EEE6',
    loop: LOOP_WORDS.test(`${data.nm || ''} ${file}`),
    ...extra,
  };
}

/**
 * Seconds per cycle, and the animation frame to show at a time on the board clock.
 * `cycle` stretches a one-shot's hold, so on a board it plays once per board loop
 * instead of being cut mid-move when the GIF wraps.
 */
function timing(cell, cycle) {
  const { ip, op, fr } = cell.data;
  if (cell.loop) {
    const span = op - ip;
    return { cycle: span / fr, frameAt: (s) => ip + ((Math.round(s * fr) % span) + span) % span };
  }
  const lead = cell.lead ?? ip;
  const length = Math.max(cycle ?? 0, (op - 1 - lead) / fr + HOLD);
  return { cycle: length, frameAt: (s) => Math.min(op - 1, lead + Math.round((s % length) * fr)) };
}

async function open(browser, cells, { cols, size, gap, pad, radius, bg, labels }) {
  const page = await browser.newPage();
  const rows = Math.ceil(cells.length / cols);
  await page.setViewport({
    width: cols * size + (cols - 1) * gap + 2 * pad,
    height: rows * size + (rows - 1) * gap + 2 * pad,
    deviceScaleFactor: 2,
  });
  await page.setContent(`<!doctype html><html><head><meta charset="utf-8"><style>
      html,body{margin:0;background:${bg}}
      .board{display:grid;grid-template-columns:repeat(${cols},${size}px);gap:${gap}px;
        padding:${pad}px;background:${bg};width:max-content}
      .cell{position:relative;width:${size}px;height:${size}px;border-radius:${radius}px;overflow:hidden}
      .anim{position:absolute;inset:0}
      .anim svg{display:block}
      .label{position:absolute;left:14px;bottom:12px;display:flex;align-items:center;gap:8px;
        font:600 11px/1 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.04em}
      .chip{width:9px;height:9px;border-radius:50%}
    </style></head><body><div class="board">${cells
      .map((cell, i) => `<div class="cell" style="background:${cell.bg}">
        <div class="anim" id="a${i}"></div>${labels && cell.label ? `<div class="label"
          style="color:${cell.chips ? cell.chips[2] : '#8A8178'}">${cell.label}${(cell.chips || [])
            .map((c) => `<span class="chip" style="background:${c}"></span>`).join('')}</div>` : ''}
      </div>`).join('')}</div></body></html>`, { waitUntil: 'domcontentloaded' });
  await page.addScriptTag({ content: LOTTIE });
  await page.evaluate(async (datas) => {
    window.anims = datas.map((data, i) => lottie.loadAnimation({ // eslint-disable-line no-undef
      container: document.getElementById(`a${i}`), renderer: 'svg', loop: false, autoplay: false, animationData: data,
    }));
    await Promise.all(window.anims.map((a) => new Promise((resolve) => {
      if (a.isLoaded) resolve(); else { a.addEventListener('DOMLoaded', resolve); setTimeout(resolve, 2000); }
    })));
    // A seek to the frame the player is parked on is a no-op; park them elsewhere.
    window.anims.forEach((a) => a.goToAndStop(Math.max(0, a.totalFrames - 1), true));
  }, cells.map((c) => c.data));
  return page;
}

async function seek(page, frames) {
  await page.evaluate(async (list) => {
    list.forEach((f, i) => window.anims[i].goToAndStop(f - window.anims[i].firstFrame, true));
    await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  }, frames);
}

/** The first frame of an entrance that paints anything, judged by its pixels. */
async function firstPainted(browser, cell) {
  const page = await open(browser, [cell], { cols: 1, size: 120, gap: 0, pad: 0, radius: 0, bg: cell.bg });
  try {
    const element = await page.$('.cell');
    const blank = await stageBlank(page, await page.$('#a0'), {});
    for (let f = cell.data.ip; f < cell.data.op; f += 1) {
      await seek(page, [f]);
      if (!Buffer.from(await element.screenshot()).equals(blank)) return f;
    }
    return cell.data.ip;
  } finally {
    await page.close();
  }
}

async function board(browser, cells, out, layout) {
  for (const cell of cells) {
    if (!cell.loop) cell.lead = await firstPainted(browser, cell);
    Object.assign(cell, timing(cell));
  }
  // Long enough for every cell to finish a cycle; boards stop at the longest, and
  // loops are authored to divide it. One-shots hold until the board wraps.
  const seconds = layout.seconds ?? Math.max(...cells.map((c) => c.cycle));
  for (const cell of cells) if (!cell.loop) Object.assign(cell, timing(cell, seconds));
  const count = Math.round(seconds * FPS);
  const page = await open(browser, cells, layout);
  const tmp = mkdtempSync(join(tmpdir(), 'lottie-gif-'));
  try {
    const element = await page.$('.board');
    for (let t = 0; t < count; t += 1) {
      await seek(page, cells.map((c) => c.frameAt(t / FPS)));
      await element.screenshot({ path: join(tmp, `f-${String(t).padStart(4, '0')}.png`) });
    }
    const width = layout.outWidth;
    execFileSync('ffmpeg', [
      '-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', join(tmp, 'f-%04d.png'),
      '-vf', `scale=${width}:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=${layout.colors ?? 128}:stats_mode=diff[p];` +
        '[b][p]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle',
      '-loop', '0', out,
    ], { stdio: ['ignore', 'pipe', 'pipe'] });
  } finally {
    rmSync(tmp, { recursive: true, force: true });
    await page.close();
  }
  const kb = Math.round(statSync(out).size / 1024);
  console.log(`  ${out.replace(`${ROOT}/`, '').padEnd(34)} ${String(count).padStart(3)} frames  ${kb} KB`);
}

async function social(browser, cells, out) {
  // A still for link previews (1280x640): most platforms will not play a GIF there.
  for (const cell of cells) Object.assign(cell, timing(cell));
  const page = await open(browser, cells, { cols: 3, size: 188, gap: 14, pad: 0, radius: 18, bg: '#F3EEE6' });
  // A loop a third of the way in; a one-shot on its final pose (just short of the wrap).
  await seek(page, cells.map((c) => c.frameAt(c.loop ? c.cycle * 0.3 : c.cycle - 1e-3)));
  const grid = await (await page.$('.board')).screenshot({ encoding: 'base64' });
  await page.setViewport({ width: 1280, height: 640, deviceScaleFactor: 1 });
  await page.setContent(`<!doctype html><html><head><meta charset="utf-8"><style>
      body{margin:0;width:1280px;height:640px;background:#F3EEE6;color:#1E1B18;display:flex;
        align-items:center;gap:56px;padding:0 72px;box-sizing:border-box;
        font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","Inter",system-ui,sans-serif}
      h1{font-size:76px;line-height:.95;letter-spacing:-.045em;margin:0 0 22px;font-weight:700}
      p{font-size:25px;line-height:1.35;color:#5E5750;margin:0;letter-spacing:-.01em;max-width:430px}
      small{display:block;margin-top:28px;font:600 14px/1 ui-monospace,Menlo,monospace;color:#8A8178;letter-spacing:.04em}
      img{width:592px;flex:none}
    </style></head><body><div><h1>Lottie<br>Animator</h1>
      <p>Motion that is looked at before it ships: converted, linted, rendered.</p>
      <small>A CLAUDE CODE SKILL</small></div>
      <img src="data:image/png;base64,${grid}"></body></html>`, { waitUntil: 'load' });
  await page.screenshot({ path: out });
  await page.close();
  console.log(`  ${out.replace(`${ROOT}/`, '')}`);
}

async function main() {
  const args = process.argv.slice(2);
  const boardsOnly = args.includes('--boards');
  const only = args.find((a) => !a.startsWith('--'));
  const names = readdirSync(EXAMPLES).filter((f) => f.endsWith('.json')).map((f) => f.slice(0, -5)).sort();
  if (only && !names.includes(only)) throw new Error(`no examples/${only}.json`);

  const executablePath = resolveChrome();
  if (!executablePath) throw new Error('no Chrome found; set CHROME_PATH');
  const browser = await puppeteer.launch({
    executablePath, headless: 'shell', args: ['--no-sandbox', '--force-color-profile=srgb'],
  });
  try {
    if (!boardsOnly) {
      console.log('examples');
      for (const name of only ? [only] : names) {
        const cell = load(join(EXAMPLES, `${name}.json`), name);
        await board(browser, [cell], join(ASSETS, `${name}.gif`),
          { cols: 1, size: 240, gap: 0, pad: 0, radius: 0, bg: cell.bg, outWidth: 240, colors: 96 });
      }
    }
    if (only) return;

    console.log('boards');
    const missing = [...HERO, PALETTE_DEMO].filter((n) => !names.includes(n));
    if (missing.length) throw new Error(`board examples missing: ${missing.join(', ')}`);
    // Framed for GitHub's light and dark canvases; the README picks one with <picture>.
    for (const [file, frame] of [['hero.gif', '#FFFFFF'], ['hero-dark.gif', '#0D1117']]) {
      const hero = HERO.map((n) => load(join(EXAMPLES, `${n}.json`), n));
      await board(browser, hero, join(ASSETS, file),
        { cols: 4, size: 200, gap: 12, pad: 12, radius: 18, bg: frame, outWidth: 872, colors: 192, seconds: 4 });
    }

    const palettes = JSON.parse(python(['-c',
      'import json,sys; sys.path.insert(0,"scripts"); from motion import PALETTES; print(json.dumps(PALETTES))']));
    const tmp = mkdtempSync(join(tmpdir(), 'lottie-palettes-'));
    try {
      const cells = Object.entries(palettes).map(([name, c]) => {
        const file = join(tmp, `${name}.json`);
        python([join('examples', `${PALETTE_DEMO}.py`), '--palette', name, '-o', file]);
        return load(file, name, { chips: [c.ink, c.accent, c.muted, c.support] });
      });
      await board(browser, cells, join(ASSETS, 'palettes.gif'),
        { cols: 3, size: 200, gap: 12, pad: 12, radius: 18, bg: '#FFFFFF', outWidth: 648, colors: 192, labels: true });
    } finally {
      rmSync(tmp, { recursive: true, force: true });
    }

    await social(browser, HERO.slice(0, 6).map((n) => load(join(EXAMPLES, `${n}.json`), n)),
      join(ASSETS, 'readme-hero.png'));
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(`make-gifs: ${error.message}`);
  process.exit(1);
});
