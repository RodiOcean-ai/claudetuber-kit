(async()=>{
const v=document.querySelector('video'); if(!v) return 'no video';
await new Promise(r=>setTimeout(r,1500)); v.muted=true; v.pause();
const D=v.duration; const seek=t=>new Promise(r=>{v.addEventListener('seeked',r,{once:true});v.currentTime=t;setTimeout(r,1500)});
const c=document.createElement('canvas'); c.width=32;c.height=56; const g=c.getContext('2d',{willReadFrequently:true});
let prev=null; const cuts=[];
for(let t=0;t<D-0.05;t+=0.2){await seek(t); g.drawImage(v,0,0,32,56); const d=g.getImageData(0,0,32,56).data;
 if(prev){let s=0;for(let i=0;i<d.length;i+=4){s+=Math.abs(d[i]-prev[i])+Math.abs(d[i+1]-prev[i+1])+Math.abs(d[i+2]-prev[i+2])} s/=(d.length/4*3); if(s>70 && (!cuts.length||t-cuts[cuts.length-1]>0.5)) cuts.push(+t.toFixed(1))} prev=d.slice();}
// contact sheet: 12 frames, 6x2
const W=120,H=213,N=12; const sh=document.createElement('canvas'); sh.width=W*6; sh.height=H*2+16; const sg=sh.getContext('2d'); sg.fillStyle='#000'; sg.fillRect(0,0,sh.width,sh.height);
for(let i=0;i<N;i++){const t=(i+0.5)*D/N; await seek(t); sg.drawImage(v,(i%6)*W,Math.floor(i/6)*H,W,H); sg.fillStyle='#ff0';sg.font='12px monospace';sg.fillText(t.toFixed(1)+'s',(i%6)*W+3,Math.floor(i/6)*H+12);}
document.getElementById('csheet')?.remove(); sh.id='csheet'; Object.assign(sh.style,{position:'fixed',left:'0',top:'0',zIndex:99999,width:sh.width+'px'}); document.body.appendChild(sh);
const views=(document.body.innerText.match(/[\d,]+ views/)||[''])[0];
return JSON.stringify({dur:+D.toFixed(2),cuts,nshots:cuts.length+1,avgShot:+(D/(cuts.length+1)).toFixed(2),pub:document.querySelector('meta[itemprop=uploadDate]')?.content,views});
})()
