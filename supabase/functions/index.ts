// supabase/functions/ask-ember/ask-ember/index.ts
// Public Edge Function. Powers the "Ask Ember" box in the welcome tour.
// Anthropic key stays server-side. Locked to FlamesChallenge help only.
// Includes a simple in-memory per-IP rate limit.

const ANTHROPIC_API_KEY = Deno.env.get("ANTHROPIC_API_KEY") ?? "";

const CORS = {
  "Access-Control-Allow-Origin": "*", // tighten to your domain later if you want
  "Access-Control-Allow-Headers": "content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

// ---- Rate limit config (tune these) ----
const PER_MINUTE = 6;     // max questions per IP per minute
const PER_HOUR   = 40;    // max questions per IP per hour
// -----------------------------------------

// In-memory store. Resets when the function instance recycles (that's fine —
// the spend cap is the hard backstop; this just stops casual hammering).
const hits = new Map<string, number[]>();

function clientIp(req: Request): string {
  const xff = req.headers.get("x-forwarded-for") || "";
  return xff.split(",")[0].trim() || "unknown";
}

function rateLimited(ip: string): boolean {
  const now = Date.now();
  const arr = (hits.get(ip) || []).filter((t) => now - t < 3600_000); // keep last hour
  const lastMin = arr.filter((t) => now - t < 60_000).length;
  if (lastMin >= PER_MINUTE || arr.length >= PER_HOUR) {
    hits.set(ip, arr);
    return true;
  }
  arr.push(now);
  hits.set(ip, arr);
  // light cleanup so the map can't grow forever
  if (hits.size > 5000) {
    for (const [k, v] of hits) {
      if (v.every((t) => now - t > 3600_000)) hits.delete(k);
    }
  }
  return false;
}

const SYSTEM_PROMPT = `You are Ember, the friendly fire-mascot guide for FlamesChallenge, a social
competition app. You ONLY answer questions about how to use FlamesChallenge.
If asked anything unrelated (general knowledge, coding, personal advice, etc.),
warmly redirect: say you're just here to help them find their way around
FlamesChallenge. Keep answers to 1-3 short sentences. Be upbeat and use the
fire/heat theme lightly (don't overdo it). Never make up features.

How FlamesChallenge works:
- CHALLENGES: pick a category (singing, dunking, drawing, rap, fashion), submit
  an entry, go head-to-head. The community votes; most votes wins. Challenges run
  on a timer with a submitting phase then a voting phase.
- VOTING: one vote per person per challenge. You vote during the voting phase.
- POLLS: quick community votes on hot takes. No points, just opinions.
- POSTS: regular posts and flyers from people you follow show in the Feed.
- RANKS: winning challenges earns rank badges — Spark, Flame, Blaze, Inferno —
  based on number of wins. Keep winning to climb.
- HALL OF FAME / CHAMPIONSHIPS: top players per category qualify for a
  Championship; winners earn medallions (Legend, Icon, Immortal, GOAT) and a
  Champion title. Sudden death can decide close ones.
- PROFILE: tap your avatar for stats, interests, dark mode, and finding people
  to follow.
- NOTIFICATIONS: the bell shows @mentions, replies, and when you get crowned.
- MESSAGES: DM other users directly.
If you don't know something specific, say so and suggest they explore that
section or ask the FlamesChallenge team.`;

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "POST only" }), {
      status: 405, headers: { ...CORS, "Content-Type": "application/json" },
    });
  }

  const ip = clientIp(req);
  if (rateLimited(ip)) {
    return new Response(JSON.stringify({ error: "rate_limited" }), {
      status: 429, headers: { ...CORS, "Content-Type": "application/json" },
    });
  }

  try {
    const { question } = await req.json().catch(() => ({ question: "" }));
    const q = String(question ?? "").trim().slice(0, 200);
    if (!q) {
      return new Response(JSON.stringify({ error: "empty question" }), {
        status: 400, headers: { ...CORS, "Content-Type": "application/json" },
      });
    }
    if (!ANTHROPIC_API_KEY) {
      return new Response(JSON.stringify({ error: "server not configured" }), {
        status: 500, headers: { ...CORS, "Content-Type": "application/json" },
      });
    }

    const resp = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        model: "claude-haiku-4-5-20251001",
        max_tokens: 200,
        system: [{ type: "text", text: SYSTEM_PROMPT, cache_control: { type: "ephemeral" } }],
        messages: [{ role: "user", content: q }],
      }),
    });

    const data = await resp.json();
    if (!resp.ok) {
      return new Response(JSON.stringify({ error: data?.error?.message || "upstream error" }), {
        status: 502, headers: { ...CORS, "Content-Type": "application/json" },
      });
    }

    const answer = (data?.content || [])
      .filter((b: any) => b.type === "text")
      .map((b: any) => b.text)
      .join("\n")
      .trim();

    return new Response(JSON.stringify({ answer }), {
      status: 200, headers: { ...CORS, "Content-Type": "application/json" },
    });
  } catch (_e) {
    return new Response(JSON.stringify({ error: "bad request" }), {
      status: 400, headers: { ...CORS, "Content-Type": "application/json" },
    });
  }
});
