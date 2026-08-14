# Deploy SIPATURE Annotator ke PythonAnywhere (free)

PythonAnywhere free tier: filesystem persisten (progress aman), tanpa kartu
kredit, satu web app di `https://<username>.pythonanywhere.com`.

## 1. Buat akun

Daftar di https://www.pythonanywhere.com/registration/register/beginner/

## 2. Install dependency (Bash console)

Buka tab **Consoles → Bash**, lalu:

```bash
pip3 install --user fastapi uvicorn
```

## 3. Upload file (tab Files)

Buat struktur berikut (upload via tab **Files**):

```
/home/<username>/annotator/app.py
/home/<username>/annotator/static/index.html
/home/<username>/annotator/requirements.txt
/home/<username>/annotations/pilot_A1_annotations.jsonl   (dan 5 file lainnya)
/home/<username>/annotations/main_A1_annotations.jsonl
```

> 6 file template JSONL diambil dari `ml/data/annotations/` di repo lokal.

## 4. Setup web app (tab Web)

1. **Add a new web app** → **Manual configuration** → pilih **Python 3.10**.
2. Buka link **WSGI configuration file** → ganti isinya dengan:

```python
import os
import sys

os.environ["ANNOTATION_DIR"] = "/home/<USERNAME>/annotations"
os.environ["STATE_DIR"] = "/home/<USERNAME>/annotator/data"
os.environ["ANNOTATOR_USERNAME"] = "tim"
os.environ["ANNOTATOR_PASSWORD"] = "ganti-password-kuat"

project_home = "/home/<USERNAME>/annotator"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from app import app as application  # noqa: E402,F401
```

Ganti `<USERNAME>` dengan username PythonAnywhere kamu.

3. Klik **Reload** (tombol hijau di tab Web).

## 5. Akses

Buka `https://<username>.pythonanywhere.com` → akan minta basic-auth
(username `tim`, password sesuai env). Bagikan URL + credential ke tim.

## Catatan

- Progress tersimpan di `/home/<username>/annotator/data/` (persisten).
- Free tier tidak pakai kartu; web app bisa diakses publik.
- Review text restricted → pastikan `ANNOTATOR_PASSWORD` kuat.
- Bila kena limit CPU free tier, annotate tidak berbarengan 3 orang sekaligus.
