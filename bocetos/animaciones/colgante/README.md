# Colgante: hero loop

This is the home hero loop. It shows the chest of a tanned guy in a white ribbed tank top, wearing a silver Barullo nameplate in the style of the Jägermeister nameplate: the «barullo» kufi wordmark cut out in polished silver, hung on a Cuban curb chain. The background is black, with a red rim on the right shoulder.

The loop is 7 s long (210 frames at 30 fps) and repeats seamlessly.

Body motion is a walk cycle built from driver expressions with harmonics:
- weight shift once per stride
- a bob twice per stride, dipping at heel strike
- shoulder counter-rotation
- breathing on top

The pendant motion is simulated (`rig_pose` + `simulate` in `colgante.py`):
- **Side to side:** a damped pendulum.
- **Away from the chest:** a hinge about the lug line.
  - Each heel strike kicks it off the chest.
  - It taps back with restitution and settles.
- **Pre-roll:** six loops, so the baked cycle is the periodic steady state, with position and velocity matched at the seam.
- **Chain:** the ring motion travels up each strand with a delay, so the links ripple. Every link is baked.

## Files

- `colgante.py` builds the whole scene and renders it. It runs headless with Windows Blender 5.2. The body is `GEO-body_male_realistic` from the Blender Studio *Human Base Meshes* bundle (CC0), loaded from `barullo-render/assets/hbm/`.
- `wordmark-kufi.svg` lives in the render folder. It is a copy of `public/media/brand/wordmark-kufi.svg`. Its polygons are extruded as curves:
  - letters: 3.4 mm thick
  - joining bars: set back from the letter faces
  - side lugs: carry the jump rings
- `lift.py` lifts Blender's pure black to #0B0B0B. Remotion's ffmpeg has no `lutrgb`, so this happens outside ffmpeg.
- `encode.mjs` lifts the frames and encodes the deliverables into `public/media/brand/`:
  - `hero-pendant-square.*`: 1080×1080 crop from the centre
  - `hero-pendant-wide.*`: 2240×960 (21:9)
  - Each one comes as webm VP9, mp4 H.264 and a poster jpg, at ≤ 2.4 MB per video.
- `colgante_medalla.py` is the previous version, a round octogram medallion on a ball chain.

## Rendering

```bash
cd /mnt/c/Users/Veintiuno/barullo-render/colgante   # copy of colgante.py + wordmark-kufi.svg + studio_small_09.hdr
./render_all.sh                                      # EEVEE, iGPU, ~30-60 s/frame, resumable
bocetos/animaciones/colgante/watchdog.sh                          # run alongside: kills a hung Blender (no frame for 4 min) so the loop resumes
node bocetos/animaciones/colgante/encode.mjs                      # from the repo root
```

Useful arguments:
- `frame=N`, `res=50`
- `cam=close`
- `lens` (default 110)
- `hinge_z`: height of the nameplate's lug line
- `lift` and `sway`: simulation targets
- `band_off` and `chrome_gain`: the chrome bands on the letter faces
- `chain_r`: how loosely the chain sits round the neck
- `neck_xf`, `neck_r` and `neck_z`: the square neckline (half-width of the flat bottom, corner radius, height)
- `hide=obj1,obj2`: hide objects from the render, for debugging
- `blur=0`: turn motion blur off

## Known issues

- **Engine:** the loop is rendered in **Cycles on the Radeon iGPU (HIP)** (`render_cycles.sh`). It takes about 105 s/frame at 28 samples with `mr=3`. EEVEE looked like plastic: screen-space SSS, no real GI, and a halo around the body.
- **Halo:** it came from the f/4 depth of field blurring the shoulders into the black background. The camera is now at f/9.
- **Arm swing:** shape keys (`arm_swing_keys`), not an Armature modifier. In Cycles the modifier left a visible crease along the weight falloff.
- **Skin shader:** no clear coat. It has broken-up roughness, blotches, follicles and skin-cell lines.

- **Flat chrome:** EEVEE shows big flat polished faces as one flat grey or black, whether they get the HDRI reflection or an area light. Procedural light/dark bands looked up by the reflection vector fix it (`chrome_bands`), and they sweep as the plate moves.
- **Teeth on the shirt edge:** they were shirt panels poking through the inner arm. They went away with deeper armholes and the arms set a bit further out (9° instead of 12°).
- **Chain inside the neck:** the strands are dropped from z = 1.47 onto the trapezius. From higher up, the rays enter the open neck cut and the chain disappears inside the neck.
- **iGPU memory:** with `mr=3` and a `grid=1100` relief, EEVEE runs out of memory on the iGPU (`EXCEPTION_ACCESS_VIOLATION` in `atio6axx.dll`).
