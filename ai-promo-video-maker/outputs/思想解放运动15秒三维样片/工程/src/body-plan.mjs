import timing from './body-timing.json' with {type:'json'};
import {progress} from './plan.mjs';
export {timing};
export function bodyState(frame,config=timing){
 const index=Math.max(0,Math.min(config.count-1,config.starts.findIndex((end,i)=>i>0&&frame<end)-1));
 const actual=frame>=config.starts[config.count]?config.count-1:index;
 const local=Math.max(0,frame-config.starts[actual]);
 const demo=config.demoEnds[actual]-config.starts[actual];
 const next=config.starts[actual+1]-config.starts[actual];
 const actionStart=18;
 return {index:actual,local,phase:Math.min(1,Math.max(0,(local-actionStart)/(demo-actionStart))),travel:progress(local,demo,Math.min(next,demo+19)),enter:progress(local,0,18)};
}
