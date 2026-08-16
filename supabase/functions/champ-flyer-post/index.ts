// supabase/functions/champ-flyer-post/index.ts
//
// Renders the Championship Night flyer and posts it to the feed. Server-side,
// so it does not depend on a user opening the app.
//
// Trigger: pg_cron every 10 minutes, plus whatever calls it at launch.
// Idempotent — the unique index on posts is the backstop.
//
// REMEMBER: turn JWT verification OFF on this function after every deploy.
//
// Body (all optional):
//   { "dry_run": true }            -> render only, return base64 PNG, post nothing
//   { "challenge_id": "<uuid>" }   -> restrict to one championship
//   { "force": true }              -> ignore the entry-phase window (testing)

import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.39.7';
import { initWasm, Resvg } from 'https://esm.sh/@resvg/resvg-wasm@2.6.2';

const WASM_URL = 'https://unpkg.com/@resvg/resvg-wasm@2.6.2/index_bg.wasm';

const SUPABASE_URL = Deno.env.get('SUPABASE_URL')!;
const SERVICE_KEY  = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
const FN_SECRET    = Deno.env.get('FC_FN_SECRET') ?? '';

const ASSETS = `${SUPABASE_URL}/storage/v1/object/public/challenge-media/Assets/`;

// Asset filenames are exact. The templates are .jpeg, NOT .jpg. Do not tidy.
const TPL = {
  h2h:  ASSETS + 'flyer-champ-h2h.jpeg',
  top3: ASSETS + 'flyer-champ-top3.jpeg',
};
const FONTS = {
  anton:  ASSETS + 'Anton-Regular.ttf',
  cinzel: ASSETS + 'Cinzel-VariableFont_wght.ttf',
  dmsans: ASSETS + 'flyer-font-dmsans.ttf',
};

const W = 1080, H = 1349;
const GOLD = '#ffdf9a';
const INK  = '#2a1a06';

// Slot geometry — fractions of W/H, measured off the artwork.
const SLOTS: Record<string, any> = {
  h2h: {
    rings: [{ x: 0.295, y: 0.560, r: 0.125 }, { x: 0.705, y: 0.560, r: 0.125 }],
    nameY: 0.712, statY: 0.740, boxY: 0.805, ctaY: 0.945, nameMaxW: 0.34,
  },
  top3: {
    rings: [{ x: 0.250, y: 0.570, r: 0.105 }, { x: 0.505, y: 0.570, r: 0.105 }, { x: 0.760, y: 0.570, r: 0.105 }],
    nameY: 0.706, statY: 0.734, boxY: 0.795, ctaY: 0.936, nameMaxW: 0.24,
  },
};

const COPY = {
  headline: (v: string) => (v === 'h2h' ? 'HEAD TO HEAD' : 'THREE QUALIFY'),
  subline:  (d: string) => (d ? 'ENTRIES CLOSE ' + d : 'ENTRIES OPEN NOW'),
  cta:      'FLAMESCHALLENGE.COM',
  post:     (cat: string, month: string) =>
    `👑 The ${cat} Championship is live for ${month}. The qualifiers are set — entries are open.`,
};

let wasmReady = false;
const cache = new Map<string, Uint8Array>();

async function bytes(url: string): Promise<Uint8Array> {
  const hit = cache.get(url);
  if (hit) return hit;
  const r = await fetch(url);
  if (!r.ok) throw new Error(`fetch ${url} -> ${r.status}`);
  const b = new Uint8Array(await r.arrayBuffer());
  cache.set(url, b);
  return b;
}

function b64(u8: Uint8Array): string {
  // Chunked — a spread over a large array blows the call stack.
  let s = '';
  const CH = 0x8000;
  for (let i = 0; i < u8.length; i += CH) {
    s += String.fromCharCode(...u8.subarray(i, i + CH));
  }
  return btoa(s);
}

function esc(s: string): string {
  return String(s ?? '').replace(/[&<>"']/g, (c) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;' }[c]!));
}

// resvg cannot measure text, so widths are estimated from average glyph width
// as a fraction of font size. These factors are deliberately generous —
// overestimating shrinks text slightly, which is safe. Underestimating
// would overflow the slot, which is not.
const AVG: Record<string, number> = { Anton: 0.46, Cinzel: 0.62, 'DM Sans': 0.55 };

function fitSize(text: string, maxW: number, startPx: number, family: string, trackPx = 0): number {
  const f = AVG[family] ?? 0.55;
  let px = startPx;
  while (px > 12) {
    const w = text.length * (px * f + trackPx);
    if (w <= maxW) break;
    px -= 1;
  }
  return px;
}

function textNode(t: string, x: number, y: number, px: number, family: string,
                  fill: string, track = 0, opacity = 1): string {
  return `<text x="${x.toFixed(1)}" y="${y.toFixed(1)}" font-family="${family}" ` +
    `font-size="${px}" fill="${fill}" text-anchor="middle" ` +
    (track ? `letter-spacing="${track}" ` : '') +
    (opacity !== 1 ? `opacity="${opacity}" ` : '') +
    `>${esc(t)}</text>`;
}

type Fighter = { user_id: string; name: string; boost: number; avatar?: string | null };

async function buildSvg(variant: string, roster: Fighter[], monthLbl: string,
                        category: string, deadlineLabel: string): Promise<string> {
  const S = SLOTS[variant];
  const tplB64 = b64(await bytes(TPL[variant as 'h2h' | 'top3']));

  let defs = '';
  let body = '';

  // Template artwork. Embedded as a data URI — resvg does not fetch remote hrefs.
  body += `<image x="0" y="0" width="${W}" height="${H}" preserveAspectRatio="none" ` +
          `xlink:href="data:image/jpeg;base64,${tplB64}"/>`;

  const eyebrow = `${monthLbl.toUpperCase()}${monthLbl ? ' · ' : ''}${category.toUpperCase()}`;
  body += textNode(eyebrow, W / 2, H * 0.082,
    fitSize(eyebrow, W * 0.8, 26, 'Cinzel', 7), 'Cinzel', GOLD, 7);

  for (let i = 0; i < roster.length; i++) {
    const f = roster[i];
    const ring = S.rings[i];
    const cx = ring.x * W, cy = ring.y * H, r = ring.r * W;

    // Photo avatars draw as photos, clipped to the ring. Anything else — emoji,
    // null, an unreachable URL — falls back to a gold monogram.
    let drew = false;
    if (f.avatar && /^https?:\/\//i.test(f.avatar)) {
      try {
        const raw = await bytes(f.avatar);
        const mime = f.avatar.toLowerCase().endsWith('.png') ? 'image/png'
                   : f.avatar.toLowerCase().endsWith('.webp') ? 'image/webp'
                   : 'image/jpeg';
        defs += `<clipPath id="ring${i}"><circle cx="${cx}" cy="${cy}" r="${r}"/></clipPath>`;
        body += `<image x="${cx - r}" y="${cy - r}" width="${r * 2}" height="${r * 2}" ` +
                `preserveAspectRatio="xMidYMid slice" clip-path="url(#ring${i})" ` +
                `xlink:href="data:${mime};base64,${b64(raw)}"/>`;
        drew = true;
      } catch (_e) { /* fall through to monogram */ }
    }
    if (!drew) {
      const letter = (f.name || '?').trim().charAt(0).toUpperCase() || '?';
      body += `<circle cx="${cx}" cy="${cy}" r="${r}" fill="#1a1206"/>`;
      body += `<text x="${cx}" y="${cy + r * 0.36}" font-family="Anton" ` +
              `font-size="${Math.round(r * 1.05)}" fill="${GOLD}" text-anchor="middle">${esc(letter)}</text>`;
    }

    const nm = (f.name || 'SOMEONE').toUpperCase();
    body += textNode(nm, cx, H * S.nameY, fitSize(nm, W * S.nameMaxW, 44, 'Anton'), 'Anton', GOLD);

    // Boost on both variants — it is the standing that decided the field.
    const boost = Number(f.boost || 0);
    if (boost > 0) {
      const stat = `${boost} BOOST`;
      body += textNode(stat, cx, H * S.statY,
        fitSize(stat, W * S.nameMaxW, 22, 'DM Sans'), 'DM Sans', GOLD, 0, 0.82);
    }
  }

  const hl = COPY.headline(variant);
  body += textNode(hl, W / 2, H * S.boxY, fitSize(hl, W * 0.66, 40, 'Anton'), 'Anton', GOLD);

  const sl = COPY.subline(deadlineLabel);
  body += textNode(sl, W / 2, H * (S.boxY + 0.038),
    fitSize(sl, W * 0.62, 24, 'DM Sans'), 'DM Sans', GOLD, 0, 0.85);

  body += textNode(COPY.cta, W / 2, H * S.ctaY,
    fitSize(COPY.cta, W * 0.8, 28, 'Anton', 4), 'Anton', INK, 4);

  return `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" ` +
         `width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">` +
         `<defs>${defs}</defs>${body}</svg>`;
}

async function renderPng(svg: string): Promise<Uint8Array> {
  if (!wasmReady) {
    await initWasm(await fetch(WASM_URL));
    wasmReady = true;
  }
  const fontBuffers = [
    await bytes(FONTS.anton),
    await bytes(FONTS.cinzel),
    await bytes(FONTS.dmsans),
  ];
  const r = new Resvg(svg, {
    fitTo: { mode: 'width', value: W },
    font: { fontBuffers, defaultFontFamily: 'DM Sans', loadSystemFonts: false },
  });
  return r.render().asPng();
}

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, content-type, x-fc-secret',
};

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: CORS });

  const db = createClient(SUPABASE_URL, SERVICE_KEY, { auth: { persistSession: false } });

  // Two callers, two credentials. The cron uses the shared secret. The admin
  // preview in the app uses the signed-in user's own token — the secret must
  // never be shipped to a browser, where anyone could read it out of the JS.
  let authed = false;
  let adminOnly = false;

  const secret = req.headers.get('x-fc-secret');
  if (FN_SECRET && secret === FN_SECRET) {
    authed = true;
  } else {
    const jwt = (req.headers.get('authorization') ?? '').replace(/^Bearer\s+/i, '');
    if (jwt) {
      const { data: u } = await db.auth.getUser(jwt);
      if (u?.user) {
        const { data: prof } = await db.from('profiles')
          .select('is_admin').eq('id', u.user.id).maybeSingle();
        if (prof?.is_admin) { authed = true; adminOnly = true; }
      }
    }
  }
  if (!authed) return new Response('forbidden', { status: 403, headers: CORS });

  let opts: any = {};
  try { opts = await req.json(); } catch (_e) { /* empty body is fine */ }
  // An admin token can preview, never post. Posting stays with the cron.
  const dryRun = adminOnly ? true : !!opts.dry_run;
  const results: any[] = [];

  try {
    let q = db.from('challenges')
      .select('id, category, creator_id, submission_deadline')
      .eq('is_championship', true);
    if (opts.challenge_id) q = q.eq('id', opts.challenge_id);
    if (!opts.force) q = q.gt('submission_deadline', new Date().toISOString());

    const { data: champs, error: chErr } = await q;
    if (chErr) throw chErr;
    if (!champs?.length) {
      return Response.json({ ok: true, checked: 0, note: 'no championship in entry phase' }, { headers: CORS });
    }

    for (const ch of champs) {
      try {
        if (!dryRun) {
          const { data: prev } = await db.from('posts')
            .select('id').eq('challenge_id', ch.id)
            .eq('auto_kind', 'championship_flyer').limit(1);
          if (prev?.length) { results.push({ id: ch.id, skipped: 'already posted' }); continue; }
        }

        // Month comes from the launch row, which is what fc_monthly_qualifiers keys on.
        const { data: launch } = await db.from('championship_launches')
          .select('month').eq('challenge_id', ch.id).maybeSingle();
        const month = launch?.month;
        if (!month) { results.push({ id: ch.id, skipped: 'no launch row / month' }); continue; }

        // Canonical roster. Filtering role <> 'reserve' rather than = 'qualifier'
        // because the launch snapshot writes 'contender' while the function
        // returns 'qualifier' — correct under either vocabulary.
        const { data: quals, error: qErr } = await db.rpc('fc_monthly_qualifiers', { p_month: month });
        if (qErr) throw qErr;

        const roster: Fighter[] = (quals ?? [])
          .filter((r: any) => r.category === ch.category && r.role !== 'reserve')
          .sort((a: any, b: any) => a.rank - b.rank)
          .slice(0, 3)
          .map((r: any) => ({ user_id: r.user_id, name: r.name, boost: Number(r.boost || 0) }));

        if (roster.length < 2) { results.push({ id: ch.id, skipped: `roster ${roster.length}` }); continue; }

        const { data: profs } = await db.from('profiles')
          .select('id, avatar').in('id', roster.map((r) => r.user_id));
        const avatarOf = new Map((profs ?? []).map((p: any) => [p.id, p.avatar]));
        roster.forEach((r) => { r.avatar = avatarOf.get(r.user_id) ?? null; });

        const variant = roster.length >= 3 ? 'top3' : 'h2h';
        const monthLbl = new Date(month + '-01T12:00:00Z')
          .toLocaleString('en-US', { month: 'long', year: 'numeric', timeZone: 'UTC' });
        const deadlineLabel = ch.submission_deadline
          ? new Date(ch.submission_deadline).toLocaleDateString('en-US',
              { month: 'short', day: 'numeric', timeZone: 'America/New_York' }).toUpperCase()
          : '';

        const svg = await buildSvg(variant, roster, monthLbl, ch.category || '', deadlineLabel);
        const png = await renderPng(svg);

        if (dryRun) {
          results.push({ id: ch.id, variant, roster: roster.map((r) => r.name),
                         png_base64: b64(png) });
          continue;
        }

        const path = `champ-flyers/${ch.id}.png`;
        const { error: upErr } = await db.storage.from('challenge-media')
          .upload(path, png, { contentType: 'image/png', upsert: true, cacheControl: '3600' });
        if (upErr) throw upErr;

        const { data: pub } = db.storage.from('challenge-media').getPublicUrl(path);

        const { data: post, error: insErr } = await db.from('posts').insert({
          user_id: ch.creator_id,
          content: COPY.post(ch.category || 'Flames', monthLbl),
          media_url: pub.publicUrl,
          media_type: 'photo',
          post_type: 'flyer',
          challenge_id: ch.id,
          auto_kind: 'championship_flyer',
        }).select('id').single();

        // 23505 = the unique index caught a double fire. Not an error.
        if (insErr && (insErr as any).code === '23505') {
          results.push({ id: ch.id, skipped: 'race — already posted' });
          continue;
        }
        if (insErr) throw insErr;

        results.push({ id: ch.id, variant, post_id: post.id, roster: roster.map((r) => r.name) });
      } catch (e) {
        results.push({ id: ch.id, error: String(e) });
      }
    }

    return Response.json({ ok: true, dry_run: dryRun, results }, { headers: CORS });
  } catch (e) {
    return Response.json({ ok: false, error: String(e) }, { status: 500, headers: CORS });
  }
});
