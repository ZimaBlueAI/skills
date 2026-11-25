(() => {
  const paths={
    play:"M7 4l13 8-13 8z",pause:"M8 5v14M16 5v14",
    expand:"M9 4H4v5m11-5h5v5M4 15v5h5m11-5v5h-5",
    collapse:"M4 9h5V4m11 5h-5V4M4 15h5v5m11-5h-5v5",
    undo:"M9 4 3 10l6 6M4 10h10a6 6 0 0 1 0 12",
    redo:"M15 4l6 6-6 6m5-6H10a6 6 0 0 0 0 12",
    prevFrame:"M5 5v14m13-14L8 12l10 7z",nextFrame:"M19 5v14M6 5l10 7-10 7z",
    seed:"M12 3v12m-5-5 5 5 5-5M4 16v4h16v-4",
    export:"M12 16V3m-5 5 5-5 5 5M4 15v6h16v-6",
    split:"M5 4l15 15M5 20 20 5M9 7a3 3 0 1 1-6 0 3 3 0 0 1 6 0m0 10a3 3 0 1 1-6 0 3 3 0 0 1 6 0",
    slow:"M12 4a8 8 0 1 0 8 8M12 12l-5 2m8-10h6",fast:"M12 4a8 8 0 1 0 8 8M12 12l3-5m4-5v6m-3-3h6",
    normal:"M12 4a8 8 0 1 0 8 8M12 8v4l3 2",
    copy:"M8 8h12v13H8zM4 16H3V3h12v2",
    paste:"M8 5H5v16h14V5h-3M9 3h6v4H9z",
    remove:"M3 6h18M8 6V3h8v3M6 6l1 15h10l1-15M10 10v7m4-7v7",
    trimRange:"M7 3v14h14M3 7h14v14",
    trimIn:"M7 4H4v16h3m4-8h9m-4-4 4 4-4 4",
    trimOut:"M17 4h3v16h-3m-4-8H4m4-4-4 4 4 4",
    mute:"M3 9h4l5-4v14l-5-4H3zM16 9l6 6m0-6-6 6",
    sound:"M3 9h4l5-4v14l-5-4H3zM16 8q4 4 0 8m3-11q7 7 0 14",
    refresh:"M20 9a8 8 0 1 0 0 7m0-13v6h-6",
    left:"M20 12H4m6-6-6 6 6 6",right:"M4 12h16m-6-6 6 6-6 6",
    add:"M12 4v16M4 12h16",addAudio:"M4 14v6m-3-3h6M11 16V5l9-2v10m-9 3a3 2 0 1 1-6 0 3 2 0 0 1 6 0m9-3a3 2 0 1 1-6 0 3 2 0 0 1 6 0",
    stretch:"M3 5v14m18-14v14M5 12h14m-11-3-3 3 3 3m8-6 3 3-3 3"
  };
  window.cutIcon=(button,key,label,shortcut="")=>{
    if(!button || !paths[key])return;
    label ||= button.textContent.trim();
    button.title=label+(shortcut?" · "+shortcut:"");
    button.setAttribute("aria-label",label);
    button.classList.add("cut-icon");
    button.innerHTML=`<svg viewBox="0 0 24 24" width="19" height="19" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="${paths[key]}"></path></svg><span></span>`;
    button.lastElementChild.textContent=label;
  };
})();
