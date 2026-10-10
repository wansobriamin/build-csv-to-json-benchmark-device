"""
Build GPU PC database dari CSV staging -> database_gpu.json.
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path

from paths import STAGING_DIR, DB_DIR

CSV_PATH = STAGING_DIR / "benchmark_pc_gpu.csv"
OUT_PATH = DB_DIR / "database_gpu.json"

# Ancor bridge
ANCHOR_GPU = "nvidia_rtx_3060"
ANCHOR_INDEX = 18100


def main():
    if not CSV_PATH.exists():
        print(f"[ERROR] {CSV_PATH} tidak ditemukan. Jalankan scraper PC dulu.")
        return

    df = pd.read_csv(CSV_PATH)
    
    anchor_row = df[df["gpu_slug"] == ANCHOR_GPU]
    if anchor_row.empty:
        print(f"[WARN] Anchor {ANCHOR_GPU} tidak ditemukan, gunakan skor absolut")
        anchor_score = None
    else:
        anchor_score = anchor_row.iloc[0]["primary_score"]
        print(f"[INFO] Anchor: {ANCHOR_GPU} (score: {anchor_score})")
    
    db = {}
    for _, row in df.iterrows():
        gpu_slug = row["gpu_slug"]
        if pd.isna(gpu_slug):
            continue
        
        if anchor_score:
            gpu_index = int((row["primary_score"] / anchor_score) * ANCHOR_INDEX)
        else:
            gpu_index = int(row["primary_score"])
        
        vendor = "unknown"
        for v in ["nvidia", "amd", "intel"]:
            if v in gpu_slug:
                vendor = v
                break
        
        ray_tracing = any(x in gpu_slug for x in ["rtx", "rx_6", "rx_7", "arc"])
        
        db[gpu_slug] = {
            "name": str(row.get("name", gpu_slug)).replace("_", " ").title(),
            "vendor": vendor,
            "gpu_index": gpu_index,
            "form_factor": row.get("form_factor", "desktop"),
            "gflops": None, 
            "opengl_es": "4.6" if vendor == "nvidia" else "4.5",
            "vulkan": "1.3" if vendor in ["nvidia", "amd"] else "1.2",
            "directx": 12,
            "ray_tracing": ray_tracing,
            "index_source": {
                "primary_score": int(row["primary_score"]),
                "score_3dmark": int(row["score_3dmark"]) if pd.notna(row.get("score_3dmark")) else None,
                "score_geekbench": int(row["score_geekbench"]) if pd.notna(row.get("score_geekbench")) else None,
                "source": row.get("source"),
                "source_url": row.get("source_url"),
                "last_updated": row.get("updated"),
                "confidence": row.get("confidence"),
            }
        }
    
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] {len(db)} GPU PC -> {OUT_PATH}")
    
    desktop_count = sum(1 for v in db.values() if v.get("form_factor") == "desktop")
    laptop_count = sum(1 for v in db.values() if v.get("form_factor") == "laptop")
    print(f"  Desktop: {desktop_count}, Laptop: {laptop_count}")


if __name__ == "__main__":
    main()