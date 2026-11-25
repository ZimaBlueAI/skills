(() => {
  let busy = false, timer, attachment, activeKey, refreshView;
  const conversations=new Map();
  window.renderCreativeChat = (host, api, selection, project, notebook={}) => {
    const key = ["zal-chat",project,selection.scene || selection.id || "",selection.script || ""].join(":");
    if(activeKey!==key){clearTimeout(timer);attachment=null;activeKey=key;}
    let chat;
    try { chat = conversations.get(key) || JSON.parse(sessionStorage.getItem(key)); } catch {}
    chat ||= {lines:[]};
    conversations.set(key,chat);
    chat.choices ||= {};
    const persist = () => sessionStorage.setItem(key,JSON.stringify(chat));
    host.innerHTML = `<div class="creation-desk"><main class="creation-main">
      <form class="creative-form"><label>这一镜，你想让观众看见或听见什么？
      <textarea rows="4" required placeholder="给 S01 做一张分镜图，保留凌晨的冷光，把镜头放低一点。"></textarea></label>
      <div class="starter-ideas" aria-label="从示例开始"></div>
      <label hidden class="sample-label">授权声音样本<input type="file" accept=".mp3,.m4a,.wav"></label>
      <div class="compose-actions"><button class="neu-btn primary">发送想法</button><button type="button" class="neu-btn fresh">新对话</button></div></form>
      <div class="creative-log" aria-live="polite"></div></main>
      <aside class="direction-tools"><details open><summary>导演提示</summary><div class="direction-options"></div></details>
      <details><summary>连续性场记</summary><form class="notes-form">
      <label>适用范围<input name="scope" value="全片" placeholder="全片或 S01" required></label>
      <label>人物与服装<textarea name="人物与服装" placeholder="小雨总扎低马尾，左袖有蓝色补丁。"></textarea></label>
      <label>动作与道具<textarea name="动作与道具" placeholder="上一镜右手拿着车票，下一镜递出后手里才空。"></textarea></label>
      <label>光线与声音<textarea name="光线与声音" placeholder="窗光从左侧进入；谈话时雨声逐渐变小。"></textarea></label>
      <button class="neu-btn">保存场记</button><p role="status"></p></form></details></aside></div>`;
    const log=host.querySelector(".creative-log"), form=host.querySelector("form"), input=form.querySelector("textarea");
    const sample=form.querySelector(".sample-label"), file=sample.querySelector("input");
    input.value=chat.draft || "";
    input.oninput=()=>{chat.draft=input.value;persist();};
    const withScene={"分镜图":"为本场最重要的动作画一张分镜图，沿用本场人物与道具，把人物之间的位置交代清楚。","短剧":"把本场拍成一段短剧视频，保留原有对白与转折，用反应镜头交代关系变化。","动画":"把本场做成动画，保留角色辨识度，把关键动作拆成预备、行动与结果。","人物对白":"我想给本场角色配音，请先问我想录哪句台词。","配乐":"为本场适合有音乐的段落设计配乐，遵守剧本的无乐时刻，给对白留出空间。","环境音":"给本场做环境音效，根据场景、空间和道具安排远近，让关键动作声与画面同步。"};
    fetch("/static/direction.json").then(r=>r.json()).then(library=>{
      if(!form.isConnected)return;
      const starters=form.querySelector(".starter-ideas");
      for(const [label,text] of library.starters){
        const idea=selection.scene ? withScene[label] || text : text;
        const b=document.createElement("button");b.type="button";b.textContent=label;b.title=idea;
        b.onclick=()=>{input.value=input.value.trim()?input.value.trim()+"\n"+idea:idea;input.oninput();input.focus();};
        starters.append(b);
      }
      const options=host.querySelector(".direction-options");
      for(const [key,[title,items]] of Object.entries(library.groups)){
        const label=document.createElement("label"),select=document.createElement("select"),hint=document.createElement("small");
        label.append(title,select,hint);select.add(new Option("按场景安排",""));
        for(const name of Object.keys(items))select.add(new Option(name,name));
        select.value=chat.choices?.[key] || "";
        const describe=()=>{hint.textContent=items[select.value] || "";};describe();
        select.onchange=()=>{chat.choices ||= {};if(select.value)chat.choices[key]=select.value;else delete chat.choices[key];describe();persist();};
        options.append(label);
      }
    }).catch(()=>{if(form.isConnected)form.querySelector(".starter-ideas").textContent="示例暂时无法载入，仍可直接写下想法。";});
    const notes=host.querySelector(".notes-form"), scope=notes.elements.scope;
    const fields=["人物与服装","动作与道具","光线与声音"];
    const loadNotes=()=>{const stored=notebook[scope.value.trim().toUpperCase()] || {};for(const k of fields)notes.elements[k].value=stored[k] || "";};
    scope.value=selection.scene || "全片";scope.onchange=loadNotes;loadNotes();
    notes.onsubmit=async ev=>{
      ev.preventDefault();
      const status=notes.querySelector('[role="status"]');
      try{const data=await api("/api/scene-notes",{method:"POST",body:Object.fromEntries(new FormData(notes))});
        notebook[data.scope]=data.notes;status.textContent="已保存，制作对应场次时会自动使用。";
      }catch(error){status.textContent=error.message;}
    };
    file.onchange=()=>{attachment=file.files[0]};
    function draw(){
      log.replaceChildren();
      for(const line of chat.lines){
        const article=document.createElement("article"), who=document.createElement("b"), p=document.createElement("p");
        who.textContent=line.user?"你":"创作助手";p.textContent=line.message;
        article.append(who,p);
        if(line.asset){
          const link=document.createElement("a");link.href=line.asset;link.target="_blank";link.rel="noopener";link.textContent="打开作品";article.append(link);
        }
        if(line.voice){const v=document.createElement("p");v.textContent="音色编号 "+line.voice;article.append(v);}
        log.append(article);
      }
      form.querySelector(".compose-actions button").disabled=busy || chat.pending;
      sample.hidden=!chat.needs_audio;
      log.scrollTop=log.scrollHeight;
    }
    async function send(message,poll=false){
      if(busy) return;
      busy=true;
      if(!poll){chat.lines.push({user:true,message});input.value="";chat.draft="";}
      draw();persist();
      try{
        const body={session:chat.session,message,poll,selection,choices:chat.choices || {}};
        if(attachment && chat.needs_audio && !poll){
          if(attachment.size>20*1024*1024) throw Error("声音样本需要小于 20 MB。");
          body.sample=await new Promise((resolve,reject)=>{const r=new FileReader();r.onload=()=>resolve(r.result.split(",")[1]);r.onerror=reject;r.readAsDataURL(attachment)});
        }
        const reply=await api("/api/creative-chat",{method:"POST",body});
        if(!poll || !reply.pending) chat.lines.push(reply);
        Object.assign(chat,{session:reply.session,pending:!!reply.pending,needs_audio:!!reply.needs_audio});
        if(!chat.needs_audio) attachment=null;
      }catch(error){chat.lines.push({message:error.message || "暂时无法连接工作台。"});chat.pending=false;}
      finally{busy=false;refreshView?.();persist();}
      if(chat.pending && activeKey===key){clearTimeout(timer);timer=setTimeout(()=>send("",true),3500);}
    }
    form.onsubmit=e=>{e.preventDefault();if(input.value.trim())send(input.value.trim());};
    form.querySelector(".fresh").onclick=()=>{
      if(busy) return;
      clearTimeout(timer);
      chat={lines:[],choices:{...chat.choices}};conversations.set(key,chat);attachment=null;input.value="";file.value="";persist();draw();input.focus();
    };
    refreshView=draw;
    draw();
    if(chat.pending && !busy){clearTimeout(timer);timer=setTimeout(()=>send("",true),1000);}
  };
})();
