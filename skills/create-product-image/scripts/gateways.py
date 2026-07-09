"""Zwei Gateways zu OpenAIs gpt-image-Familie, hinter einer gemeinsamen Schnittstelle.

- openrouter: chat/completions in Bild-Modalitaet. Referenzen gehen als base64-Data-URI
  rein, das Bild kommt als base64 zurueck. Kein Upload-Schritt. Ausgabe ist immer
  ~quadratisch (1024^2), das Seitenverhaeltnis steuert nur die Komposition.
- fal: fal.ai-SDK mit Upload -> subscribe -> Download. Liefert ECHTE Ausgabegroessen,
  bei gpt-image-2 bis 3840px.

Der Unterschied ist keine Nebensaechlichkeit: bei openrouter ist --aspect-ratio ein
Wunsch an das Modell, bei fal eine Tatsache der Leinwand.

Beide Gateways liefern (bild_bytes, meta_dict) und schreiben ihre Kosten in die
.meta.json neben dem Bild.
"""
from __future__ import annotations

import base64
import json
import mimetypes
import os
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Callable

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Modell-Registry. Das Gateway ergibt sich aus dem Modell, nicht umgekehrt -
# so kann --model allein das Gateway bestimmen und beide bleiben konsistent.
MODELS: dict[str, dict[str, Any]] = {
    # --- OpenRouter -----------------------------------------------------------
    # Achtung: ein literales "openai/gpt-image-2" gibt es auf OpenRouter NICHT.
    "gpt-5.4-image-2": {
        "gateway": "openrouter",
        "id": "openai/gpt-5.4-image-2",
        "custom_size": False,
    },
    "gpt-5-image": {
        "gateway": "openrouter",
        "id": "openai/gpt-5-image",
        "custom_size": False,
    },
    "gpt-5-image-mini": {
        "gateway": "openrouter",
        "id": "openai/gpt-5-image-mini",
        "custom_size": False,
    },
    # --- fal.ai ---------------------------------------------------------------
    "gpt-image-1": {
        "gateway": "fal",
        "t2i": "fal-ai/gpt-image-1/text-to-image",
        "edit": "fal-ai/gpt-image-1/edit-image",
        "custom_size": False,
        "size_by_ar": {
            "9:16": (1024, 1536), "16:9": (1536, 1024), "1:1": (1024, 1024),
            "2:3": (1024, 1536), "3:2": (1536, 1024),
        },
        "cost_by_quality": {"low": 0.04, "medium": 0.08, "high": 0.20},
    },
    "gpt-image-2": {
        "gateway": "fal",
        "t2i": "openai/gpt-image-2",
        "edit": "openai/gpt-image-2/edit",
        "custom_size": True,
        "size_by_ar": {
            "9:16": (1024, 1536), "16:9": (1536, 1024), "1:1": (1024, 1024),
            "2:3": (1024, 1536), "3:2": (1536, 1024),
            "3:4": (1536, 2048), "4:3": (2048, 1536), "4:5": (1024, 1280),
        },
        "cost_by_quality": {"low": 0.02, "medium": 0.07, "high": 0.19},
    },
}

DEFAULT_MODEL = {"openrouter": "gpt-5.4-image-2", "fal": "gpt-image-1"}

KEY_SPEC = {
    "openrouter": (("OPENROUTER_API_KEY", "OPENROUTER_KEY"), "OPENROUTER_API_KEY",
                   "https://openrouter.ai/keys"),
    "fal": (("FAL_API_KEY", "FAL_KEY"), "FAL_KEY", "https://fal.ai/dashboard/keys"),
}


def models_for(gateway: str) -> list[str]:
    return [n for n, c in MODELS.items() if c["gateway"] == gateway]


def load_key(gateway: str) -> str:
    """Hole den Key aus der Umgebung oder einer .env im Verzeichnisbaum aufwaerts.

    Beendet das Script mit klarer Meldung, wenn nichts gefunden wird - ein fehlender
    Key soll ein sauberer Abbruch sein, kein stiller Fehlschlag mitten im Batch.
    """
    names, canonical, url = KEY_SPEC[gateway]
    for var in names:
        val = os.environ.get(var)
        if val:
            os.environ[canonical] = val
            return val
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        env = parent / ".env"
        if not env.exists():
            continue
        for line in env.read_text().splitlines():
            line = line.strip()
            for var in names:
                if line.startswith(var + "="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        os.environ[canonical] = val
                        return val
    sys.exit(
        f"ERROR: {' oder '.join(names)} nicht gesetzt. Exportiere den Key oder trage ihn "
        f"in eine .env ein.\nKey holen: {url}"
    )


def write_meta(output_path: Path, **fields: Any) -> Path:
    """Schreibe eine .meta.json neben das Bild (Nachweis: welches Modell, welche Referenzen)."""
    fields.setdefault("wrote_at", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    meta_path = output_path.with_suffix(output_path.suffix + ".meta.json")
    meta_path.write_text(json.dumps(fields, indent=2, default=str))
    return meta_path


# --------------------------------------------------------------------------- #
# OpenRouter
# --------------------------------------------------------------------------- #

def _data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(str(path))[0] or "image/jpeg"
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


def openrouter_generate(model_id: str, prompt: str, ref_paths: list[Path], key: str,
                        *, timeout: int = 300, retries: int = 2) -> tuple[bytes, dict]:
    """chat/completions in Bild-Modalitaet. Referenzen inline als base64.

    Nicht-leere ref_paths entsprechen dem /edit-Modus von fal: das Modell ankert
    stark auf dem Eingabebild. Reihenfolge zaehlt, sauberstes Produktfoto zuerst.
    """
    content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
    for r in ref_paths:
        content.append({"type": "image_url", "image_url": {"url": _data_uri(Path(r))}})
    body = json.dumps({
        "model": model_id,
        "messages": [{"role": "user", "content": content}],
        "modalities": ["image", "text"],
    }).encode()

    last = ""
    for attempt in range(retries + 1):
        req = urllib.request.Request(OPENROUTER_URL, data=body, headers={
            "Authorization": f"Bearer {key}", "Content-Type": "application/json",
        })
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                d = json.load(resp)
        except Exception as e:
            last = str(e)
            if hasattr(e, "read"):
                try:
                    last += " " + e.read().decode()[:300]
                except Exception:
                    pass
            time.sleep(2 * (attempt + 1))
            continue
        if isinstance(d, dict) and d.get("error"):
            last = str(d["error"])[:300]
            time.sleep(2 * (attempt + 1))
            continue
        msg = d.get("choices", [{}])[0].get("message", {})
        imgs = msg.get("images") or []
        if not imgs:
            last = ("keine Bilder; finish=" + str(d.get("choices", [{}])[0].get("finish_reason"))
                    + " text=" + str(msg.get("content"))[:150])
            time.sleep(2 * (attempt + 1))
            continue
        url = imgs[0]["image_url"]["url"]
        usage = d.get("usage", {})
        return base64.b64decode(url.split(",", 1)[1]), usage
    raise RuntimeError(f"OpenRouter-Bildgenerierung fuer {model_id} nach {retries + 1} Versuchen fehlgeschlagen: {last}")


# --------------------------------------------------------------------------- #
# fal.ai
# --------------------------------------------------------------------------- #

def _fal_upload(path: Path) -> str:
    import fal_client  # spaet importiert, damit load_key zuerst laeuft
    if not path.exists():
        raise FileNotFoundError(f"Referenz fehlt: {path}")
    size = path.stat().st_size
    if size > 50 * 1024 * 1024:
        raise ValueError(f"Datei ueber 50 MB: {path} ({size} Bytes)")
    return fal_client.upload_file(str(path))


def _fal_subscribe(model: str, arguments: dict, *, with_logs: bool = False,
                   on_log: Callable[[Any], None] | None = None) -> dict:
    import fal_client

    def _on_update(update):
        if on_log and hasattr(update, "logs"):
            for line in update.logs or []:
                on_log(line.get("message", "") if isinstance(line, dict) else str(line))

    start = time.time()
    try:
        return fal_client.subscribe(model, arguments=arguments, with_logs=with_logs,
                                    on_queue_update=_on_update)
    except Exception as e:
        raise RuntimeError(f"fal subscribe fuer {model} nach {time.time() - start:.1f}s fehlgeschlagen: {e}") from e


def _fal_download(url: str, output_path: Path, *, min_bytes: int = 1024) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as resp, open(output_path, "wb") as f:
        while chunk := resp.read(1 << 16):
            f.write(chunk)
    size = output_path.stat().st_size
    if size < min_bytes:
        body = output_path.read_text(errors="replace")[:500]
        raise RuntimeError(f"Datei zu klein ({size} Bytes), vermutlich Fehler-JSON: {body}")
    return size


def _fal_is_error(result: dict | None) -> tuple[bool, str]:
    if not result:
        return True, "leeres Ergebnis"
    if isinstance(result, dict):
        if result.get("error"):
            return True, f"Fehlerfeld gesetzt: {str(result['error'])[:200]}"
        if result.get("status") == "FAILED":
            return True, f"status=FAILED: {str(result)[:200]}"
    return False, ""


def fal_generate(cfg: dict, prompt: str, ref_paths: list[Path], *, width: int, height: int,
                 quality: str, with_logs: bool = False) -> tuple[str, dict, dict]:
    """Lade Referenzen hoch, rufe das Modell, gib (bild_url, payload, roh_ergebnis) zurueck."""
    image_size: object = {"width": width, "height": height} if cfg["custom_size"] else f"{width}x{height}"
    payload: dict = {"prompt": prompt, "image_size": image_size, "quality": quality, "num_images": 1}

    if ref_paths:
        urls = []
        for ref in ref_paths:
            print(f"[fal] lade Referenz hoch: {ref.name}", flush=True)
            urls.append(_fal_upload(ref))
        payload["image_urls"] = urls
        model = cfg["edit"]
    else:
        model = cfg["t2i"]

    print(f"[fal] sende {model} ({width}x{height}, q={quality})...", flush=True)
    result = _fal_subscribe(model, payload, with_logs=with_logs,
                            on_log=(lambda m: print(f"  [fal] {m}", flush=True)) if with_logs else None)

    err, reason = _fal_is_error(result)
    if err:
        sys.exit(f"ERROR: fal meldet Fehler: {reason}")
    images = result.get("images") or []
    if not images or not images[0].get("url"):
        sys.exit(f"ERROR: kein Bild im Ergebnis: {result}")
    return images[0]["url"], payload, result


def fal_download(url: str, output_path: Path) -> int:
    return _fal_download(url, output_path)


def round16(n: int) -> int:
    """Auf das naechste positive Vielfache von 16 runden (fal-Regel fuer freie Groessen)."""
    return max(16, int(round(n / 16)) * 16)
