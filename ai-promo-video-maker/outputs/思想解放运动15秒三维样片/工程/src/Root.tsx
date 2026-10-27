import "./index.css";
import { Composition } from "remotion";
import { Promo } from "./Promo";
import timing from "./timing.json";
import {BodyPreview} from './BodyPreview';
import bodyTiming from './body-timing.json';
import fullTiming from './full-timing.json';

const frames = (fps: number) => Math.round(timing.duration * fps);

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition id="FullFilm" component={BodyPreview} durationInFrames={fullTiming.durationFrames} fps={30} width={1920} height={1080} defaultProps={{withAudio:false,full:true}}/>
      <Composition id="BodyPreview" component={BodyPreview} durationInFrames={bodyTiming.durationFrames} fps={30} width={1920} height={1080} defaultProps={{withAudio:false}}/>
      <Composition
        id="Promo"
        component={Promo}
        durationInFrames={frames(timing.fps)}
        fps={timing.fps}
        width={timing.width}
        height={timing.height}
        defaultProps={{ withAudio: true }}
      />
      <Composition
        id="PromoPreview"
        component={Promo}
        durationInFrames={frames(30)}
        fps={30}
        width={timing.width}
        height={timing.height}
        defaultProps={{ withAudio: true }}
      />
    </>
  );
};
