#!/usr/bin/env python3
"""Sync tracked anime from local Animeko (Ani) SQLite DB + Bilibili public bangumi list
into src/data/anime.json.

- Local Ani entries keep local cached covers & exact episode playback progress.
- Bilibili entries (UID 499115598) use hdslb.com HTTPS covers (loaded with no-referrer)
  and are deduplicated against Ani / manual entries by normalized title.
- Existing manual entries & custom notes in src/data/anime.json are preserved.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sqlite3
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANI_DB = Path(os.environ.get("APPDATA", "")) / "Him188" / "Ani" / "data" / "ani_room_database_main.db"
OUT_JSON = ROOT / "src" / "data" / "anime.json"
COVER_DIR = ROOT / "public" / "images" / "anime" / "covers"
BILI_UID = "499115598"

ANI_STATUS_MAP = {
    "DOING": "watching",
    "DONE": "watched",
    "WISH": "wish",
    "ON_HOLD": "on_hold",
    "DROPPED": "dropped",
}

BILI_STATUS_MAP = {
    1: "wish",
    2: "watching",
    3: "watched",
}


def decode_val(v):
    if isinstance(v, bytes):
        return v.decode("utf-8", errors="ignore")
    return v


def norm_title(t: str) -> str:
    return re.sub(r"[\s！!？?：:·\-—（）()《》「」『』\[\]【】、。,.]+", "", (t or "").lower())


def parse_tags(raw) -> list[str]:
    if not raw:
        return []
    text = decode_val(raw)
    if not isinstance(text, str):
        return []
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
    for ext in ("webp", "jpg"):
        existing = COVER_DIR / f"bgm-{subject_id}.{ext}"
        if existing.exists() and existing.stat().st_size > 2000:
            return f"/images/anime/covers/bgm-{subject_id}.{ext}"
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
        return {"updatedAt": "", "source": "", "items": []}
    return json.loads(OUT_JSON.read_text(encoding="utf-8"))


def sync_ani(by_id: dict[str, dict]) -> int:
    if not ANI_DB.exists():
        print(f"[warn] Ani DB not found: {ANI_DB}")
        return 0
    count = 0
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
        for r in cur.fetchall():
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

            status = ANI_STATUS_MAP.get(str(r["collectionType"] or "").upper(), "watching")
            cover_url = decode_val(r["imageLarge"]) or decode_val(r["imageThumb"]) or ""
            local_cover = download_cover(sid, cover_url)

            prev = by_id.get(key, {})
            by_id[key] = {
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
            count += 1
        con.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return count


def sync_bilibili(by_id: dict[str, dict]) -> int:
    # Build normalized title set of higher-priority Ani/manual entries to avoid duplicates
    existing_titles = {
        norm_title(v.get("title", ""))
        for v in by_id.values()
        if v.get("source") in ("ani", "manual")
    }
    count = 0
    pn = 1
    ps = 30
    total = None
    while True:
        url = f"https://api.bilibili.com/x/space/bangumi/follow/list?type=1&vmid={BILI_UID}&pn={pn}&ps={ps}"
        res = subprocess.run(
            [
                "curl.exe",
                "-fsSL",
                "--max-time",
                "15",
                "-H",
                f"Referer: https://space.bilibili.com/{BILI_UID}/bangumi",
                "-H",
                "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                url,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if res.returncode != 0 or not res.stdout:
            print(f"[warn] bilibili page {pn} failed: rc={res.returncode}")
            break
        payload = json.loads(res.stdout)
        if payload.get("code") != 0:
            print(f"[warn] bilibili page {pn} error: {payload.get('message')}")
            break
        data = payload.get("data") or {}
        if total is None:
            total = int(data.get("total") or 0)
        lst = data.get("list") or []
        if not lst:
            break

        for idx, it in enumerate(lst):
            title = (it.get("title") or "").strip()
            if not title or norm_title(title) in existing_titles:
                continue
            sid = int(it.get("season_id") or 0)
            key = f"bili-{sid}"
            status = BILI_STATUS_MAP.get(int(it.get("follow_status") or 2), "watching")
            total_eps = int(it.get("total_count") or 0)
            if total_eps < 0:
                total_eps = 0
            watched = total_eps if (status == "watched" and total_eps > 0) else 0
            # Parse progress string if present (e.g. "看到第5话")
            prog = str(it.get("progress") or "")
            m = re.search(r"(\d+)", prog)
            if m:
                watched = int(m.group(1))
            cover = str(it.get("cover") or "").replace("http://", "https://")
            if cover and "@" not in cover:
                cover = cover + "@360w_480h.webp"
            styles = it.get("styles") or []
            tags = [str(s) for s in styles if isinstance(s, str)][:4]
            if not tags and it.get("season_type_name"):
                tags = [str(it["season_type_name"])]

            prev = by_id.get(key, {})
            by_id[key] = {
                "id": key,
                "seasonId": sid,
                "title": title,
                "originalTitle": "",
                "status": prev.get("statusOverride") or status,
                "watched": watched,
                "total": total_eps,
                "score": prev.get("score"),
                "bgmScore": None,
                "cover": cover,
                "tags": tags,
                "note": prev.get("note") or (it.get("badge") or ""),
                "url": it.get("url") or f"https://www.bilibili.com/bangumi/play/ss{sid}",
                "updatedAt": "",
                "order": (pn - 1) * ps + idx,
                "source": "bilibili",
            }
            count += 1

        if pn * ps >= total:
            break
        pn += 1
        time.sleep(0.15)
    return count


def sync() -> None:
    existing = load_existing()
    # Keep manual + ani entries first; rebuild bilibili entries fresh while preserving notes
    by_id: dict[str, dict] = {}
    bili_prev: dict[str, dict] = {}
    for it in existing.get("items", []):
        if it.get("source") == "bilibili":
            bili_prev[str(it.get("id"))] = it
        else:
            by_id[str(it.get("id"))] = it

    ani_cnt = sync_ani(by_id)
    # Pass previous bilibili notes through
    for k, v in bili_prev.items():
        if v.get("note") or v.get("score") or v.get("statusOverride"):
            by_id[k] = v
    bili_cnt = sync_bilibili(by_id)

    # Sort: Ani & manual entries first, then Bilibili by follow recency
    src_rank = {"ani": 0, "manual": 1, "bilibili": 2}
    status_rank = {"watching": 0, "watched": 1, "wish": 2, "on_hold": 3, "dropped": 4}
    items = sorted(
        by_id.values(),
        key=lambda x: (
            src_rank.get(x.get("source", "bilibili"), 9),
            status_rank.get(x.get("status", "watching"), 9),
            int(x.get("order", 999999)) if x.get("source") == "bilibili" else 0,
            -(int(x.get("updatedAt", "0000-00-00").replace("-", "") or 0)),
        ),
    )

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "updatedAt": datetime.now().strftime("%Y-%m-%d"),
        "source": "Animeko (Ani) + B站追番",
        "items": items,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Synced {ani_cnt} Ani + {bili_cnt} Bilibili -> total {len(items)} entries in {OUT_JSON}")


if __name__ == "__main__":
    sync()
