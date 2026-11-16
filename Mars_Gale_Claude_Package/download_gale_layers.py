#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Télécharge les couches Mars Trek et les découpe sur l'emprise Gale.
Prérequis : GDAL (gdalinfo + gdalwarp) avec pilote WMTS et connexion Internet.
"""
import argparse, json, shutil, subprocess, sys, time
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
META = ROOT / "layers_metadata.json"

def run(cmd, log=None):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       text=True, encoding="utf-8", errors="replace")
    if log:
        Path(log).write_text(p.stdout, encoding="utf-8")
    return p.returncode, p.stdout

def cap_urls(layer_id):
    root = "https://trek.nasa.gov/tiles/Mars/EQ/" + quote(layer_id, safe="")
    return [
        root + "/WMTSCapabilities.xml",
        root + "/1.0.0/WMTSCapabilities.xml",
        root + "?SERVICE=WMTS&REQUEST=GetCapabilities"
    ]

def open_wmts(layer_id, diagnostics):
    failures = []
    for n, url in enumerate(cap_urls(layer_id), 1):
        source = f"WMTS:{url},layer={layer_id}"
        code, output = run(["gdalinfo", source], diagnostics / f"{layer_id}_probe_{n}.log")
        if code == 0:
            return source, url
        failures.append(f"{url}\n{output[-1200:]}")
    raise RuntimeError("Aucune URL GetCapabilities n'a permis d'ouvrir la couche :\n" + "\n---\n".join(failures))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="Gale_Mars_Trek")
    parser.add_argument("--only", nargs="*", help="ID(s) de couche à télécharger")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    for exe in ("gdalinfo", "gdalwarp"):
        if not shutil.which(exe):
            sys.exit(f"ERREUR : {exe} est introuvable. Installe GDAL avec le pilote WMTS.")

    meta = json.loads(META.read_text(encoding="utf-8"))
    bb = meta["bbox"]
    out = Path(args.out).resolve()
    diag = out / "_diagnostics"
    out.mkdir(parents=True, exist_ok=True)
    diag.mkdir(exist_ok=True)

    selected = [x for x in meta["layers"] if x["gale_extract"]]
    if args.only:
        wanted = set(args.only)
        selected = [x for x in selected if x["id"] in wanted]
        absent = wanted - {x["id"] for x in selected}
        if absent:
            print("Non trouvées ou hors Gale :", ", ".join(sorted(absent)))

    report = {
        "source": meta["source"], "crs": meta["crs"], "bbox": bb,
        "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "excluded_outside_gale": ["Ausonia_CTX_BlockAdj_dd", "olympus_mons.eq"],
        "results": []
    }

    for layer in selected:
        lid = layer["id"]
        target = out / f"{lid}_Gale.tif"
        item = {"id":lid, "file":target.name, "opacity_in_mars_trek":layer["opacity"]}
        print(f"\n=== {lid} ===", flush=True)
        if target.exists() and not args.overwrite:
            item["status"] = "already_exists"
            report["results"].append(item)
            print("Déjà présent — conservé.")
            continue
        try:
            source, cap = open_wmts(lid, diag)
            item["capabilities_url"] = cap
            cmd = [
                "gdalwarp","-overwrite","-multi",
                "-t_srs",meta["crs"],"-te_srs",meta["crs"],
                "-te",str(bb["west"]),str(bb["south"]),str(bb["east"]),str(bb["north"]),
                "-r","near","-dstalpha",
                "-co","TILED=YES","-co","COMPRESS=DEFLATE",
                "-co","PREDICTOR=2","-co","BIGTIFF=IF_SAFER",
                source,str(target)
            ]
            code, output = run(cmd, diag / f"{lid}_gdalwarp.log")
            if code != 0 or not target.exists() or target.stat().st_size == 0:
                raise RuntimeError(output[-2500:] or "gdalwarp a échoué.")
            info_code, info = run(["gdalinfo","-json",str(target)])
            if info_code == 0:
                try:
                    obj = json.loads(info)
                    item["size_pixels"] = obj.get("size")
                    item["bands"] = len(obj.get("bands",[]))
                except Exception:
                    pass
            item["file_size_bytes"] = target.stat().st_size
            item["status"] = "downloaded"
            print(f"OK : {target} ({target.stat().st_size:,} octets)", flush=True)
        except Exception as exc:
            item["status"] = "failed"
            item["error"] = str(exc)
            print("ÉCHEC :", exc, flush=True)
        report["results"].append(item)

    report["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    (out/"rapport_extraction.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    lines = [
        "# Catalogue des rasters — Gale","",
        f"- Source : {meta['source']}",f"- CRS : `{meta['crs']}`",
        f"- Emprise : `{bb['west']}, {bb['south']}, {bb['east']}, {bb['north']}`",
        "- Format : GeoTIFF compressé, géoréférencé","","## Résultats",""
    ]
    for r in report["results"]:
        lines += [f"### `{r['id']}`",f"- Statut : **{r['status']}**",
                  f"- Opacité initiale Mars Trek : {r['opacity_in_mars_trek']*100:.0f} %"]
        if r.get("size_pixels"): lines.append(f"- Dimensions : {r['size_pixels']}")
        if r.get("error"): lines.append(f"- Erreur : {r['error']}")
        lines.append("")
    lines += ["## Sélectionnées mais hors de Gale","","- `Ausonia_CTX_BlockAdj_dd`","- `olympus_mons.eq`","",
              "L'opacité est un réglage d'affichage, pas une valeur scientifique du raster."]
    (out/"CATALOGUE_CLAUDE.md").write_text("\n".join(lines),encoding="utf-8")
    succeeded = sum(r["status"] in ("downloaded","already_exists") for r in report["results"])
    print(f"\n{ succeeded }/{len(report['results']) } couche(s) disponibles.")
    if succeeded == 0:
        sys.exit(2)

if __name__ == "__main__":
    main()
