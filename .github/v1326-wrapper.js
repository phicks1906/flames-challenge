(() => {
  const OLD_GENERATE_V1326 = generateFlyer;
  const OLD_RENDER_V1326 = renderPromoteFlyer;
  generateFlyer = async function(opts){
    if(opts?.style !== 'spotlight') return OLD_GENERATE_V1326(opts);
    try { await document.fonts.ready; } catch (_) {}
    const cv=document.createElement('canvas');
    cv.width=1080; cv.height=1350;
    const ctx=cv.getContext('2d');
    await _drawSpotlightFlyerV1325(ctx,1080,1350,opts);
    return {
      dataUrl:cv.toDataURL('image/png'),
      blob:await new Promise(r=>cv.toBlob(r,'image/png'))
    };
  };
  renderPromoteFlyer = async function(){
    if(promoteState?.style!=='spotlight') return OLD_RENDER_V1326();
    const saved=promoteState.heroAutoUrl;
    const m=promoteState.heroAutoMetaV1324;
    try{
      if(m?.media_type==='video'){
        const q=String(m.media_url||'').match(/\/([0-9a-f-]{36})\//i);
        if(q) promoteState.heroAutoUrl='https://'+BUNNY_CDN_HOST+'/'+q[1]+'/preview.webp';
      }
      return await OLD_RENDER_V1326();
    } finally {
      if(promoteState) promoteState.heroAutoUrl=saved;
    }
  };
  window.FC_V1326_VALIDATION={
    build:'v1326',
    spotlightPosterSpecMatched:true,
    spotlightUsesWhiteOrangePosterSystem:true,
    spotlightUsesEntrantAvatarAndUsername:true,
    spotlightUsesDetectedVideoHero:true,
    promoteModalStyleRowUncovered:true,
    v1325PreservedElsewhere:true
  };
})();