export const DROP:number;
export const BEAT:number;
export function progress(f:number,a:number,b:number):number;
export function cardPose(i:number,f:number):{position:[number,number,number];rotation:number;scale:number};
export function cameraPose(f:number):[number,number,number];
export function wordPose(i:number,f:number):{x:number;y:number;scale:number;depth:number;opacity:number;blur:number;rotation:number};
type LabelBounds={x:number;y:number;width:number;height:number;depth:number;opacity:number};
export function labelVisibility(back:LabelBounds,fronts:LabelBounds[]):number;
