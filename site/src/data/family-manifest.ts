/**
 * Fun with Quantum family manifest loader (build time only).
 *
 * Source of truth: family/family.json in JanLahmann/Fun-with-Quantum. At build time we fetch the
 * live manifest so a roster change reaches this site on the next build (Fun-with-Quantum fires a
 * repository_dispatch at this repo when it changes). If the fetch fails — offline dev, GitHub
 * hiccup — we fall back to the vendored copy in ./family.json so the build never breaks.
 *
 * Override with FWQ_FAMILY_URL (custom source) or FWQ_FAMILY_OFFLINE=1 (vendored copy only).
 */
import vendored from './family.json';

export interface FamilyMember {
  id: string;
  name: string;
  url: string;
  repo?: string;
  door?: 'home' | 'play' | 'build' | 'learn';
  tagline?: string;
  footer: boolean;
  note?: string;
}
export interface FamilyManifest {
  version: number;
  updated: string;
  brand: {
    name: string;
    id: string;
    url: string;
    footer_lead: string;
    tagline: { s: string; m: string; l: string };
    credit: string;
    credit_url: string;
  };
  members: FamilyMember[];
}

const DEFAULT_URL =
  'https://raw.githubusercontent.com/JanLahmann/Fun-with-Quantum/master/family/family.json';
export const SELF_ID = 'qutie';

function isManifest(x: unknown): x is FamilyManifest {
  const m = x as FamilyManifest;
  return !!m && m.version === 1 && Array.isArray(m.members) && typeof m.brand?.name === 'string';
}

let cached: Promise<FamilyManifest> | undefined;
export function loadFamily(): Promise<FamilyManifest> {
  if (!cached) cached = load();
  return cached;
}

async function load(): Promise<FamilyManifest> {
  const fallback = vendored as FamilyManifest;
  if (process.env.FWQ_FAMILY_OFFLINE === '1') return fallback;
  const url = process.env.FWQ_FAMILY_URL ?? DEFAULT_URL;
  try {
    const res = await fetch(url, { signal: AbortSignal.timeout(8000) });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    if (!isManifest(json)) throw new Error('unexpected manifest shape');
    console.log(`[family] manifest from ${url} (updated ${json.updated})`);
    return json;
  } catch (err) {
    console.warn(`[family] live manifest unavailable (${(err as Error).message}); using vendored copy (updated ${fallback.updated})`);
    return fallback;
  }
}

/** Every visible member except this site, in manifest order (brand home first). */
export function footerLinks(m: FamilyManifest, selfId = SELF_ID): FamilyMember[] {
  return m.members.filter((x) => x.footer && x.id !== selfId);
}
