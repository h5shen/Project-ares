# Instructions pour Claude — rasters de la région de Gale

Commence par lire `layers_metadata.json`, `rapport_extraction.json` et `CATALOGUE_CLAUDE.md`.

- Vérifie le CRS, les dimensions, les bandes, les valeurs NoData et les pixels transparents de chaque GeoTIFF.
- Distingue les images CTX et THEMIS des couches topographiques MOLA/HRSC et des produits TES.
- Les couches TES ont une opacité initiale de 0 % dans Mars Trek, mais leurs valeurs raster restent des données à analyser.
- Ne suppose pas que les couches ont la même résolution. Avant toute comparaison pixel à pixel, indique la reprojection et la méthode de rééchantillonnage.
- Identifie les zones sans couverture et les pixels NoData; ne les interprète pas comme des zéros scientifiques.
- Cite le nom du fichier et l'identifiant de couche pour chaque observation.
- N'analyse pas une couche dont le téléchargement est marqué `failed`.

Emprise commune : 133.294245933863, -9.346237321415312, 141.5449782018324, -2.369919092173532 (Ouest, Sud, Est, Nord), CRS EPSG:104905.
