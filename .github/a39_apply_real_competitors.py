#!/usr/bin/env python3
"""A3.9 single-purpose staging patch; rejects any source other than the production v1389 blob."""
import pathlib
import subprocess

p = pathlib.Path("index.html")
sha = subprocess.check_output(["git", "hash-object", str(p)], text=True).strip()
expected = "6ac3a54842e15bb8a554194160ef2e673f51ee17"
if sha != expected:
    raise SystemExit(f"Source drift; expected {expected}, got {sha}. No changes made.")
s = p.read_text(encoding="utf-8")
original = len(s)

def once(old, new, label):
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f"Patch guard for {label}: found {count} copies. No changes made.")
    s = s.replace(old, new, 1)

once('<meta content="v1389 · continuous-championship-medal-rings" name="fc-build"/>',
     '<meta content="v1390 · staging-real-competitor-navigation" name="fc-build"/>', "build")
once('<meta content="Championship gold, silver and bronze portrait rings now form complete, uninterrupted circles." name="fc-whatsnew"/>',
     '<meta content="Staging: navigate real eligible competitors inside the existing challenge viewer." name="fc-whatsnew"/>', "what's new")

css = """<style id="fc-real-competitor-navigation-v1390">
#fvCompetitorStripV1390{display:flex;gap:6px;align-items:center;min-height:50px;flex:0 0 auto;overflow-x:auto;overscroll-behavior-x:contain;scrollbar-width:none;padding:6px 12px;border-bottom:1px solid var(--border);background:var(--surface)}
#fvCompetitorStripV1390[hidden]{display:none}
#fvCompetitorStripV1390::-webkit-scrollbar{display:none}
#fvCompetitorStripV1390 .fc1390-competitor{flex:0 0 auto;min-width:84px;max-width:174px;min-height:36px;padding:7px 10px;border-radius:11px;border:1px solid var(--border);background:var(--surface-2);color:var(--text-muted);font:700 12px/1.2 var(--font-body);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;cursor:pointer}
#fvCompetitorStripV1390 .fc1390-competitor[aria-pressed="true"]{border-color:var(--ember);background:var(--surface);color:var(--text);box-shadow:inset 0 0 0 1px var(--ember)}
#fvCompetitorStripV1390 .fc1390-competitor:focus-visible{outline:2px solid var(--ember);outline-offset:2px}
</style>
"""
once("<!-- v1011 CANONICAL BRAND ASSET:",css+"<!-- v1011 CANONICAL BRAND ASSET:", "CSS")
once("<!-- v670: everything below (entries/counter/standings) now lives in its OWN",
    '<div id="fvCompetitorStripV1390" aria-label="Competitors in this challenge" role="group" hidden></div>\n<!-- v670: everything below (entries/counter/standings) now lives in its OWN', "DOM")

js = """// v1390 staging: labels and navigation come ONLY from the same eligible entry rail.
function fcSyncFvCompetitorStripV1390(index) {
  const strip = document.getElementById('fvCompetitorStripV1390');
  if (!strip || strip.hidden) return;
  strip.querySelectorAll('[data-fv-competitor-index]').forEach((btn, i) => {
    const active = i === index;
    if (btn.getAttribute('aria-pressed') !== String(active)) {
      btn.setAttribute('aria-pressed', String(active));
      if (active && (btn.offsetLeft < strip.scrollLeft || btn.offsetLeft + btn.offsetWidth > strip.scrollLeft + strip.clientWidth)) {
        strip.scrollLeft = Math.max(0, btn.offsetLeft - strip.offsetLeft - 12);
      }
    }
  });
}
function fcRenderFvCompetitorStripV1390(entries, list) {
  const strip = document.getElementById('fvCompetitorStripV1390');
  if (!strip) return;
  strip.replaceChildren();
  const visible = Array.isArray(entries) ? entries : [];
  strip.hidden = visible.length < 2;
  if (strip.hidden || !list) return;
  visible.forEach((entry, index) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'fc1390-competitor';
    btn.dataset.fvCompetitorIndex = String(index);
    btn.setAttribute('aria-label', 'View competitor ' + (index + 1) + ' of ' + visible.length + ': ' + (entry.submitter?.name || 'Competitor'));
    btn.setAttribute('aria-pressed', index === 0 ? 'true' : 'false');
    btn.textContent = (index + 1) + ' · ' + (entry.submitter?.name || 'Competitor');
    strip.appendChild(btn);
  });
  strip.onclick = event => {
    const button = event.target.closest('[data-fv-competitor-index]');
    if (!button || !strip.contains(button)) return;
    const index = Number(button.dataset.fvCompetitorIndex);
    if (!Number.isInteger(index) || index < 0 || index >= visible.length || !list.clientWidth) return;
    list.scrollTo({ left: index * list.clientWidth, behavior: 'smooth' });
  };
}
"""
once("async function openFeedViewer(chId, startEntryId = null, strictStartV1361 = false) {",
     js+"\nasync function openFeedViewer(chId, startEntryId = null, strictStartV1361 = false) {", "viewer")
once("  list.innerHTML    = '<div style=\"text-align:center;padding:40px;color:var(--text-muted);\">Loading…</div>';",
     "  list.innerHTML    = '<div style=\"text-align:center;padding:40px;color:var(--text-muted);\">Loading…</div>';\n  fcRenderFvCompetitorStripV1390([], list);", "reset")
once("    if (!_eligibleVisibleV1047.length) {\n      fcResetFeedViewerActiveHeightV1285(list);",
     "    if (!_eligibleVisibleV1047.length) {\n      fcRenderFvCompetitorStripV1390([], list);\n      fcResetFeedViewerActiveHeightV1285(list);", "empty")
once("    // The first visible frame now contains the real entry rail rather than a",
     "    fcRenderFvCompetitorStripV1390(_eligibleVisibleV1047, list);\n    // The first visible frame now contains the real entry rail rather than a", "render")
once("          const idx = Math.round(list.scrollLeft / list.offsetWidth);\n          if (counter)",
     "          const idx = Math.round(list.scrollLeft / list.offsetWidth);\n          fcSyncFvCompetitorStripV1390(Math.max(0, Math.min(total - 1, idx)));\n          if (counter)", "swipe sync")

assert 'name="fc-build"' in s[:1600] and "v1390 · staging-real-competitor-navigation" in s[:1600]
assert s.count('id="fvCompetitorStripV1390"') == 1
assert "fcVoteUpsertQueryV1112" in s and "renderWinningMediaV1195" in s
assert s.count(js) == 1
p.write_text(s, encoding="utf-8")
print(f"A3.9 staging patched from v1389; delta chars={len(s)-original}; new Git blob={subprocess.check_output(['git','hash-object',str(p)],text=True).strip()}")
