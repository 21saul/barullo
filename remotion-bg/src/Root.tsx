import React from 'react';
import {Composition} from 'remotion';
import {BgLiquidChrome} from './BgLiquidChrome';
import {BgBloomDrift} from './BgBloomDrift';
import {BgSparkleField} from './BgSparkleField';
import {FPS} from './tokens';

export const Root: React.FC = () => (
  <>
    <Composition id="BgLiquidChrome-vertical" component={BgLiquidChrome} durationInFrames={FPS * 16} fps={FPS} width={1080} height={1920} />
    <Composition id="BgLiquidChrome-wide" component={BgLiquidChrome} durationInFrames={FPS * 16} fps={FPS} width={1920} height={1080} />
    <Composition id="BgBloomDrift-vertical" component={BgBloomDrift} durationInFrames={FPS * 14} fps={FPS} width={1080} height={1920} />
    <Composition id="BgBloomDrift-wide" component={BgBloomDrift} durationInFrames={FPS * 14} fps={FPS} width={1920} height={1080} />
    <Composition id="BgSparkleField" component={BgSparkleField} durationInFrames={FPS * 4} fps={FPS} width={1920} height={1080} />
  </>
);
