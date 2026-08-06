#!/usr/bin/env node
/**
 * Build the README's animated GIFs from the example Lotties, using this
 * repository's own renderer.
 *
 *   node scripts/make-gifs.mjs                 # all examples -> assets/
 *   node scripts/make-gifs.mjs panda-loader    # just one
 *
 * Needs ffmpeg on PATH (brew install ffmpeg) plus the npm devDependencies.
 *
 * Two presentation rules make a loop read well in a README, and both are
 * applied here rather than baked into the animations:
 *
 *   - Leading empty frames are dropped. An entrance animation legitimately
 *     starts on an empty canvas, but in a looping GIF that blank frame is a
 *     flash on every repeat.
 *   - A hold is appended so the settled state is legible before the loop
 *     restarts. Without it an entrance reads as a twitch.
 */
import { execFileSync, spawnSync } from 'node:child_process';
import { mkdtempSync, rmSync, readdirSync, readFileSync, copyFileSync, mkdirSync, statSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, basename, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const OUT_DIR = join(ROOT, 'assets');

/** Presentation per example: background, frame stride, output width, tail hold (seconds). */
const PRESETS = {
  'rocket-launch': { bg: '#0d1117', step: 2, width: 280, hold: 0.6 },
  'logo-draw-on': { bg: '#0d1117', step: 2, width: 280, hold: 0.6 },
  'shape-morph': { bg: '#0d1117', step: 2, width: 280, hold: 0 },
  // The panda is a black-and-white character: on the dark card its chest and
  // ears disappear into the background. It gets a light card, deliberately.
  'panda-loader': { bg: '#f6f8fa', step: 2, width: 280, hold: 0 },
};

function sh(cmd, args, opts = {}) {
  return execFileSync(cmd, args, { cwd: ROOT, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], ...opts });
}

/**
 * Is this frame a single flat colour? The luma spread across the frame is the
 * cheapest reliable signal: a rendered shape always moves YMIN or YMAX away
 * from the background, an empty canvas cannot.
 */
function isFlat(png) {
  // ffmpeg writes filter metadata to stderr, not stdout — read the right stream
  // or every frame silently looks non-empty.
  const { stderr } = spawnSync(
    'ffmpeg',
    ['-hide_banner', '-i', png, '-vf', 'signalstats,metadata=print', '-f', 'null', '-'],
    { encoding: 'utf8' },
  );
  const log = stderr ?? '';
  const min = /lavfi\.signalstats\.YMIN=(\d+)/.exec(log);
  const max = /lavfi\.signalstats\.YMAX=(\d+)/.exec(log);
  if (!min || !max) return false;
  return Number(max[1]) - Number(min[1]) <= 2;
}

function build(name) {
  const src = join(ROOT, 'examples', `${name}.json`);
  const preset = PRESETS[name] ?? { bg: '#0d1117', step: 2, width: 280, hold: 0 };
  const comp = JSON.parse(readFileSync(src, 'utf8'));
  const ip = Math.round(comp.ip);
  const op = Math.round(comp.op);
  const fr = Math.round(comp.fr);

  // Exclude op: on a seamless loop it duplicates ip and stutters the GIF.
  const frames = [];
  for (let f = ip; f < op; f += preset.step) frames.push(f);

  const tmp = mkdtempSync(join(tmpdir(), `lottie-gif-${name}-`));
  try {
    sh('node', [
      'scripts/render.mjs', src,
      '--frames', frames.join(','),
      '--out', tmp,
      '--bg', preset.bg,
      '--width', String(preset.width),
      '--scale', '2',
      '--no-strip',
    ]);

    // render.mjs names files by frame number, so sort numerically, not lexically.
    let shots = readdirSync(tmp)
      .filter((f) => /^frame-\d+\.png$/.test(f))
      .sort((a, b) => Number(a.match(/\d+/)[0]) - Number(b.match(/\d+/)[0]))
      .map((f) => join(tmp, f));

    const before = shots.length;
    while (shots.length > 1 && isFlat(shots[0])) shots = shots.slice(1);
    const dropped = before - shots.length;

    const seqDir = join(tmp, 'seq');
    mkdirSync(seqDir);
    let i = 0;
    for (const s of shots) copyFileSync(s, join(seqDir, `s-${String(i++).padStart(4, '0')}.png`));

    const fps = fr / preset.step;
    const holdFrames = Math.round(preset.hold * fps);
    for (let h = 0; h < holdFrames; h += 1) {
      copyFileSync(shots[shots.length - 1], join(seqDir, `s-${String(i++).padStart(4, '0')}.png`));
    }

    const out = join(OUT_DIR, `${name}.gif`);
    execFileSync('ffmpeg', [
      '-y', '-loglevel', 'error',
      '-framerate', String(fps),
      '-i', join(seqDir, 's-%04d.png'),
      '-vf', `scale=${preset.width}:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle`,
      '-loop', '0',
      out,
    ], { stdio: ['ignore', 'pipe', 'pipe'] });

    const kb = Math.round(statSync(out).size / 1024);
    console.log(
      `  ${name.padEnd(15)} ${String(shots.length).padStart(3)} frames` +
      `${dropped ? ` (${dropped} empty dropped)` : ''}` +
      `${holdFrames ? ` +${holdFrames} hold` : ''}` +
      `  ${fps}fps  ${kb} KB`,
    );
  } finally {
    rmSync(tmp, { recursive: true, force: true });
  }
}

const only = process.argv[2];
const names = only ? [only] : Object.keys(PRESETS);
console.log(`Building ${names.length} GIF(s) into assets/`);
for (const n of names) build(n);
