from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
repls=[
('<meta content="v1291 · moderation-final-status-updates" name="fc-build"/>','<meta content="v1292 · admin-entry-controls-and-adaptive-video-viewer" name="fc-build"/>'),
('<meta content="Made video moderation final states explicit: automatic approvals, extra-review states, and rejections now notify entrants, and rejected videos no longer remain visually stuck under review." name="fc-whatsnew"/>','<meta content="Added direct Admin moderation controls to the entry viewer and made played videos use their actual orientation instead of forcing every video into a small 16:9 stage." name="fc-whatsnew"/>'),
('''<div class="fc-ev-header-actions-v1079">\n<span id="evCounter"></span>\n<button aria-label="Close entry viewer" class="fc-ev-close-v1079" onclick="closeEntryViewer()">×</button>\n</div>\n</div>\n<!-- Swipeable media container -->''','''<div class="fc-ev-header-actions-v1079">\n<span id="evCounter"></span>\n<button id="evAdminBtnV1292" type="button" class="fc-ev-admin-btn-v1292" onclick="fcToggleEvAdminPanelV1292()" aria-expanded="false" style="display:none">🛡 Admin</button>\n<button aria-label="Close entry viewer" class="fc-ev-close-v1079" onclick="closeEntryViewer()">×</button>\n</div>\n</div>\n<div id="evAdminPanelV1292" class="fc-ev-admin-panel-v1292" hidden></div>\n<!-- Swipeable media container -->'''),
('''      controls playsinline preload="metadata"\n      onloadedmetadata="fcRepairVideoMetadataV1194(this)">\n    </video>`;''','''      controls playsinline preload="metadata"\n      onloadedmetadata="fcRepairVideoMetadataV1194(this);fcSizeEvVideoV1292(this)">\n    </video>`;'''),
('''  mediaEl.appendChild(mediaContent);\n\n\n  // Caption''','''  mediaEl.appendChild(mediaContent);\n  fcSyncEvAdminControlsV1292();\n\n\n  // Caption'''),
('''function closeEntryViewer() {\n  document.getElementById('entryViewerSheet').classList.remove('open');''','''function closeEntryViewer() {\n  fcCloseEvAdminPanelV1292();\n  document.getElementById('entryViewerSheet').classList.remove('open');'''),
]
for old,new in repls:
    c=s.count(old)
    if c!=1: raise SystemExit(f'replacement count {c}: {old[:100]}')
    s=s.replace(old,new,1)
helpers=r'''
// v1292 — admins can moderate an entry while looking at the actual full entry,
// instead of backing out to Admin > Flags. This deliberately uses the existing
// hardened moderation mutations so RLS row-count checks, notifications, cache
// refreshes and urgent confirmation remain the single source of truth.
function fcEvModerationStatusV1292(entry) {
  const st = String(entry?.moderation_status || '').toLowerCase();
  if (st === 'approved' || st === 'clear') return {label:'APPROVED', kind:'approved'};
  if (st === 'rejected') return {label:'REJECTED', kind:'rejected'};
  if (st === 'escalated') return {label:'URGENT REVIEW', kind:'urgent'};
  if (st === 'flagged') return {label:'FLAGGED', kind:'flagged'};
  if (st === 'pending') return {label:'UNDER REVIEW', kind:'pending'};
  return {label:'UNREVIEWED', kind:'neutral'};
}

function fcSyncEvAdminControlsV1292() {
  const btn = document.getElementById('evAdminBtnV1292');
  const panel = document.getElementById('evAdminPanelV1292');
  const entry = _evEntry;
  const visible = !!(entry && typeof isAdmin === 'function' && isAdmin());
  if (btn) btn.style.display = visible ? 'inline-flex' : 'none';
  if (!visible) {
    if (panel) { panel.hidden = true; panel.innerHTML = ''; }
    if (btn) btn.setAttribute('aria-expanded','false');
    return;
  }
  if (panel && !panel.hidden) fcRenderEvAdminPanelV1292();
}

function fcToggleEvAdminPanelV1292() {
  if (!(typeof isAdmin === 'function' && isAdmin()) || !_evEntry) return;
  const panel = document.getElementById('evAdminPanelV1292');
  const btn = document.getElementById('evAdminBtnV1292');
  if (!panel) return;
  const opening = panel.hidden;
  panel.hidden = !opening;
  if (btn) btn.setAttribute('aria-expanded', opening ? 'true' : 'false');
  if (opening) fcRenderEvAdminPanelV1292();
}

function fcCloseEvAdminPanelV1292() {
  const panel = document.getElementById('evAdminPanelV1292');
  const btn = document.getElementById('evAdminBtnV1292');
  if (panel) { panel.hidden = true; panel.innerHTML = ''; }
  if (btn) btn.setAttribute('aria-expanded','false');
}

function fcRenderEvAdminPanelV1292() {
  const panel = document.getElementById('evAdminPanelV1292');
  const entry = _evEntry;
  if (!panel || !entry || !(typeof isAdmin === 'function' && isAdmin())) return;
  const st = fcEvModerationStatusV1292(entry);
  const reason = String(entry.moderation_reason || '').trim();
  const isApproved = st.kind === 'approved';
  const isRejected = st.kind === 'rejected';
  panel.innerHTML = `<div class="fc-ev-admin-summary-v1292">
      <span class="fc-ev-admin-status-v1292" data-kind="${st.kind}">${st.label}</span>
      ${reason ? `<span class="fc-ev-admin-reason-v1292">${escapeHtml(reason)}</span>` : ''}
    </div>
    <div class="fc-ev-admin-actions-v1292">
      <button type="button" class="approve" onclick="fcEvAdminActionV1292('approve')" ${isApproved ? 'disabled' : ''}>✅ Approve</button>
      <button type="button" class="reject" onclick="fcEvAdminActionV1292('reject')" ${isRejected ? 'disabled' : ''}>🚫 Reject</button>
      <button type="button" class="delete" onclick="fcEvAdminActionV1292('delete')">🗑 Delete</button>
    </div>`;
}

async function fcReloadEvEntryV1292(entryId) {
  try {
    const { data, error } = await db.from('entries')
      .select('*, submitter:profiles!entries_user_id_fkey(id, name, avatar)')
      .eq('id', entryId).maybeSingle();
    if (error) throw error;
    if (!data) return null;
    _evEntry = data;
    if (_evIndex >= 0 && _evIndex < _evEntries.length) _evEntries[_evIndex] = data;
    return data;
  } catch (e) {
    dlog('mod','viewer-refresh-fail',{entry:String(entryId).slice(0,8),error:String(e?.message||e).slice(0,80)});
    return _evEntry;
  }
}

async function fcEvAdminActionV1292(action) {
  if (!(typeof isAdmin === 'function' && isAdmin()) || !_evEntry) return;
  const entryId = _evEntry.id;
  const status = String(_evEntry.moderation_status || '').toLowerCase();
  const panel = document.getElementById('evAdminPanelV1292');
  panel?.querySelectorAll('button').forEach(b => b.disabled = true);
  try {
    if (action === 'approve') await approveVideoEntry(entryId, status === 'escalated');
    else if (action === 'reject') await rejectVideoEntry(entryId);
    else if (action === 'delete') {
      await removeVideoEntry(entryId);
      const stillThere = await fcReloadEvEntryV1292(entryId);
      if (!stillThere) { closeEntryViewer(); return; }
    }
    if (action !== 'delete') await fcReloadEvEntryV1292(entryId);
    if (_evEntry) _renderEvEntry();
    const p = document.getElementById('evAdminPanelV1292');
    if (p && !p.hidden) fcRenderEvAdminPanelV1292();
  } finally {
    panel?.querySelectorAll('button').forEach(b => b.disabled = false);
  }
}

// v1292 — do not force every played video into a 16:9 rectangle. Size the stage
// from the decoded video's own dimensions. A portrait phone clip can now use the
// available vertical space just like a portrait photo, while landscape clips stay
// landscape. This fixes the "large poster, tiny played video" mismatch.
function fcSizeEvVideoV1292(video) {
  if (!video) return;
  const stage = video.closest('.fc-ev-video-stage-v1194');
  if (!stage) return;
  const w = Number(video.videoWidth) || 0;
  const h = Number(video.videoHeight) || 0;
  if (!(w > 0 && h > 0)) return;
  const ar = Math.max(.35, Math.min(2.4, w / h));
  stage.style.setProperty('--fc-ev-video-ar-v1292', String(ar));
  stage.dataset.fcVideoOrientationV1292 = ar < .82 ? 'portrait' : ar > 1.22 ? 'landscape' : 'square';
  video.dataset.fcVideoOrientationV1292 = stage.dataset.fcVideoOrientationV1292;
}

'''
needle="function closeEntryViewer() {\n  fcCloseEvAdminPanelV1292();"
if s.count(needle)!=1: raise SystemExit('close marker mismatch')
s=s.replace(needle,helpers+needle,1)
css=r'''
<style id="fc-v1292-admin-entry-controls-video-sizing-css">
.fc-ev-admin-btn-v1292{height:34px;padding:0 10px;border-radius:999px;border:1px solid rgba(255,128,62,.28);background:rgba(255,91,32,.08);color:#ff9a62;font:800 10px/1 var(--font-ui);align-items:center;justify-content:center;gap:4px;white-space:nowrap}
.fc-ev-admin-panel-v1292{flex:0 0 auto;padding:10px 14px;border-bottom:1px solid var(--border);background:linear-gradient(180deg,rgba(255,92,31,.055),rgba(255,255,255,.012));box-shadow:inset 0 1px 0 rgba(255,255,255,.035)}
.fc-ev-admin-panel-v1292[hidden]{display:none!important}.fc-ev-admin-summary-v1292{display:flex;align-items:center;gap:8px;min-width:0;margin-bottom:8px}
.fc-ev-admin-status-v1292{flex:0 0 auto;padding:5px 8px;border-radius:999px;font:900 9px/1 var(--font-ui);letter-spacing:.07em;border:1px solid rgba(255,255,255,.12);color:#c9bbb1;background:rgba(255,255,255,.035)}
.fc-ev-admin-status-v1292[data-kind="approved"]{color:#5cdb7c;border-color:rgba(75,205,111,.28);background:rgba(75,205,111,.08)}
.fc-ev-admin-status-v1292[data-kind="rejected"]{color:#ff6d70;border-color:rgba(255,86,92,.30);background:rgba(255,86,92,.08)}
.fc-ev-admin-status-v1292[data-kind="urgent"],.fc-ev-admin-status-v1292[data-kind="flagged"]{color:#ffc05a;border-color:rgba(255,179,65,.30);background:rgba(255,179,65,.08)}
.fc-ev-admin-reason-v1292{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#9f9186;font-size:10px}.fc-ev-admin-actions-v1292{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:7px}
.fc-ev-admin-actions-v1292 button{height:36px;border-radius:10px;font:800 10px/1 var(--font-ui);border:1px solid var(--border);background:var(--surface-2);color:var(--text);touch-action:manipulation}
.fc-ev-admin-actions-v1292 button.approve{color:#60db80;border-color:rgba(75,205,111,.30);background:rgba(75,205,111,.08)}.fc-ev-admin-actions-v1292 button.reject{color:#ff6d70;border-color:rgba(255,86,92,.30);background:rgba(255,86,92,.08)}.fc-ev-admin-actions-v1292 button.delete{color:#c9bbb1}.fc-ev-admin-actions-v1292 button:disabled{opacity:.38}
.fc-entry-viewer-v1079 .fc-ev-video-stage-v1194{aspect-ratio:auto!important;width:100%!important;height:min(72dvh,calc(100vw / var(--fc-ev-video-ar-v1292,1.7777778)))!important;min-height:min(220px,42dvh)!important;max-height:72dvh!important;flex:0 0 auto!important;background:#000!important}
.fc-entry-viewer-v1079 .fc-ev-video-v1194{width:100%!important;height:100%!important;max-height:none!important;object-fit:contain!important;background:#000!important}
.fc-entry-viewer-v1079 .fc-ev-video-stage-v1194[data-fc-video-orientation-v1292="portrait"]{height:min(72dvh,calc(100vw / var(--fc-ev-video-ar-v1292,.5625)))!important}.fc-entry-viewer-v1079 .fc-ev-video-stage-v1194[data-fc-video-orientation-v1292="square"]{height:min(68dvh,100vw)!important}.fc-entry-viewer-v1079 .fc-ev-video-stage-v1194[data-fc-video-orientation-v1292="landscape"]{height:min(58dvh,calc(100vw / var(--fc-ev-video-ar-v1292,1.7777778)))!important}
.fc-entry-viewer-v1079 .entry-viewer-media[data-entry-media-type-v1194="video"]{flex:0 0 auto!important;max-height:72dvh!important;height:auto!important;background:#000!important}.fc-entry-viewer-v1079 .entry-viewer-media[data-entry-media-type-v1194="video"] .fc-ev-media-content-v1079{height:auto!important;max-height:72dvh!important}
@media(max-width:390px){.fc-ev-admin-btn-v1292{font-size:0;width:34px;padding:0}.fc-ev-admin-btn-v1292::after{content:'🛡';font-size:14px}.fc-ev-admin-panel-v1292{padding-inline:10px}}
</style>
<script>window.FC_V1292_VALIDATION={build:'v1292',adminControlsInEntryViewer:true,adminGateUsesIsAdmin:true,approveRejectDeleteReuseHardenedMutations:true,videoStageUsesIntrinsicAspect:true,portraitVideoUsesVerticalSpace:true,forced169Removed:true,v1291ModerationNotificationsPreserved:true};</script>
'''
if 'id="fc-v1292-admin-entry-controls-video-sizing-css"' in s: raise SystemExit('v1292 already applied')
if '</body>' not in s: raise SystemExit('body marker missing')
s=s.replace('</body>',css+'\n</body>',1)
p.write_text(s,encoding='utf-8')
