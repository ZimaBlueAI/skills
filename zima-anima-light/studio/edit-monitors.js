// The program clock belongs to the sequence. The source viewer has its own native transport.
window.createEditMonitors = function(host, preview, format, position, commit) {
  host.innerHTML=`<section class="screen"><h3>全片时间线</h3><div class="screen-frame program-frame"></div>
    <div class="screen-controls"><button type="button" class="neu-btn play-sequence">播放全片</button>
    <input type="range" class="sequence-seek" aria-label="全片播放位置" step="0.01" min="0"><output></output></div><small class="program-caption"></small></section>
    <section class="screen"><h3>当前素材</h3><div class="screen-frame source-frame"></div><small class="source-caption"></small></section>`;
  const program=host.querySelector(".program-frame"), source=host.querySelector(".source-frame");
  const slider=host.querySelector(".sequence-seek"), play=host.querySelector(".play-sequence");
  let clips=[],soundClips=[],total=0,t=0,playing=false,frame=0,last=0,programKey,sourceKey,media;
  const voices=new Map();
  function mix(force){
    const active=soundClips.filter(c=>t>=c.start && t<c.start+c.duration);
    for(const [id,player] of voices)if(!active.some(c=>c.id===id)){player.pause();voices.delete(id);}
    for(const c of active){
      let audio=voices.get(c.id);
      const added=!audio;
      if(added){
        const node=document.createElement("div");node.innerHTML=preview({...c,kind:"audio"});
        audio=node.querySelector("audio");if(!audio)continue;
        voices.set(c.id,audio);
        audio.onloadedmetadata=()=>{if(voices.get(c.id)===audio)mix(true);};
      }
      audio.volume=c.volume ?? 1;audio.muted=Boolean(c.muted);audio.playbackRate=c.speed || 1;
      const time=(c.in_point || 0)+(t-c.start)*audio.playbackRate;
      if(audio.readyState && (force || Math.abs(audio.currentTime-time)>.3))audio.currentTime=time;
      if(playing && audio.readyState>=2 && audio.paused && !audio.ended)audio.play().catch(()=>{});
    }
  }
  function pause(save=false){
    playing=false;cancelAnimationFrame(frame);media?.pause();window.cutIcon(play,"play","播放全片");
    for(const audio of voices.values())audio.pause();
    if(save)commit(t);
  }
  function stamp(){
    slider.value=t;
    host.querySelector("output").textContent=format(t)+" / "+format(total);
    position(t);
  }
  function show(at, force=false){
    t=Math.max(0,Math.min(total,at));
    const c=clips.find(c=>t>=c.start && (t<c.start+c.duration || (t===total && t===c.start+c.duration)));
    const key=c?[c.id,c.path,c.in_point,c.out_point,c.speed,c.volume,c.muted].join("|"):"gap";
    const changed=key!==programKey;
    if(changed){
      media?.pause();programKey=key;
      program.innerHTML=c?preview(c):"";
      media=program.querySelector("video,audio");
      host.querySelector(".program-caption").textContent=c?.title || (total?"留白":"把第一个镜头加到时间线");
      if(media){
        const element=media;
        element.controls=false;element.muted=Boolean(c.muted);element.volume=c.volume ?? 1;
        const align=()=>{
          if(media!==element)return;
          element.currentTime=Math.min(element.duration || Infinity,(c.in_point || 0)+Math.max(0,t-c.start)*(c.speed || 1));
          element.playbackRate=c.speed || 1;
          if(playing) element.play().catch(()=>{if(media===element && playing)pause();});
        };
        element.onloadedmetadata=align;
        element.onerror=()=>{if(media===element){pause();host.querySelector(".program-caption").textContent="此素材无法播放，请检查文件。";}};
        if(element.readyState>=1)align();
      }
    }else if(force && media && media.readyState>=1){
      media.currentTime=(c.in_point || 0)+Math.max(0,t-c.start)*(c.speed || 1);
    }
    mix(force);stamp();
  }
  function tick(now){
    if(!playing)return;
    const elapsed=(now-last)/1000;last=now;
    let next=t+elapsed;
    if(media){
      const c=clips.find(c=>c.id===programKey.split("|")[0]);
      if(c && !media.ended) next=c.start+Math.max(0,media.currentTime-(c.in_point || 0))/(c.speed || 1);
      else if(c) next=c.start+c.duration;
    }
    show(next);
    if(t>=total-.001){pause(true);return;}
    frame=requestAnimationFrame(tick);
  }
  play.onclick=async()=>{
    if(playing){pause(true);return;}
    if(!total)return;
    if(t>=total-.001)show(0,true);
    source.querySelector("audio,video")?.pause();
    playing=true;last=performance.now();window.cutIcon(play,"pause","暂停全片");
    if(media && media.readyState>=1){try{await media.play();}catch{pause();return;}}
    if(playing)frame=requestAnimationFrame(tick);
  };
  slider.oninput=()=>{pause();show(Number(slider.value),true);};
  slider.onchange=()=>commit(t);
  function update(timeline,duration,selected){
    clips=(timeline.clips || []).filter(c=>(c.track || "V1")==="V1");
    soundClips=(timeline.clips || []).filter(c=>c.track!=="V1" && c.track && c.kind==="audio");
    total=duration;slider.max=total;play.disabled=!total;
    show(playing?t:timeline.playhead || 0,!playing);
    const key=selected?.path;
    if(key!==sourceKey || !source.childNodes.length){
      sourceKey=key;source.querySelector("audio,video")?.pause();
      source.innerHTML=selected?preview(selected):"";
      const player=source.querySelector("audio,video");
      if(player){player.controls=true;player.muted=false;player.onplay=()=>{if(playing)pause(true);};}
    }
    host.querySelector(".source-caption").textContent=selected?.title || "点选时间线片段或素材";
  }
  window.cutIcon(play,"play","播放全片");
  return {update,pause,leave(){pause();source.querySelector("audio,video")?.pause();}};
};
