#!/usr/bin/env bash
# Downloads the crop recommendation training data into ml/crop/data/raw (~550 MB).
#   - MapSPAM 2010 v2.0 (IFPRI, CC BY 4.0): harvested area and yield per crop, 5 arc-minute grid
#   - WorldClim 2.1 (CC BY 4.0): monthly rainfall and temperature normals and elevation, 2.5 arc-minute grid
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p data/raw && cd data/raw

DATAVERSE=https://dataverse.harvard.edu/api/access/datafile
WORLDCLIM=https://geodata.ucdavis.edu/climate/worldclim/2_1/base

get() {  # get <file> <url>: download once, resumable
  [ -f "$1.done" ] && { echo "have $1"; return; }
  echo "downloading $1 ..."
  curl -L --fail --retry 5 --retry-delay 10 -C - -o "$1" "$2"
  touch "$1.done"
}

get spam2010_readme.txt        "$DATAVERSE/3984174"
get spam2010_harv_area.csv.zip "$DATAVERSE/3984976"
get spam2010_yield.csv.zip     "$DATAVERSE/3984974"
get wc2.1_2.5m_prec.zip        "$WORLDCLIM/wc2.1_2.5m_prec.zip"
get wc2.1_2.5m_tavg.zip        "$WORLDCLIM/wc2.1_2.5m_tavg.zip"
get wc2.1_2.5m_elev.zip        "$WORLDCLIM/wc2.1_2.5m_elev.zip"
echo "all downloads complete"
