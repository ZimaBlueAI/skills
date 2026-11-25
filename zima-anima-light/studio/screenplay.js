/* Render both the imported production screenplay and the editable Light script. */
window.mountScreenplay = function (host, documents, onEdit, feedback, saveFeedback, dismiss, onProduce) {
  let current = 0;
  const el = (tag, cls, text) => {
    const node = document.createElement(tag);
    node.className = cls;
    node.textContent = text || "";
    return node;
  };
  function sectionList(text) {
    const sections = [{title:"创作说明", lines:[]}];
    for (const line of text.split(/\r?\n/)) {
      const heading = line.trim().replace(/^#{1,6}\s*/, "");
      if (/^(?:S\d{1,3}\b|第[\d一二三四五六七八九十百]+[场幕]|场景\s*\d+|(?:INT|EXT)\.)/i.test(heading)) {
        sections.push({title:heading, lines:[]});
      } else sections.at(-1).lines.push(line);
    }
    return sections;
  }
  function draw() {
    const doc = documents[current];
    const sections = sectionList(doc.text);
    const head = el("header", "script-head");
    const picker = el("select", "script-picker");
    picker.setAttribute("aria-label","剧本来源");
    documents.forEach((d,i) => picker.add(new Option(d.label,i,false,i===current)));
    picker.onchange = () => { current = Number(picker.value); draw(); };
    const edit = el("button","neu-btn",doc.source ? "从此稿开始改写" : "编辑工作稿");
    edit.onclick = () => onEdit(doc);
    const produce=el("button","neu-btn primary","制作这一场");
    produce.onclick=()=>onProduce(doc, activeScene);
    head.append(picker,edit,produce);
    const nav = el("nav","script-index");
    nav.setAttribute("aria-label","剧本场次");
    nav.append(el("h3","","场次目录"));
    const paper = el("article","script-page");
    const margin = el("aside","script-margin");
    const tools = el("div","quote-actions");
    const threads = el("div","quote-threads");
    const bar=el("div","script-selbar");
    bar.hidden=true;
    bar.onmousedown=e=>e.preventDefault();
    const styles={yellow:"黄色高亮",teal:"青色高亮",pink:"粉色高亮",green:"绿色高亮",underline:"下划线",strike:"删除线"};
    let activeScene, anchor;
    const documentKey = doc.source ? "development/screenplay-v001.md" : "boards/story.md";
    function locate(a) {
      const content = paper.textContent;
      let start = a.start;
      if (content.slice(start,start+a.quote.length)!==a.quote) {
        start = content.indexOf(a.quote);
        if (start<0 || content.indexOf(a.quote,start+1)>=0) return;
      }
      const nodes = document.createTreeWalker(paper,NodeFilter.SHOW_TEXT);
      const range = document.createRange();
      let offset=0, begun=false;
      while(nodes.nextNode()){
        const n=nodes.currentNode, next=offset+n.length;
        if (!begun && start<next) {range.setStart(n,start-offset);begun=true;}
        if (begun && start+a.quote.length<=next) {range.setEnd(n,start+a.quote.length-offset);return range;}
        offset=next;
      }
    }
    function showThreads(){
      const ranges=Object.fromEntries(Object.keys(styles).map(k=>[k,[]]));
      threads.replaceChildren();
      for(const item of feedback.filter(f=>f.anchor?.document===documentKey && f.anchor.scene===activeScene && f.status!=="dismissed")){
        const range=locate(item.anchor);
        if(range) (ranges[item.anchor.style] || ranges.yellow).push(range);
        const b=el("button","quote-thread",(item.kind?"批注":"评论")+" · "+item.anchor.quote);
        b.disabled=!range;
        b.onclick=()=>{
          const sel=getSelection();sel.removeAllRanges();sel.addRange(range);
          range.startContainer.parentElement.scrollIntoView({block:"center"});
        };
        threads.append(b,el("p","",item.body));
        if(item.anchor.style){
          const remove=el("button","quote-thread","移除标记");
          remove.onclick=async()=>{await dismiss(item.id);item.status="dismissed";showThreads();};
          threads.append(remove);
        }
      }
      if(window.Highlight) for(const [name,group] of Object.entries(ranges)) CSS.highlights.set("story-"+name,new Highlight(...group));
    }
    function selected(){
      const sel=getSelection();
      bar.hidden=true;
      if (!sel.rangeCount || sel.isCollapsed) return;
      const range=sel.getRangeAt(0);
      if (!paper.contains(range.commonAncestorContainer)) return;
      const quote=range.toString();
      if(!quote.trim()) return;
      const before=document.createRange();before.selectNodeContents(paper);
      before.setEnd(range.startContainer,range.startOffset);
      anchor={document:documentKey,scene:activeScene,start:before.toString().length,quote};
      bar.replaceChildren();
      const rect=range.getBoundingClientRect();
      bar.hidden=false;
      for(const [style,label] of Object.entries(styles)){
        const mark=el("button","mark-"+style,style==="underline"?"下划":style==="strike"?"删除线":"");
        mark.type="button";mark.title=label;mark.setAttribute("aria-label",label);
        mark.onclick=async()=>{
          const saved={...anchor,style};bar.hidden=true;
          try{feedback.push(await saveFeedback("annotate",saved,label));showThreads();}
          catch(err){tools.textContent=err.message;}
        };
        bar.append(mark);
      }
      for(const [action,label] of [["annotate","批注"],["comment","评论"]]){
        const btn=el("button","neu-btn",label);
        btn.onclick=()=>{
          const saved={...anchor};
          bar.hidden=true;
          const input=el("textarea","");input.placeholder="写下"+label;input.setAttribute("aria-label",input.placeholder);
          const send=el("button","neu-btn","保存"+label);
          const cancel=el("button","neu-btn","取消");
          cancel.onclick=()=>tools.replaceChildren();
          send.onclick=async()=>{
            if(!input.value.trim()) return;
            send.disabled=true;
            try {feedback.push(await saveFeedback(action,saved,input.value.trim()));tools.replaceChildren();showThreads();}
            catch(err){send.disabled=false;tools.append(el("p","",err.message));}
          };
          tools.replaceChildren(el("blockquote","",saved.quote),input,send,cancel);
          input.focus();
        };
        bar.append(btn);
      }
      bar.style.left=Math.max(4,Math.min(rect.left,innerWidth-bar.offsetWidth-6))+"px";
      bar.style.top=Math.max(4,rect.top-bar.offsetHeight-5)+"px";
    }
    paper.onpointerup=()=>setTimeout(selected,0);
    paper.onkeyup=selected;
    paper.onscroll=()=>{bar.hidden=true;};
    paper.onpointerdown=()=>{bar.hidden=true;};
    paper.onclick=e=>{
      if(!getSelection().isCollapsed || !document.caretRangeFromPoint) return;
      const point=document.caretRangeFromPoint(e.clientX,e.clientY);
      if(!point) return;
      const items=feedback.filter(f=>f.anchor?.document===documentKey && f.anchor.scene===activeScene && f.status!=="dismissed");
      const index=items.findIndex(item=>locate(item.anchor)?.isPointInRange(point.startContainer,point.startOffset));
      const note=index>=0 ? threads.querySelectorAll("p")[index] : null;
      if(note){note.scrollIntoView({block:"nearest"});note.animate([{background:"#f6e0a6"},{background:"transparent"}],900);}
    };
    margin.append(el("h3","","本场批注与评论"),el("p","muted","在正文中划选文字，即可留下批注或评论。"),tools,threads);
    function read(index) {
      const scene = sections[index];
      activeScene=scene.title;
      produce.hidden=index===0;
      bar.hidden=true;
      tools.replaceChildren();
      const [name, ...time] = scene.title.split("｜");
      paper.replaceChildren(el("h2","",name));
      if (time.length) paper.append(el("p","script-time",time.join(" · ")));
      for (const raw of scene.lines) {
        const line = raw.trim();
        if (!line || line === "---") continue;
        const clean = line.replace(/^#{1,6}\s*/,"").replace(/\*\*/g,"");
        const dialogue = clean.match(/^([^：:]{1,25})[：:]\s*([“「"].*)$/);
        if (dialogue) {
          const block = el("p","script-dialogue");
          block.append(el("b","",dialogue[1]),el("span","",dialogue[2]));
          paper.append(block);
        } else {
          const cls = /^\*\*\d\d:\d\d/.test(line) ? "script-time" : /^#|^\*\*/.test(line) ? "script-note" : "";
          paper.append(el("p",cls,clean));
        }
      }
      [...nav.querySelectorAll("button")].forEach((b,i)=>b.setAttribute("aria-current",String(i===index)));
      paper.scrollTop = 0;
      showThreads();
    }
    sections.forEach((s,i)=>{
      const b = el("button","",s.title.split("｜")[0]);
      b.onclick = () => read(i);
      nav.append(b);
    });
    const spread = el("div","script-spread");
    spread.append(nav,paper,margin);
    host.replaceChildren(head,spread,bar);
    read(sections.length > 1 ? 1 : 0);
  }
  draw();
};
