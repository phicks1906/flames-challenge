Deno.serve(() =>
  new Response(JSON.stringify({ ok: true, msg: "hello from edge" }), {
    headers: { "Content-Type": "application/json" },
  })
);
