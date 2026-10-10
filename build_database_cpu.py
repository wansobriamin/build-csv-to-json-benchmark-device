"""
Build CPU PC database dari CSV staging -> database_cpu.json.
"""
import json
import re
import pandas as pd
from paths import STAGING_DIR, DB_DIR

CPU_CSV = STAGING_DIR / "benchmark_pc_cpu.csv"
CPU_DB = DB_DIR / "database_cpu.json"

# Ancor bridge
ANCHOR_CPU = "intel_core_i5_12400f"
ANCHOR_INDEX = 1100         

COMING_SOON = ("apple_", "snapdragon_x", "qualcomm_snapdragon_x")


def clean_text(s):
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return None
    s = re.sub(r"[\u200b\u200c\u200d\u2060\ufeff]", "", str(s))
    return re.sub(r"\s+", " ", s).strip()


def valid_name(n) -> bool:
    n = clean_text(n)
    return bool(n) and any(c.isalpha() for c in n) and len(n) > 2


def slug(s) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(s).lower()).strip("_").replace("_sore_", "_core_")


def main():
    if not CPU_CSV.exists():
        print(f"[skip] {CPU_CSV.name} tidak ada")
        return
    df = pd.read_csv(CPU_CSV)
    df["slug"] = [slug(s) for s in df.cpu_slug]
    df = df[df.cb_multi.notna() & (df.cb_multi > 0)]

    anchor_row = df[df["slug"] == ANCHOR_CPU]
    if anchor_row.empty:
        print(f"[ERROR] Anchor '{ANCHOR_CPU}' tidak ditemukan di CSV. Build dibatalkan.")
        return
    anchor_score = float(anchor_row.iloc[0]["cb_multi"])
    print(f"[INFO] Anchor: {ANCHOR_CPU} (cb_multi {anchor_score:.0f} -> index {ANCHOR_INDEX})")

    db = {}
    for _, r in df.iterrows():
        name = clean_text(r.name)
        if not valid_name(name):
            name = r.slug.replace("_", " ").title()
        coming = r.slug.startswith(COMING_SOON)

        cpu_index = int(round((float(r.cb_multi) / anchor_score) * ANCHOR_INDEX))

        db[r.slug] = {
            "name": name,
            "cpu_index": cpu_index,
            "cb_single": int(r.cb_single) if pd.notna(r.get("cb_single")) else None,
            "cb_multi": int(r.cb_multi),
            "form_factor": r.form_factor,
            "available": not coming,
            **({"status": "coming_soon"} if coming else {}),
            "index_source": {
                "metric": "cinebench2024_multi",
                "confidence": "nanoreview_bridge",
                "anchor": ANCHOR_CPU,
                "anchor_score": anchor_score,
                "anchor_index": ANCHOR_INDEX,
                "source_url": clean_text(r.source_url),
                "last_updated": str(r.get("updated", "")),
            },
        }

    CPU_DB.parent.mkdir(parents=True, exist_ok=True)
    CPU_DB.write_text(json.dumps(db, indent=2, ensure_ascii=False), encoding="utf-8")
    nd = sum(1 for v in db.values() if v.get("form_factor") == "desktop")
    nl = sum(1 for v in db.values() if v.get("form_factor") == "laptop")
    print(f"[OK] CPU PC: {len(db)} entri | desktop {nd} | laptop {nl}")


if __name__ == "__main__":
    main()