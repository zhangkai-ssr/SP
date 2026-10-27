import timing from './timing.json' with {type:'json'};
export const DROP = timing.drop*timing.fps;
export const BEAT = timing.beat*timing.fps;
export const progress = (f,a,b) => {const t=Math.min(1,Math.max(0,(f-a)/(b-a)));return t*t*(3-2*t);};
export function cardPose(i,f) {
  const p=progress(f,288+i*1.2,332+i*1.2);
  const x=(i%4-1.5)*5.85,y=3.7-Math.floor(i/4)*2.95;
  return {position:[x*p,y*p,-1+(1-p)*2],rotation:(1-p)*(i%2?-.7:.7),scale:.12+.88*p};
}
export function cameraPose(f) {
  const intro=progress(f,0,225), close=progress(f,DROP+12*BEAT,DROP+17*BEAT);
  return [-1.7*close,.75*close,24-2*intro-2.2*close];
}
export function wordPose(i,f) {
  const travel=f*.18+38*progress(f,145,232)**2;
  const layer=Math.floor(i/4), lane=i%4, angle=lane*Math.PI/2+layer*1.37;
  const radius=8+(i*13%9), depth=22+layer*10+(lane%3)*2-travel;
  let wx=Math.cos(angle)*radius, wy=Math.sin(angle)*radius*.58;
  if(i===0){wx=-6;wy=3;}
  if(i===1){wx=6;wy=-1.5;}
  if(i===2){wx=-3;wy=-4.6;}
  const safeDepth=Math.max(2,depth), scale=32/safeDepth;
  const dx=(wx-Math.sin(f/72)*1.15)*1390/safeDepth;
  const dy=-(wy-Math.sin(f/93)*.65)*1390/safeDepth;
  const roll=Math.sin(f/100)*.035;
  return {x:960+dx*Math.cos(roll)-dy*Math.sin(roll),y:540+dx*Math.sin(roll)+dy*Math.cos(roll),scale,depth,
    opacity:progress(depth,5,15)*(1-progress(depth,28,125))*.92,
    blur:Math.max(0,(depth-38)/18)+Math.max(0,(13-depth)*.22),rotation:roll*180/Math.PI};
}
export function labelVisibility(back,fronts) {
  let visible=back.opacity;
  for(const front of fronts){
    if(front.depth>=back.depth-2||front.opacity<.45)continue;
    const x=Math.max(0,Math.min(back.x+back.width/2,front.x+front.width/2)-Math.max(back.x-back.width/2,front.x-front.width/2));
    const y=Math.max(0,Math.min(back.y+back.height/2,front.y+front.height/2)-Math.max(back.y-back.height/2,front.y-front.height/2));
    visible*=1-progress(x*y/Math.min(back.width*back.height,front.width*front.height),.015,.3)*front.opacity;
  }
  return visible;
}
