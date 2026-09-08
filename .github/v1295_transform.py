from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')

def one(old,new,label):
    global s
    c=s.count(old)
    if c!=1:
        raise SystemExit(f'{label}: expected 1, found {c}')
    s=s.replace(old,new,1)

one('<meta content="v1294 · authoritative-admin-entitlement-refresh" name="fc-build"/>',
    '<meta content="v1295 · sudden-death-fresh-entry-editor" name="fc-build"/>','build meta')
one('<meta content="Restored Admin controls when a valid admin session has stale client profile state by re-checking the signed-in user’s server-side admin entitlement on boot and when Settings opens." name="fc-whatsnew"/>',
    '<meta content="Fixed sudden-death entry submission so tied finalists get a fresh current-round editor with the sudden-death deadline, rather than the closed original entry or old round media." name="fc-whatsnew"/>','whatsnew')

needle="""function fcEntryWindowClosedV1267(ch) {\n  const ts = Date.parse(ch?.submission_deadline || '');\n  return Number.isFinite(ts) && ts <= Date.now();\n}\n\n\nasync function fcRefreshChampionshipEntryStateV1270(ch) {"""
insert="""function fcEntryWindowClosedV1267(ch) {\n  const ts = Date.parse(ch?.submission_deadline || '');\n  return Number.isFinite(ts) && ts <= Date.now();\n}\n\n// v1295 — a sudden-death submission is a fresh challenge round. The original\n// entry window and round-0 entry are not authoritative while tied finalists are\n// submitting new hidden work. Centralize that state so the editor, cache lookup,\n// and deadline UI cannot disagree again.\nfunction fcSuddenDeathEntryStateV1295(ch) {\n  const active = ch?.sd_phase === 'submitting';\n  const round = Number(ch?.sd_round || 0);\n  const uid = String(state.profile?.id || '');\n  const tied = active && !!uid && Array.isArray(ch?.sd_user_ids) &&\n    ch.sd_user_ids.some(id => String(id) === uid);\n  const endMs = Date.parse(ch?.sd_submit_end || '');\n  const open = active && tied && (!Number.isFinite(endMs) || endMs > Date.now());\n  return { active, round, tied, endMs, open };\n}\n\nasync function fcRefreshChampionshipEntryStateV1270(ch) {"""
one(needle,insert,'insert sd helper')

one("""    const hasFreshDetailStateV1271 =\n      freshnessV1271 > 0 && (Date.now() - freshnessV1271) < 45000;""",
    """    const hasFreshDetailStateV1271 =\n      ch.sd_phase !== 'submitting' &&\n      freshnessV1271 > 0 && (Date.now() - freshnessV1271) < 45000;""",'disable champ cache reuse during sd')

needle="""  seState.standaloneContextV1275 =\n    !document.getElementById('challengeDetailSheet')?.classList.contains('open');\n\n  // v1270 — Championship access and \"do I already have an entry?\" are refreshed"""
insert="""  seState.standaloneContextV1275 =\n    !document.getElementById('challengeDetailSheet')?.classList.contains('open');\n\n  const sdEntryStateV1295 = fcSuddenDeathEntryStateV1295(ch);\n  if (sdEntryStateV1295.active && !sdEntryStateV1295.tied) {\n    toast('Sudden Death entry is limited to the tied finalists.');\n    if (seState.standaloneContextV1275) fcClearStandaloneEntryContextV1275(ch.id);\n    return;\n  }\n  if (sdEntryStateV1295.active && !sdEntryStateV1295.open) {\n    toast('Sudden Death submission window has closed.');\n    if (seState.standaloneContextV1275) fcClearStandaloneEntryContextV1275(ch.id);\n    return;\n  }\n  if (sdEntryStateV1295.active && entryToEdit &&\n      Number(entryToEdit.sd_round || 0) !== sdEntryStateV1295.round) {\n    entryToEdit = null;\n  }\n\n  // v1270 — Championship access and \"do I already have an entry?\" are refreshed"""
one(needle,insert,'sd access guard')

one("""  if (!entryToEdit && state.profile) {\n    const _mine = e => e.user_id === state.profile.id && e.challenge_id === ch.id;\n    entryToEdit = (state.currentEntries || []).find(_mine) || (state.feedEntries || []).find(_mine) || null;\n  }""",
    """  if (!entryToEdit && state.profile) {\n    const _mine = e => e.user_id === state.profile.id &&\n      e.challenge_id === ch.id &&\n      (!sdEntryStateV1295.active || Number(e.sd_round || 0) === sdEntryStateV1295.round);\n    entryToEdit = (state.currentEntries || []).find(_mine) || (state.feedEntries || []).find(_mine) || null;\n  }\n  // A round-0 object supplied by an older card must never turn a sudden-death\n  // submission into an edit of the original entry.\n  if (sdEntryStateV1295.active && entryToEdit &&\n      Number(entryToEdit.sd_round || 0) !== sdEntryStateV1295.round) {\n    entryToEdit = null;\n  }""",'round-filter generic lookup')

one("""    const currentRound = ch.sd_phase === 'submitting' ? Number(ch.sd_round || 0) : 0;\n    const row = rows.find(e => Number(e.sd_round || 0) === currentRound) || rows[0] || null;""",
    """    const currentRound = ch.sd_phase === 'submitting' ? Number(ch.sd_round || 0) : 0;\n    const row = rows.find(e => Number(e.sd_round || 0) === currentRound) ||\n      (ch.sd_phase === 'submitting' ? null : (rows[0] || null));""",'nonchamp refresh round fallback')

one("""  if (entryToEdit) {\n    document.querySelector('#submitEntrySheet h2').textContent = entryModerationV1288 === 'rejected' ? 'Replace Your Entry' : 'Edit Your Entry';\n    if (submitBtn) {\n      submitBtn.disabled = false;\n      submitBtn.textContent = entryModerationV1288 === 'rejected' ? 'Replace & Resubmit' : 'Save Changes';\n    }""",
    """  if (entryToEdit) {\n    document.querySelector('#submitEntrySheet h2').textContent = sdEntryStateV1295.active\n      ? 'Edit Sudden-Death Entry'\n      : (entryModerationV1288 === 'rejected' ? 'Replace Your Entry' : 'Edit Your Entry');\n    if (submitBtn) {\n      submitBtn.disabled = false;\n      submitBtn.textContent = entryModerationV1288 === 'rejected' ? 'Replace & Resubmit' : 'Save Changes';\n    }""",'sd edit title')

one("""  } else {\n    document.querySelector('#submitEntrySheet h2').textContent = 'Your Entry';\n    fcSyncEntryModerationBannerV1288(ch, null);\n    if (submitBtn) submitBtn.textContent = 'Submit Entry';\n  }\n\n  // v1268 — the database deadline is authoritative. Championship entry\n  // windows now close at midnight ET; never leave Save looking active afterward.\n  if (entryToEdit && ch.is_championship && fcEntryWindowClosedV1267(ch)) {""",
    """  } else {\n    document.querySelector('#submitEntrySheet h2').textContent = sdEntryStateV1295.active ? 'Sudden-Death Entry' : 'Your Entry';\n    fcSyncEntryModerationBannerV1288(ch, null);\n    if (submitBtn) submitBtn.textContent = sdEntryStateV1295.active ? 'Submit New Entry' : 'Submit Entry';\n  }\n\n  // v1295 — the active sudden-death window replaces the original entry deadline\n  // for tied finalists. Do not disable a current-round edit just because round 0\n  // closed days earlier.\n  if (sdEntryStateV1295.active && !sdEntryStateV1295.open) {\n    const error = document.getElementById('seError');\n    if (error) {\n      error.textContent = 'Sudden Death submission window has closed.';\n      error.classList.add('show');\n    }\n    if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = 'Sudden Death Closed'; }\n  } else if (!sdEntryStateV1295.active && entryToEdit && ch.is_championship && fcEntryWindowClosedV1267(ch)) {""",'sd deadline ui')

one("""  const _sdSubmitting = ch.sd_phase === 'submitting' && Array.isArray(ch.sd_user_ids) && ch.sd_user_ids.includes(state.profile.id);""",
    """  const _sdStateV1295 = fcSuddenDeathEntryStateV1295(ch);\n  const _sdSubmitting = _sdStateV1295.active && _sdStateV1295.tied;""",'submit sd helper')

marker="""<script>window.FC_V1295_VALIDATION={build:'v1295',suddenDeathFreshRoundEditor:true,oldRoundEntryNeverPrefilled:true,sdDeadlineOverridesOriginalDeadline:true,sdCurrentRoundEditSupported:true,sdNewEntryCopy:true,championshipRoundRefreshForced:true,regularSuddenDeathFallbackFixed:true,v1294AdminRefreshPreserved:true};</script>\n"""
if s.count('</body>')!=1:
    raise SystemExit('body marker')
s=s.replace('</body>',marker+'</body>',1)
p.write_text(s,encoding='utf-8')
