import type { APIRoute } from 'astro';
import { getImage } from 'astro:assets';
import { execSync } from 'node:child_process';

// /sitemap.xml: every page in src/pages except the 404 page and this file. New pages join automatically.
// The site is one page (the sections are #anchors, which sitemaps can't list), so the home page also
// carries the gallery photos as image entries for image search.
const pages = Object.keys(import.meta.glob('./**/*.astro'))
  .filter((p) => !/\/404\.astro$/.test(p) && !p.includes('['))
  .map((p) => p.replace(/^\.\//, '').replace(/(^|\/)index\.astro$/, '$1').replace(/\.astro$/, '/'))
  .sort();

// <lastmod>: the date of the commit being built — stable across the family-footer rebuilds, which
// don't add commits. Omitted if git isn't available.
let lastmod: string | undefined;
try {
  lastmod = execSync('git log -1 --format=%cs', { encoding: 'utf8' }).trim() || undefined;
} catch {}

const galleryModules = import.meta.glob<{ default: ImageMetadata }>(
  '../assets/gallery/*.{jpg,jpeg,png,webp,gif,avif}',
  { eager: true }
);

export const GET: APIRoute = async ({ site }) => {
  const photos = await Promise.all(
    Object.keys(galleryModules)
      .sort()
      .map(async (k) => new URL((await getImage({ src: galleryModules[k].default, width: 1200, format: 'jpeg' })).src, site).href)
  );
  const urls = pages
    .map((p) => {
      const images = p === '' ? photos.map((src) => `\n    <image:image><image:loc>${src}</image:loc></image:image>`).join('') : '';
      return `  <url>\n    <loc>${new URL(p, site).href}</loc>${lastmod ? `\n    <lastmod>${lastmod}</lastmod>` : ''}${images}\n  </url>`;
    })
    .join('\n');
  return new Response(
    `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n${urls}\n</urlset>\n`,
    { headers: { 'Content-Type': 'application/xml' } },
  );
};
