# El diablillo — mascota de Barullo

Bola de cromo iridiscente con cuernos rojos, cuatro pinchos, ojos verdes de enfadado, piercings en la ceja y la
nariz, un halo de cadena con espinas y la cola en lazo con punta de flecha. Sale de las referencias de esta
carpeta (`ref-frente.png`, `ref-espalda.png`, `ref-halo-cadena.png`; material de terceros, sólo consulta).

## 3D (Blender) → bucle de los CTA

- `diablillo.py`: escena entera procedural (Cycles). Cada fotograma se monta para una fase t∈[0,1) y se
  renderiza por separado, así el bucle cierra perfecto y se puede reanudar (`skip=1`).
  Animación: flota, cabecea y gira la cabeza; el halo va con retraso y gira dos eslabones por vuelta; la cola
  latiguea con una onda que crece hacia la punta; un parpadeo por bucle (t≈0.62).
  Luz: HDRI de estudio teñido por altura (magenta arriba, rosa al centro, verde agua abajo) + tiras blancas
  y manchas suaves invisibles a cámara. Fondo transparente.
- `run.sh <args>`: lanza el Blender de Windows en **CPU** (6 hilos), para convivir con los renders de GPU de
  otras sesiones. Ej. final: `./run.sh frames=0-119 res=900 samples=48 skip=1 out=C:/Users/Veintiuno/barullo-render/diablillo/final/f_`
  (~60 s/fotograma). Pruebas: `cam=face` (primer plano de la cara), `res=360 samples=16`.
- `encode.py <carpeta>`: escribe en `public/media/brand/diablillo/` `loop.webm` (VP9 con alfa),
  `loop.webp` (WebP animado para Safari, que no lee el alfa del VP9) y `poster.png`; deja `preview.mp4`
  sobre el negro de la web en la carpeta de fotogramas.
- Web: `src/components/brand/Diablillo.tsx` (en `ProposeCta`, sobre el plato rojo).

## Dibujo vectorial → sello de los formularios

- `vector/diablillo.svg`: la mascota dibujada (contorno uniforme, degradados de cromo), revisada y guardada en
  VectorCraft (`vector/diablillo.vectorcraft`). Copia publicada en `public/media/brand/diablillo/diablillo.svg`.
- Web: `src/components/brand/SelloDiablillo.tsx` (pegatina dentada hueso con texto circular). Va junto a los
  formularios de `/contacto` y `/eventos-privados`, y al enviar cae «de golpe» (`.sello-golpe` en globals.css)
  con «MENSAJE RECIBIDO» / «PROPUESTA RECIBIDA».
