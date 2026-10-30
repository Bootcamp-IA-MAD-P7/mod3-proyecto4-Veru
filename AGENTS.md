# AGENTS.md — Instrucciones del proyecto

## Idioma y forma de trabajo
- Responder en español, de forma breve y concreta.
- Trabajar issue por issue siguiendo `docs/ISSUES_DESIGN.md`.
- Pedir confirmación antes de acciones destructivas, instalaciones grandes o cambios de alcance.
- No hacer commit ni push sin que el usuario lo pida o lo haya autorizado en el flujo de issues.

## Flujo Git obligatorio
- Rama de desarrollo: `dev`. Rama final: `main`.
- **No commitear directamente en `dev` ni en `main`.**
- Excepción aceptada: el issue #5 ya se inició en `dev`; terminarlo allí.
- Para cada issue nuevo:
  1. `git switch dev && git pull origin dev`
  2. `git switch -c issue/NN-slug` (ej. `issue/06-split-dataset`)
  3. Implementar y verificar. Commits atómicos.
  4. `git push -u origin issue/NN-slug`
  5. Avisar al usuario para que abra el PR y haga merge a `dev`. No mergear sin pedido.
- Al final del proyecto, el usuario pasará todo `dev` a `main`.

## Issues
- Fuente de verdad: `docs/ISSUES_DESIGN.md`.
- Marcar `- [x]` solo cuando el issue esté realmente terminado y verificado.
- No adelantar issues ni mezclar alcance de varios issues en una rama.

## Datos y artefactos
- No versionar imágenes crudas, crops, vídeos, DB ni pesos (`*.pt`, `*.onnx`).
- Sí versionar: `data/raw/metadata.csv`, `data/labeled/manifest.csv`,
  `data/labeled/classes.txt`, labels YOLO `.txt`, `data.yaml` y documentación.
- Mantener provenance (URL, fuente, licencia) al añadir datos.
- Regenerar QA con `python scripts/qa_images.py` cuando cambie el dataset.

## Verificación mínima
- `make check` (compileall + pytest) antes de cerrar cualquier issue que toque código.
- `make test-epicN` para la épica en curso (ej. `make test-epic2`).
- `python scripts/check_labels.py --fill-empty` tras etiquetar.
- No cerrar un issue sin comprobar que los archivos referenciados existen.
- Añadir tests con el marcador de su épica (`@pytest.mark.epicN`) al implementar cada issue.

## Entorno
- Windows + bash, Python 3.14.
- ffmpeg no está en PATH por defecto:
  `export PATH="$LOCALAPPDATA/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.2-full_build/bin:$PATH"`
- LabelImg:
  `labelImg data/labeled/images data/labeled/classes.txt data/labeled/labels`
- YouTube suele bloquear `yt-dlp` con bot check: usar PeerTube o cookies.
