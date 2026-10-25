# ArtCraft para personajes 3D — informe (2026-10-20)

Fuente: lectura del repo `storytold/artcraft` y `storytold/artcraft-services` por la API de GitHub (sin clonar),
más getartcraft.com/pricing. Nada instalado, ninguna cuenta creada.

## 1. ¿CLI / canal JSON / MCP? — NO en ArtCraft
- `storytold/artcraft` es una app de escritorio Tauri (`crates/desktop/artcraft`, `main.rs` sólo llama a
  `artcraft_app_lib::run()`) + `artcraft-native` (UI egui, `cargo run -p artcraft_native --release`).
  No hay binario CLI, ni `clap`, ni servidor MCP en el árbol (7.307 rutas revisadas).
- `_docs/dev_setup.md` sólo describe `./script/artcraft/unix_dev.sh` (Vite + `cargo tauri dev`). No menciona CLI ni MCP.
- Lo que sí hay de MCP: tipos de API para *sesiones MCP alojadas* (`artcraft_api_defs/src/mcp_sessions/*`,
  `POST /v1/mcp/session/create`) y la parte de servidor en `artcraft-services`. En
  `frontend/libs/components/pagescene/AGENTS.md`: "MCP not ready", "Deferred: real MCP backend".
- La frase "UI, CLI, JSON control channel o MCP server" es de **PhotoCraft** (`storytold/photocraft`, editor de
  fotos): `photocraft-cli run|batch|mcp`, `photocraft --control`. No genera imágenes con IA.
- Lo que existe para automatizar ArtCraft: la **Omni API** (`_docs/artcraft_omni_api.md`), HTTP con clave
  `artcraft_api_…` contra `https://api.storyteller.ai`. La clave "must have API keys enabled from our staff"
  (acceso restringido por cuenta). La guía sólo documenta `POST /v1/omni_api/generate/video`; imagen/malla por
  Omni API: no verificado (el cliente de escritorio usa `/v1/omni_gen/{models,cost,generate}/...` con sesión).
- Hay un `artcraft-mcp` de terceros (listado en Glama) que reutiliza la sesión de la app y gasta créditos. No oficial, no probado.

## 2. Modelos — todos remotos y de pago
- `RouterProvider`: Artcraft, Midjourney, Fal, GmiCloud, GrokApi, KinoviWeb, WorldLabs. Todos remotos.
- No hay inferencia local en el repo (ni onnx, ni candle, ni torch, ni CUDA).
- Se puede usar fal con clave propia o Midjourney con cuenta propia; siguen siendo de pago.

## 3. Máquina
- WSL2, 12 núcleos, **7,7 GB de RAM**, 8 GB de swap, 900 GB libres.
- `/usr/lib/wsl/lib` sólo tiene `libd3d12*`/`libdxcore` (DirectX). **No hay `libcuda.so`**, así que CUDA no está
  disponible. Modelo de GPU: no verificado.
- A ArtCraft la GPU le da igual: genera en la nube.
- Compilar: los 1,3 GB son el tamaño del repo, no el código Rust. La primera compilación no la he hecho;
  estimación (no medida): 20–60 min, con riesgo de quedarse sin memoria con 7,7 GB de RAM. Además necesita las
  dependencias de WebKitGTK para Tauri y Node 20+.

## 4. Precios (1 crédito = 1 céntimo de USD, comentario en `flux_1_dev/cost.rs`)
Imagen: FLUX.1 dev 2¢ · Nano Banana 4¢ · Seedream 4.5 4¢ · GPT Image 1.5 1–20¢ según calidad · Nano Banana Pro 15¢ (30¢ en 4K) · Seedream 5 Pro 7/12¢.
Malla 3D: Rodin 2.5 Fast 13¢ · Tripo3D H3.1 26–52¢ (+26¢ geometría detallada) · Hunyuan 3D 3.1 Rapid 30¢ (+20¢ PBR) · Hunyuan 3.1 Pro 49¢ (+20¢ por cada extra) · Meshy 6 104¢.
Planes: Basic 10 $/mes (1.000 cr), Pro 35 $ (3.750), Max 60 $ (6.600); hay un 20 % de descuento en el pago anual.
Fuentes: `artcraft-services/crates/api_clients/artcraft/artcraft_router/src/generate/generate_{image,mesh}/providers/artcraft/*/cost.rs` y getartcraft.com/pricing.
