#!/usr/bin/env bash
# Downloads the public datasets used to train the disease model into ml/disease/data/raw.
# Safe to re-run: finished files are skipped and partial downloads resume.
set -euo pipefail
cd "$(dirname "$0")/data/raw"

get() {  # get <file> <url>
  if [ -f "$1.done" ]; then echo "already have $1"; return; fi
  echo "downloading $1 ..."
  curl -L --fail --retry 5 --retry-delay 10 -C - -o "$1" "$2"
  touch "$1.done"
}

HF=https://huggingface.co/datasets
ZENODO=https://zenodo.org/records/15685236/files

# Beans (Makerere AI Lab, MIT): angular leaf spot, bean rust, healthy
get beans_train.zip      "$HF/AI-Lab-Makerere/beans/resolve/main/data/train.zip"
get beans_validation.zip "$HF/AI-Lab-Makerere/beans/resolve/main/data/validation.zip"
get beans_test.zip       "$HF/AI-Lab-Makerere/beans/resolve/main/data/test.zip"

# PlantDoc (real-world photos, CC BY 4.0)
get plantdoc_0.parquet "$HF/geraldmc/plantdoc-full/resolve/main/data/train-00000-of-00002.parquet"
get plantdoc_1.parquet "$HF/geraldmc/plantdoc-full/resolve/main/data/train-00001-of-00002.parquet"

# Cassava (Makerere / iCassava, field photos)
get cassava.zip "https://storage.googleapis.com/emcassavadata/cassavaleafdata.zip"

# PlantVillage (official, CC BY-SA 3.0) + its official train/test split
get plantvillage.zip       "$HF/mohanty/PlantVillage/resolve/main/data.zip"
get pv_color_train.txt     "$HF/mohanty/PlantVillage/resolve/main/splits/color_train.txt"
get pv_color_test.txt      "$HF/mohanty/PlantVillage/resolve/main/splits/color_test.txt"

# Tanzania maize: MLN, MSV, healthy (NM-AIST & TARI, CC BY 4.0) - one part per class
get tz_mln1.zip     "$ZENODO/mln1.zip?download=1"
get tz_msv1.zip     "$ZENODO/msv1.zip?download=1"
get tz_healthy1.zip "$ZENODO/healthy1.zip?download=1"

echo "all downloads complete"
