from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
repls=[
('<meta content="v1293 · home-next-move-routing-fix" name="fc-build"/>','<meta content="v1294 · authoritative-admin-entitlement-refresh" name="fc-build"/>'),
('<meta content="Fixed Your Next Move routing so Home recommendations perform their own action instead of being intercepted by the daily Ember briefing. The daily briefing still opens automatically on first login each day." name="fc-whatsnew"/>','<meta content="Restored Admin controls when a valid admin session has stale client profile state by re-checking the signed-in user’s server-side admin entitlement on boot and when Settings opens." name="fc-whatsnew"/>')
]
for old,new in repls:
    c=s.count(old)
    if c!=1: raise SystemExit(f'meta replacement count {c}: {old[:80]}')
    s=s.replace(old,new,1)

old='''      if (!state.profile) return; // banned or signed out — loadProfile handled redirect\n      if (typeof window.fcEnsureAccountSetupV1103 === 'function') {\n        await window.fcEnsureAccountSetupV1103();\n      }\n      // A leftover state.currentView from a previous account must never carry\n'''
new='''      if (!state.profile) return; // banned or signed out — loadProfile handled redirect\n      // v1294 — a same-user profile object can survive an iOS/PWA restore even\n      // when its is_admin field is stale or missing. Re-check the signed-in user's\n      // authoritative profile before deciding whether Admin UI exists.\n      if (typeof window.fcRefreshAdminEntitlementV1294 === 'function') {\n        await window.fcRefreshAdminEntitlementV1294({ silent:true });\n      }\n      if (typeof window.fcEnsureAccountSetupV1103 === 'function') {\n        await window.fcEnsureAccountSetupV1103();\n      }\n      // A leftover state.currentView from a previous account must never carry\n'''
if s.count(old)!=1: raise SystemExit(f'hydrate marker count {s.count(old)}')
s=s.replace(old,new,1)

marker='''function isRealAdmin() {\n  if (!state.profile) return false;\n  if (state.profile.is_admin === true) return true;\n  if (state.profile.is_admin === undefined && state.profile.id === ADMIN_BOOTSTRAP_UUID) return true;\n  return false;\n}\n'''
insert=marker+'''\n// v1294 — authoritative admin entitlement refresh. The Admin shield and the\n// View as member escape hatch must not disappear because the in-memory profile\n// is stale or was restored without is_admin. Query only the signed-in user's own\n// profile row, merge the entitlement into state.profile, then resync both Admin\n// surfaces. This never grants access based on a client flag; the server row wins.\nfunction fcSyncAdminSurfacesV1294() {\n  const real = isRealAdmin();\n  const va = document.getElementById('viewAsRow');\n  const admin = document.getElementById('fcAdminSettingsV1117');\n  const vaState = document.getElementById('viewAsState');\n  if (va) va.style.display = real ? 'grid' : 'none';\n  if (admin) admin.style.display = real ? 'block' : 'none';\n  if (vaState) vaState.textContent = state.viewAsMember ? 'On' : 'Off';\n  showAdminNav();\n  return real;\n}\n\nasync function fcRefreshAdminEntitlementV1294({ silent=false } = {}) {\n  const uid = state.session?.user?.id;\n  if (!uid || !state.profile || String(state.profile.id) !== String(uid)) {\n    fcSyncAdminSurfacesV1294();\n    return false;\n  }\n  try {\n    const req = db.from('profiles').select('id,is_admin').eq('id', uid).maybeSingle();\n    const result = typeof fcWithTimeoutV1099 === 'function'\n      ? await fcWithTimeoutV1099(req, 8000, 'Admin entitlement')\n      : await req;\n    if (result?.error) throw result.error;\n    if (result?.data && String(result.data.id) === String(uid)) {\n      state.profile = { ...state.profile, is_admin: result.data.is_admin === true };\n    }\n  } catch (e) {\n    if (!silent) console.warn('[v1294] admin entitlement refresh failed', e);\n  }\n  return fcSyncAdminSurfacesV1294();\n}\nwindow.fcRefreshAdminEntitlementV1294 = fcRefreshAdminEntitlementV1294;\nwindow.fcSyncAdminSurfacesV1294 = fcSyncAdminSurfacesV1294;\n'''
if s.count(marker)!=1: raise SystemExit(f'isRealAdmin marker count {s.count(marker)}')
s=s.replace(marker,insert,1)

old='''    const va=document.getElementById('viewAsRow');\n    const admin=document.getElementById('fcAdminSettingsV1117');\n    const show=typeof isRealAdmin==='function'&&isRealAdmin();\n    if(va)va.style.display=show?'grid':'none';\n    if(admin)admin.style.display=show?'block':'none';\n    const vaState=document.getElementById('viewAsState');if(vaState)vaState.textContent=state.viewAsMember?'On':'Off';\n    const ticker=document.getElementById('tickerState');if(ticker&&typeof tickerDismissed==='function')ticker.textContent=tickerDismissed()?'Off':'On';\n'''
new='''    if(typeof window.fcSyncAdminSurfacesV1294==='function')window.fcSyncAdminSurfacesV1294();\n    else {\n      const va=document.getElementById('viewAsRow');\n      const admin=document.getElementById('fcAdminSettingsV1117');\n      const show=typeof isRealAdmin==='function'&&isRealAdmin();\n      if(va)va.style.display=show?'grid':'none';\n      if(admin)admin.style.display=show?'block':'none';\n      const vaState=document.getElementById('viewAsState');if(vaState)vaState.textContent=state.viewAsMember?'On':'Off';\n    }\n    if(typeof window.fcRefreshAdminEntitlementV1294==='function')window.fcRefreshAdminEntitlementV1294({silent:true});\n    const ticker=document.getElementById('tickerState');if(ticker&&typeof tickerDismissed==='function')ticker.textContent=tickerDismissed()?'Off':'On';\n'''
if s.count(old)!=1: raise SystemExit(f'settings opener marker count {s.count(old)}')
s=s.replace(old,new,1)

validation="""\n<script>window.FC_V1294_VALIDATION={build:'v1294',authoritativeAdminRefresh:true,bootRefresh:true,settingsRefresh:true,viewAsEscapeHatchRestoredForRealAdmins:true,serverIsAdminWins:true,nonAdminsRemainHidden:true,v1293NextMovePreserved:true,v1292AdminEntryControlsPreserved:true};</script>\n"""
if '</body>' not in s: raise SystemExit('body missing')
s=s.replace('</body>',validation+'</body>',1)
p.write_text(s,encoding='utf-8')
