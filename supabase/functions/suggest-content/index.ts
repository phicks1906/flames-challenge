// supabase/functions/suggest-content/index.ts
// Opt-in AI suggestions via Claude Haiku 4.5.
// kind: 'caption'  -> short caption ideas for an entry the user is posting
// kind: 'challenge'-> challenge title/prompt ideas for a category

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

const SYSTEM = `You write short, high-energy suggestions for FlamesChallenge, a social video/photo/audio competition app (categories: Art, Photography, Music, Writing, Cooking, Style, Sports, Fitness, Comedy, Other).
Rules:
- Return ONLY a JSON array of 3 strings. No preamble, no markdown, no keys.
- Keep each item under ~90 characters. Punchy, confident, a little playful.
- No hashtags, no emoji spam (one emoji max, only if it fits).
- Nothing offensive, sexual, or targeting real people.
- For captions: hype the entry without describing pixels you can't see.
- For challenge ideas: give a clear, doable prompt people can actually enter.`;

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "POST only" }), {
      status: 405, headers: { ...CORS, "Content-Type": "application/json" },
    });
  }

  try {
    const key = Deno.env.get("ANTHROPIC_API_KEY");
    if (!key) throw new Error("ANTHROPIC_API_KEY not set");

    const body = await req.json().catch(() => ({}));
    const kind = body?.kind === "challenge" ? "challenge" : "caption";
    const category = String(body?.category ?? "").slice(0, 40);
    const context = String(body?.context ?? "").slice(0, 400);

    const userPrompt = kind === "challenge"
      ? `Suggest 3 challenge ideas${category ? ` for the "${category}" category` : ""}.${context ? ` The creator hinted: "${context}".` : ""}`
      : `Suggest 3 caption ideas for an entry${category ? ` in the "${category}" category` : ""}.${context ? ` Draft/notes: "${context}".` : ""}`;

    const resp = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: "claude-haiku-4-5",
        max_tokens: 300,
        system: [{ type: "text", text: SYSTEM, cache_control: { type: "ephemeral" } }],
        messages: [{ role: "user", content: userPrompt }],
      }),
    });

    if (!resp.ok) {
      const t = await resp.text();
      throw new Error(`anthropic ${resp.status}: ${t.slice(0, 300)}`);
    }

    const data = await resp.json();
    const raw = (data?.content ?? [])
      .map((b) => (b?.type === "text" ? b.text : "")).join("").trim();

    let ideas = [];
    try {
      ideas = JSON.parse(raw.replace(/```json|```/g, "").trim());
    } catch {
      ideas = raw.split("\n").map((s) => s.replace(/^[-*\d.\s]+/, "").trim()).filter(Boolean);
    }
    ideas = ideas.filter((s) => typeof s === "string" && s.length).slice(0, 3);

    return new Response(JSON.stringify({ ideas }), {
      headers: { ...CORS, "Content-Type": "application/json" },
    });
  } catch (e) {
    return new Response(JSON.stringify({ ideas: [], error: String(e?.message ?? e) }), {
      status: 200, headers: { ...CORS, "Content-Type": "application/json" },
    });
  }
});
