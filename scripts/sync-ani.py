#!/usr/bin/env python3
"""Sync tracked anime from local Animeko (Ani) SQLite DB into src/data/anime.json.

Preserves manually added entries and custom notes in src/data/anime.json,
and caches cover art locally under public/images/anime/covers/ as WebP.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sqlite3
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANI_DB = Path(os.environ.get("APPDATA", "")) / "Him188" / "Ani" / "data" / "ani_room_database_main.db"
OUT_JSON = ROOT / "src" / "data" / "anime.json"
COVER_DIR = ROOT / "public" / "images" / "anime" / "covers"

STATUS_MAP = {
    "DOING": "watching",
    "DONE": "watched",
    "WISH": "wish",
    "ON_HOLD": "on_hold",
    "DROPPED": "dropped",
}


def decode_val(v):
    if isinstance(v, bytes):
        return v.decode("utf-8", errors="ignore")
    return v


def parse_tags(raw) -> list[str]:
    if not raw:
        return []
    text = decode_val(raw)
    if not isinstance(text, str):
        return []
    # Strip protobuf wire/control bytes and extract clean tag tokens
    skip = {"TV", "日本", "2026", "2026年10月", "动画", "漫改"}
    tokens = []
    for part in re.split(r"[\x00-\x1f,，]+", text):
        t = part.strip()
        if not t or len(t) < 2 or len(t) > 16:
            continue
        if t in skip or t.isdigit():
            continue
        if t not in tokens:
            tokens.append(t)
    return tokens[:4]


def download_cover(subject_id: int, url: str) -> str:
    COVER_DIR.mkdir(parents=True, exist_ok=True)
    target = COVER_DIR / f"bgm-{subject_id}.webp"
    rel = f"/images/anime/covers/bgm-{subject_id}.webp"
    if target.exists() and target.stat().st_size > 2000:
        return rel
    if not url:
        return ""
    try:
        res = subprocess.run(
            ["curl.exe", "-fsSL", "--max-time", "20", "-A", "Mozilla/5.0", url],
            capture_output=True,
            check=True,
        )
        data = res.stdout
        if len(data) < 1000:
            raise ValueError("downloaded cover too small")
        try:
            from io import BytesIO
            from PIL import Image

            img = Image.open(BytesIO(data)).convert("RGB")
            img.thumbnail((480, 680))
            img.save(target, "WEBP", quality=84, method=5)
            return rel
        except Exception:
            jpg = COVER_DIR / f"bgm-{subject_id}.jpg"
            jpg.write_bytes(data)
            return f"/images/anime/covers/bgm-{subject_id}.jpg"
    except Exception as exc:
        print(f"[warn] failed to download cover for {subject_id}: {exc}")
        return url


def ms_to_date(ms) -> str:
    if not ms:
        return ""
    try:
        val = int(ms)
        if val > 10_000_000_000:
            val = val / 1000.0
        return datetime.fromtimestamp(val, tz=timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        return ""


def load_existing() -> dict:
    if not OUT_JSON.exists():
        return {"updatedAt": "", "source": "Animeko (Ani) + 手动整理", "items": []}
    return json.loads(OUT_JSON.read_text(encoding="utf-8"))


def sync() -> None:
    if not ANI_DB.exists():
        raise SystemExit(f"Ani DB not found: {ANI_DB}")

    existing = load_existing()
    by_id: dict[str, dict] = {str(it.get("id")): it for it in existing.get("items", [])}

    tmp = tempfile.mkdtemp(prefix="ani_sync_")
    try:
        for ext in ("", "-wal", "-shm"):
            src = Path(str(ANI_DB) + ext)
            if src.exists():
                shutil.copy2(src, Path(tmp) / f"db.sqlite{ext}")

        con = sqlite3.connect(Path(tmp) / "db.sqlite")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(
            """
            SELECT subjectId, name, nameCn, imageLarge, imageThumb, totalEpisodes,
                   airDate, tags, collectionType, rating_score, self_rating_score,
                   self_rating_comment, lastUpdated
            FROM subject_collection
            ORDER BY lastUpdated DESC
            """
        )
        rows = cur.fetchall()
        for r in rows:
            sid = int(r["subjectId"])
            key = f"bgm-{sid}"
            cur.execute(
                "SELECT COUNT(*) FROM episode_collection WHERE subjectId = ? AND selfCollectionType = 'DONE'",
                (sid,),
            )
            done_ep = int(cur.fetchone()[0] or 0)
            cur.execute(
                "SELECT MAX(episodeSort), MAX(updatedAtMillis) FROM playback_history_record WHERE subjectId = ? AND deletedAtMillis IS NULL",
                (sid,),
            )
            max_sort, last_watch = cur.fetchone()
            cur.execute(
                "SELECT COUNT(*) FROM episode_collection WHERE subjectId = ? AND episodeType = 'MainStory'",
                (sid,),
            )
            main_eps = int(cur.fetchone()[0] or 0)

            total_eps = int(r["totalEpisodes"] or main_eps or 0)
            # Some multi-season Bangumi entries use cumulative episodeSort (e.g. 55 for S3E7)
            hist_watched = 0
            if max_sort:
                ms_int = int(max_sort)
                if total_eps > 0 and ms_int > total_eps:
                    cur.execute(
                        "SELECT COUNT(*) FROM episode_collection WHERE subjectId = ? AND episodeType = 'MainStory' AND sortNumber <= ?",
                        (sid, float(max_sort)),
                    )
                    hist_watched = int(cur.fetchone()[0] or 0)
                else:
                    hist_watched = ms_int
            watched = max(done_ep, hist_watched)

            status = STATUS_MAP.get(str(r["collectionType"] or "").upper(), "watching")
            cover_url = decode_val(r["imageLarge"]) or decode_val(r["imageThumb"]) or ""
            local_cover = download_cover(sid, cover_url)

            prev = by_id.get(key, {})
            entry = {
                "id": key,
                "subjectId": sid,
                "title": decode_val(r["nameCn"]) or decode_val(r["name"]),
                "originalTitle": decode_val(r["name"]) or "",
                "status": prev.get("statusOverride") or status,
                "watched": watched,
                "total": total_eps,
                "score": float(r["self_rating_score"]) if r["self_rating_score"] else (float(prev["score"]) if prev.get("score") else None),
                "bgmScore": round(float(r["rating_score"]), 1) if r["rating_score"] else None,
                "cover": local_cover,
                "tags": prev.get("tags") or parse_tags(r["tags"]),
                "note": decode_val(r["self_rating_comment"]) or prev.get("note") or "",
                "url": f"https://bgm.tv/subject/{sid}",
                "updatedAt": ms_to_date(last_watch) or ms_to_date(r["lastUpdated"]) or prev.get("updatedAt") or "",
                "source": "ani",
            }
            by_id[key] = entry
        con.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # Sort: watching first, then watched, wish, on_hold, dropped; newest updatedAt first
    order = {"watching": 0, "watched": 1, "wish": 2, "on_hold": 3, "dropped": 4}
    items = sorted(
        by_id.values(),
        key=lambda x: (order.get(x.get("status", "watching"), 9), -(int(x.get("updatedAt", "0000-00-00").replace("-", "") or 0))),
    )

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "updatedAt": datetime.now().strftime("%Y-%m-%d"),
        "source": "Animeko (Ani) 本地同步 + 手动整理",
        "items": items,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Synced {len(items)} anime entries -> {OUT_JSON}")


if __name__ == "__main__":
    sync()
