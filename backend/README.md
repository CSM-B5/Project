# NeuroAI — Backend (FastAPI)

Backend for **AI-LLM Based Medical Imaging Classification and Segmentation** (brain MRI).
Works with the React/Vite frontend (login + Admin / Doctor / Radiologist / Patient dashboards).

> ⚠️ Research prototype — **not** a medical device, not for clinical use.
> The classifier and segmenter are **placeholders** (see "Plugging in real models").

## What it does

| Role | Can do |
|---|---|
| **Radiologist** | Upload a brain MRI → classification (Glioma / Meningioma / Pituitary / No Tumor), tumour segmentation mask, Dice/IoU (if a ground-truth mask is given) and an AI-drafted report |
| **Doctor** | See studies of *their assigned patients*, edit and **approve** the report |
| **Patient** | See own scans; AI results appear **only after the doctor approves** |
| **Admin** | Create / activate / deactivate users, assign doctors to patients, view the activity log |

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate               # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env               # Mac/Linux: cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Interactive docs: http://localhost:8000/docs  (click **Authorize** after logging in via `/api/auth/login`).

Tests: `pip install -r requirements-dev.txt && pytest`

### Demo accounts (development only)

`.env.example` sets `SEED_DEMO_USERS=true`, which creates these on first start:

| Role | Email | Password |
|---|---|---|
| admin | admin@example.com | Admin@12345 |
| doctor | doctor@example.com | Doctor@12345 |
| radiologist | radiologist@example.com | Radio@12345 |
| patient | patient@example.com | Patient@12345 |

The passwords are public — set `SEED_DEMO_USERS=false` for anything real, and create the first admin with
`ADMIN_EMAIL` / `ADMIN_PASSWORD` in `.env` instead.

## API

| Method | Path | Who | Purpose |
|---|---|---|---|
| GET | `/health` | anyone | Liveness check |
| POST | `/api/auth/login` | anyone | `{email, password, role}` → `{accessToken, user}` |
| POST | `/api/auth/register` | anyone | Self-register a **patient** (can be disabled) |
| GET | `/api/auth/me` | logged in | Current user |
| GET | `/api/stats/dashboard` | logged in | Numbers for the role's StatCards |
| POST | `/api/studies` | radiologist | `multipart`: `file`, optional `patientId`, optional `groundTruthMask` |
| GET | `/api/studies` | logged in | Studies this role may see (`?reportStatus=Pending\|Approved`) |
| GET | `/api/studies/{id}` | logged in | One study with images (data-URLs) |
| PATCH | `/api/studies/{id}` | radiologist, admin | Link study to a patient `{patientId}` |
| POST | `/api/studies/{id}/report/approve` | doctor | Approve (optionally edit `{summary}`) |
| GET | `/api/patients` | admin, doctor, radiologist | Patients to pick from |
| POST | `/api/chat` | admin, doctor, radiologist | `{message, studyId?, history?}` → `{reply}` |
| GET/POST | `/api/admin/users` | admin | List / create users |
| PATCH | `/api/admin/users/{id}` | admin | Edit, (de)activate, assign doctor, reset password |
| GET | `/api/admin/activity` | admin | Audit log |

Send the token as `Authorization: Bearer <accessToken>`.

`GET /api/studies/{id}` has the same shape as the frontend's `mockData.json`:

```json
{
  "id": 1, "caseId": "CASE-2026-00001",
  "patientInfo": { "caseId": "...", "name": "Demo Patient", "scanType": "Brain MRI" },
  "classification": { "predictedClass": "Glioma",
                      "probabilities": { "Glioma": 91.0, "Meningioma": 5.0, "Pituitary": 3.0, "No Tumor": 1.0 } },
  "segmentation": { "status": "Completed", "originalImage": "data:image/png;base64,...",
                    "predictedMask": "data:...", "overlayImage": "data:...",
                    "diceScore": null, "iouScore": null,
                    "detectedRegionsCount": 2, "tumorAreaPercent": 3.4 },
  "report": { "status": "Pending", "summary": "AI-assisted draft: ...", "approvedBy": null }
}
```

## Security notes

- Passwords are hashed with scrypt; login uses signed JWTs (default 8 h).
- Every endpoint checks the role **on the server**; other people's studies return 404.
- Login failures use one generic message, and 5 failures per email lock it for 15 minutes (in memory).
- Uploads are type-checked, size-limited and decoded safely; images are stored under `storage/` using numeric ids only.
- The secret key is generated once into `storage/.secret_key` (git-ignored) unless you set `SECRET_KEY`.
- Use HTTPS in any real deployment, and never use real patient data without proper de-identification and compliance review.

## Connect the frontend

Copy everything in `frontend-integration/src/` over the frontend's `src/` (same folder layout).
It adds `api.js` (axios), a real `AuthContext`, the login call, live dashboard numbers, an MRI upload panel for
radiologists, a study list/approval panel for doctors and patients, and user management for admins.
Optional: `VITE_API_URL=http://localhost:8000` in the frontend `.env`.

## Plugging in real models

Everything model-specific is in `app/services/`:

- `classifier.py` → implement `predict(image) -> ClassificationResult`, return it from `get_classifier()`
- `segmenter.py` → implement `segment(image, tumor_expected) -> SegmentationResult`, return it from `get_segmenter()`
- `llm.py` → `LLM_PROVIDER=mock` (default) or `anthropic` (set `ANTHROPIC_API_KEY`)

Keep the four class names from `CLASSES`. Put weights in `weights/` (git-ignored).

## Structure

```
app/
  main.py  config.py  database.py  models.py  schemas.py  security.py  deps.py  seed.py
  api/        auth, admin, patients, studies, stats, chat
  services/   image_io, classifier, segmenter, visuals, metrics, storage, access, presenter, llm, activity
tests/        27 tests (auth, permissions, workflow, stats, uploads)
frontend-integration/src/   drop-in files for the React frontend
storage/      database + uploaded scans (created at runtime, git-ignored)
```

The database is SQLite (`storage/medvision.db`) and tables are created automatically.
There are no migrations yet: if the models change, delete the file and restart.
