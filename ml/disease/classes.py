"""
The classes the AgroSmart disease model predicts, and how each dataset's labels map onto them.

Class names follow the PlantVillage style "Crop___Condition" and must match the
keys in crop_recommendation/disease_detection/ml_models/disease_info.json.
"""

PLANTVILLAGE = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Blueberry___healthy",
    "Cherry_(including_sour)___Powdery_mildew",
    "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Raspberry___healthy",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
]

# Tanzania maize dataset (NM-AIST / TARI). Its "healthy" folds into PlantVillage's healthy maize.
TANZANIA_MAIZE = {
    "mln": "Corn_(maize)___Maize_lethal_necrosis",
    "msv": "Corn_(maize)___Maize_streak_virus",
    "healthy": "Corn_(maize)___healthy",
}

# Makerere / iCassava dataset folder names
CASSAVA = {
    "cbb": "Cassava___bacterial_blight",
    "cbsd": "Cassava___brown_streak_disease",
    "cgm": "Cassava___green_mottle",
    "cmd": "Cassava___mosaic_disease",
    "healthy": "Cassava___healthy",
}

# Makerere iBean dataset folder names
BEANS = {
    "angular_leaf_spot": "Bean___angular_leaf_spot",
    "bean_rust": "Bean___rust",
    "healthy": "Bean___healthy",
}

# PlantDoc class labels (real-world photos) -> PlantVillage classes
PLANTDOC = {
    "Apple Scab Leaf": "Apple___Apple_scab",
    "Apple leaf": "Apple___healthy",
    "Apple rust leaf": "Apple___Cedar_apple_rust",
    "Bell_pepper leaf spot": "Pepper,_bell___Bacterial_spot",
    "Bell_pepper leaf": "Pepper,_bell___healthy",
    "Blueberry leaf": "Blueberry___healthy",
    "Cherry leaf": "Cherry_(including_sour)___healthy",
    "Corn Gray leaf spot": "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn leaf blight": "Corn_(maize)___Northern_Leaf_Blight",
    "Corn rust leaf": "Corn_(maize)___Common_rust_",
    "Peach leaf": "Peach___healthy",
    "Potato leaf early blight": "Potato___Early_blight",
    "Potato leaf late blight": "Potato___Late_blight",
    "Raspberry leaf": "Raspberry___healthy",
    "Soyabean leaf": "Soybean___healthy",
    "Squash Powdery mildew leaf": "Squash___Powdery_mildew",
    "Strawberry leaf": "Strawberry___healthy",
    "Tomato Early blight leaf": "Tomato___Early_blight",
    "Tomato Septoria leaf spot": "Tomato___Septoria_leaf_spot",
    "Tomato leaf bacterial spot": "Tomato___Bacterial_spot",
    "Tomato leaf late blight": "Tomato___Late_blight",
    "Tomato leaf mosaic virus": "Tomato___Tomato_mosaic_virus",
    "Tomato leaf yellow virus": "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato leaf": "Tomato___healthy",
    "Tomato mold leaf": "Tomato___Leaf_Mold",
    "Tomato two spotted spider mites leaf": "Tomato___Spider_mites Two-spotted_spider_mite",
    "grape leaf black rot": "Grape___Black_rot",
    "grape leaf": "Grape___healthy",
}

CLASSES = sorted(
    set(PLANTVILLAGE)
    | set(TANZANIA_MAIZE.values())
    | set(CASSAVA.values())
    | set(BEANS.values())
)
CLASS_INDEX = {name: i for i, name in enumerate(CLASSES)}

# Sources whose photos are taken in real fields (used to judge real-world accuracy)
FIELD_SOURCES = {"plantdoc", "tanzania_maize", "cassava", "beans"}
