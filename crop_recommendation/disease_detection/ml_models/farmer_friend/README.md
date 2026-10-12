# FarmerFriend plant disease model (reference only)

Copied from [DevilStudio27/Plant-Disease-Detection-and-Solution](https://github.com/DevilStudio27/Plant-Disease-Detection-and-Solution)
(commit `1a3fb3b`, MIT licence, © 2020 Sahil Thakur; see `LICENSE`).

| File | What it is |
|---|---|
| `model.tflite` | TensorFlow Lite model from the Android app: input 200×200×3 (pixels / 255), 39 outputs |
| `labels.txt` | The app's class labels, in output order (38 PlantVillage classes + `background`) |
| `Plant_Disease_Detection_Classification_Updated.ipynb` | Training notebook (a 34-class run, 95.8% on PlantVillage validation) |

The project's disease solutions file (`data.json`) is a paid download and is not included.

## Not used by AgroSmart

This model is **not** wired into the app. Tested on 190 labelled PlantVillage photos
(5 per class), it predicted the right class for 2 (1%), about the same as guessing:
it gives almost identical scores to every class. The shipped `.tflite` does not
match the notebook (39 outputs vs 34 trained classes), so it is probably not the
trained model.

AgroSmart's disease detection uses `../plant_disease_model1.keras` with `../class_indices.json`
and `../disease_info.json`.
