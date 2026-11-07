# MedVision AI — Backend (FastAPI)

Backend for **AI-LLM Based Medical Imaging Classification and Segmentation**
(Final-Year Project, Batch B5). Works with the React/Vite frontend in the `frontend` branch.

> ⚠️ Research prototype — **not** a medical device, not for clinical use.
> The classifier and segmenter are currently **placeholders** (see "Plugging in real models").

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                 # Windows: copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Interactive docs: http://localhost:8000/docs

Tests: `pip install -r requirements-dev.txt && pytest`

Docker: `docker build -t medvision-backend . && docker run -p 8000:8000 --env-file .env medvision-backend`

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness check |
| POST | `/api/analyze` | `multipart/form-data` field `file` (`.png/.jpg/.dcm`) → classification, segmentation mask, summary |
| POST | `/api/chat` | `{ message, caseId?, history? }` → `{ reply }` |
| GET | `/api/cases/{caseId}` | Re-fetch a previous analysis (in-memory) |

`/api/analyze` returns the same shape as the frontend's `src/mockData.json`, plus
`caseId`, `segmentation.maskImage` (transparent PNG data-URL for the overlay) and a `disclaimer`.

```json
{
  "caseId": "CASE-2026-A1B2C3",
  "patientInfo": { "caseId": "...", "name": "Anonymous Patient", "scanType": "Chest X-Ray" },
  "classification": { "primaryLabel": "Pneumonia", "confidenceScore": 89.4,
                      "secondaryLabel": "Normal Variant", "secondaryScore": 10.6,
                      "anatomicalTarget": "Left Lower Lobe" },
  "segmentation": { "maskActive": true, "overlayColor": "#f43f5e",
                    "detectedRegionsCount": 2, "maskImage": "data:image/png;base64,..." },
  "llmInitialSummary": "..."
}
```

## Connect the frontend

Copy `frontend-integration/api.js` → `src/api.js` and `frontend-integration/App.jsx` → `src/App.jsx`
in the frontend project, then add `VITE_API_URL=http://localhost:8000` to its `.env` (optional;
that is the default). This replaces the mock `setTimeout` chat and hard-coded 89.4% with live data
and draws the real mask when "Activate Segmentation Mask" is ticked.

## Plugging in real models

Everything model-specific is isolated in `app/services/`:

- `classifier.py` → implement `predict(image) -> Classification`, return it from `get_classifier()`
- `segmenter.py` → implement `segment(image) -> SegmentationResult`, return it from `get_segmenter()`
- `llm.py` → `LLM_PROVIDER=mock` (default) or `anthropic` (set `ANTHROPIC_API_KEY`)

Put weights in `weights/` (git-ignored for `.pt/.pth/.onnx`).

## Structure

```
app/
  main.py          FastAPI app + CORS
  config.py        env settings
  schemas.py       request/response models
  api/routes.py    endpoints
  services/        image_io, classifier, segmenter, llm, store
tests/             pytest suite
frontend-integration/   drop-in api.js + App.jsx for the frontend
```
