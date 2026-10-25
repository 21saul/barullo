import { Config } from '@remotion/cli/config';

Config.setVideoImageFormat('png');
Config.setOverwriteOutput(true);
Config.setConcurrency('50%');

// WebGL en Chrome headless (HeroCharacter3D). Probado: swangle y angle
// funcionan; swiftshader falla. Es render por software: lento pero estable.
Config.setChromiumOpenGlRenderer('swangle');

// La mascota 3D con supersampling tarda en montar la escena en cada pestaña.
Config.setDelayRenderTimeoutInMilliseconds(180000);
