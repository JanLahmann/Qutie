import type { APIRoute } from 'astro';

// /sitemap.xml: every page in src/pages except the 404 page and this file. New pages join automatically.
const pages = Object.keys(import.meta.glob('./**/*.astro'))
  .filter((p) => !/\/404\.astro$/.test(p) && !p.includes('['))
  .map((p) => p.replace(/^\.\//, '').replace(/(^|\/)index\.astro$/, '$1').replace(/\.astro$/, '/'))
  .sort();

export const GET: APIRoute = ({ site }) => {
  const urls = pages.map((p) => `  <url><loc>${new URL(p, site).href}</loc></url>`).join('\n');
  return new Response(
    `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>\n`,
    { headers: { 'Content-Type': 'application/xml' } },
  );
};
