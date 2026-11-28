// Pure Number Search generator; no browser or account dependencies.
export const LEVELS = Object.freeze({easy:{size:6,length:3,count:4},medium:{size:8,length:4,count:6},hard:{size:10,length:5,count:8}});
const dirs=[[0,1],[1,0],[1,1],[1,-1],[0,-1],[-1,0],[-1,-1],[-1,1]];
export function occurrences(grid,word,directions=dirs){
 const hits=[]; const n=grid.length;
 for(let r=0;r<n;r++)for(let c=0;c<n;c++)for(const [dr,dc] of directions){
 if([...word].every((v,i)=>String(grid[r+i*dr]?.[c+i*dc])===v))hits.push({r,c,dr,dc});
 }return hits;
}
export function generateNumberSearch(level='easy',rng=Math.random){
 const cfg=LEVELS[level];if(!cfg)throw new Error('Unknown level');
 const {size,length,count}=cfg;const pick=n=>Math.floor(rng()*n);
 const allowed=dirs.slice(0,level==='easy'?2:level==='medium'?4:8);
 for(let attempt=0;attempt<100;attempt++){
 const grid=Array.from({length:size},()=>Array(size).fill(null));const words=[];
 for(let k=0;k<200&&words.length<count;k++){
 const word=String(1+pick(9))+Array.from({length:length-1},()=>pick(10)).join('');
 if(words.includes(word)||word===[...word].reverse().join(''))continue;
 const r=pick(size),c=pick(size),[dr,dc]=allowed[pick(allowed.length)];
 const cells=[...word].map((v,i)=>[r+i*dr,c+i*dc,Number(v)]);
 if(!cells.every(([y,x,v])=>y>=0&&y<size&&x>=0&&x<size&&(grid[y][x]===null||grid[y][x]===v)))continue;
 for(const [y,x,v] of cells)grid[y][x]=v;words.push(word);
 }
 if(words.length!==count)continue;
 for(const row of grid)for(let i=0;i<size;i++)if(row[i]===null)row[i]=pick(10);
 const solutions=words.map(word=>occurrences(grid,word));
 if(solutions.every(h=>h.length===1))return {level,grid,words,solutions:solutions.map(h=>h[0])};
 }throw new Error('Unable to generate a verified board; retry.');
}
