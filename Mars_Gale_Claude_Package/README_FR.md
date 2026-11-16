# Mars Trek → Gale → Claude

Ce paquet contient un script pour récupérer les couches NASA Mars Trek sélectionnées et les découper sur la zone de Gale.

## Emprise
- CRS : `EPSG:104905`
- Ouest : 133.294245933863°
- Sud : −9.346237321415312°
- Est : 141.5449782018324°
- Nord : −2.369919092173532°

## Couches à récupérer (7)
- `Gale_CTX_BlockAdj_dd`
- `Mars_MOLA_blend200ppx_HRSC_ClrShade_clon0dd_200mpp_lzw`
- `Mars_MGS_MOLA_ClrShade_merge_global_463m`
- `TES_Dust` (opacité initiale 0 %)
- `Mars_MGS_TES_Albedo_mosaic_global_7410m` (opacité initiale 0 %)
- `THEMIS_NightIR_ControlledMosaics_100m_v2_oct2018`
- `THEMIS_DayIR_ControlledMosaics_100m_v2_oct2018`

Les couches `Ausonia_CTX_BlockAdj_dd` et `olympus_mons.eq` sont sélectionnées dans le lien, mais leur couverture géographique est hors de Gale : elles sont répertoriées dans les métadonnées et exclues du découpage.

## Prérequis
- Python 3.9+
- GDAL installé avec le pilote WMTS (`gdalinfo` et `gdalwarp` disponibles dans le terminal)
- Accès Internet à `trek.nasa.gov`

Vérifie le pilote :
```bash
gdalinfo --formats
```
La liste doit contenir `WMTS`.

## Lancer le téléchargement
Dans le dossier extrait :
```bash
python download_gale_layers.py
```
Les fichiers GeoTIFF sont écrits dans `Gale_Mars_Trek/`.

Une seule couche :
```bash
python download_gale_layers.py --only Gale_CTX_BlockAdj_dd
```

Remplacer les fichiers déjà présents :
```bash
python download_gale_layers.py --overwrite
```

## Fichiers générés
- Un GeoTIFF par couche (`*_Gale.tif`)
- `rapport_extraction.json` : état, dimensions et taille
- `CATALOGUE_CLAUDE.md` : catalogue pour accompagner les rasters dans Claude
- `_diagnostics/` : journaux de diagnostic si un service ne répond pas

## À savoir
Le ZIP ne contient pas les rasters : il contient le téléchargeur et les métadonnées. Les GeoTIFF sont récupérés depuis les serveurs NASA lorsque le script est exécuté sur une machine disposant de GDAL et d'Internet. Le script essaie plusieurs formes d'URL GetCapabilities, car le service est WMTS et ses paramètres doivent être lus dans les capacités du service.

L'opacité de Mars Trek est seulement un réglage de visualisation. Les couches TES à 0 % sont donc téléchargées comme données, sans modifier leurs valeurs.

## Documentation
- Mars Trek WMTS : https://trek.nasa.gov/tiles/apidoc/trekAPI.html?body=mars
- Pilote WMTS GDAL : https://gdal.org/en/stable/drivers/raster/wmts.html
