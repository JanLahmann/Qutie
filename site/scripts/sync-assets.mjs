// Copies the canonical maker assets from the repo root into the site:
//   /stl/*.stl        -> site/public/models/     (served as direct downloads + 3D viewer)
//   /images/*.{jpg..} -> site/src/assets/gallery/ (optimized by astro:assets)
// Both targets are gitignored — /stl and /images are the single source of truth.
// Runs automatically before `npm run dev` and `npm run build`.

import { copyFileSync, existsSync, mkdirSync, readdirSync, rmSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const siteDir = join(dirname(fileURLToPath(import.meta.url)), '..');
const repoDir = join(siteDir, '..');

const jobs = [
  {
    label: 'models',
    from: join(repoDir, 'stl'),
    to: join(siteDir, 'public', 'models'),
    exts: ['.stl'],
  },
  {
    label: 'gallery',
    from: join(repoDir, 'images'),
    to: join(siteDir, 'src', 'assets', 'gallery'),
    exts: ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.avif'],
  },
];

for (const { label, from, to, exts } of jobs) {
  rmSync(to, { recursive: true, force: true });
  mkdirSync(to, { recursive: true });
  let count = 0;
  if (existsSync(from)) {
    for (const file of readdirSync(from)) {
      if (exts.some((ext) => file.toLowerCase().endsWith(ext))) {
        copyFileSync(join(from, file), join(to, file));
        count += 1;
      }
    }
  }
  console.log(`[sync-assets] ${label}: ${count} file(s)`);
}
