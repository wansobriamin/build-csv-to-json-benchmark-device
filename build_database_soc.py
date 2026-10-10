"""
Build Mobile SoC database dari CSV staging -> database_soc.json.
"""
import json
import re
import pandas as pd
from paths import STAGING_DIR, DB_DIR, RAW_DIR

CSV = STAGING_DIR / "benchmark_soc.csv"
DETAILS = RAW_DIR / "details_cache.json"
OUT = DB_DIR / "database_soc.json"

GPU_SUB_ANCHOR = 125449.0
TOTAL_ANCHOR = 824513.0 
GB6_SINGLE_REF = 1300.0 

VENDOR_PREFIXES = (
    "qualcomm_", "mediatek_", "samsung_", "hisilicon_",
    "unisoc_", "google_", "xiaomi_", "apple_",
)
SERIES_VENDOR = {
    "snapdragon": "qualcomm", "dimensity": "mediatek", "helio": "mediatek",
    "exynos": "samsung", "tensor": "google", "kirin": "hisilicon",
    "unisoc": "unisoc", "t": "unisoc", "xring": "xiaomi",
}


def canon(s: str) -> str:
    s = str(s).strip().lower().replace("_sore_", "_core_")
    for p in VENDOR_PREFIXES:
        if s.startswith(p):
            s = s[len(p):]
            break
    return s


def series_of(key: str) -> str:
    return key.split("_")[0]


def vendor_of(key: str) -> str:
    if re.match(r"^[am]\d+", key):          
        return "apple"
    return SERIES_VENDOR.get(series_of(key), "unknown")


def _val(r, *names):
    for n in names:
        v = r.get(n)
        if v is not None and not (isinstance(v, float) and pd.isna(v)):
            return v
    return None


def load_details() -> dict:
    if not DETAILS.exists():
        return {}
    try:
        raw = json.loads(DETAILS.read_text(encoding="utf-8"))
        return {canon(k): v for k, v in raw.items()}
    except Exception:
        return {}


def main():
    df = pd.read_csv(CSV)
    details = load_details()
    db = {}
    n_sub = n_tot = n_gb = n_skip = 0

    for _, r in df.iterrows():
        raw_slug = r.get("soc_slug")
        if pd.isna(raw_slug):
            n_skip += 1
            continue
        key = canon(raw_slug)
        d = details.get(key, {})

        gpu_name = _val(r, "gpu_name") or d.get("gpu_name")
        gpu_slug = _val(r, "gpu_slug") or key

        sub = _val(r, "antutu_gpu", "antutu_v10_gpu") or d.get("antutu10_gpu")
        total = _val(r, "antutu_total", "antutu10_total")
        gb6s = _val(r, "geekbench6_single", "geekbench6_compute")
        gb6m = _val(r, "geekbench6_multi")

        if sub:
            idx, conf = int(round(1000.0 * float(sub) / GPU_SUB_ANCHOR)), "benchmark"
            n_sub += 1
        elif total:
            idx, conf = int(round(1000.0 * float(total) / TOTAL_ANCHOR)), "proxy_antutu_total"
            n_tot += 1
        elif gb6s:
            idx, conf = int(round(float(gb6s) * 2.2)), "gb6_bridge" 
            n_gb += 1
        else:
            idx, conf = 0, "needs_review"

        cpu_index = int(round(1000.0 * float(gb6s) / GB6_SINGLE_REF)) if gb6s else 0

        vendor = vendor_of(key)
        platform = "ios" if vendor == "apple" else "android"
        gpu_vendor = next((v for v in ("adreno", "mali", "xclipse", "apple")
                           if str(gpu_slug).startswith(v)), vendor)

        name = key.replace("_", " ").title()
        if vendor == "apple":
            name = "Apple " + name

        db[key] = {
            "name": name,
            "platform": platform,
            "vendor": vendor,
            "series": series_of(key),
            "gpu_slug": gpu_slug,
            "gpu_name": gpu_name,
            "gpu_vendor": gpu_vendor,
            "gpu_index": idx,
            "cpu_index": cpu_index,
            "opengl_es": "3.2",
            "vulkan": "1.1",
            "ray_tracing": False,
            "available": True,
            "index_source": {
                "antutu_gpu": int(sub) if sub else None,
                "antutu_total": int(total) if total else None,
                "geekbench6_single": int(gb6s) if gb6s else None,
                "geekbench6_multi": int(gb6m) if gb6m else None,
                "confidence": conf,
                "source_url": r.get("source_url"),
                "last_updated": r.get("updated"),
            },
        }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(db, indent=2, ensure_ascii=False), encoding="utf-8")
    ios = sum(1 for v in db.values() if v["platform"] == "ios")
    print(f"[OK] SoC: {len(db)} entri | ios {ios} | android {len(db) - ios}")
    print(f"     gpu_index: subscore={n_sub}, total={n_tot}, gb6={n_gb}, skip={n_skip}")


if __name__ == "__main__":
    main()
    