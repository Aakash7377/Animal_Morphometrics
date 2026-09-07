import os

import torch
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image


# =========================
# DEVICE
# =========================

device = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else (
        "mps"
        if torch.backends.mps.is_available()
        else "cpu"
    )
)

print(f"Using device: {device}")


# =========================
# IMAGE TRANSFORM
# =========================

transform = transforms.Compose([
    transforms.Resize((224, 224)),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# =========================
# MODEL PATH
# =========================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODELS_DIR = os.path.join(
    BASE_DIR,
    "models"
)

CHECKPOINT_PATH = os.path.join(
    MODELS_DIR,
    "cattle_breed_bestt.pth"
)


# =========================
# CHECK MODEL FILE
# =========================

if not os.path.exists(CHECKPOINT_PATH):

    raise FileNotFoundError(
        f"Model file not found: {CHECKPOINT_PATH}"
    )


# =========================
# LOAD CHECKPOINT
# =========================

try:

    checkpoint = torch.load(
        CHECKPOINT_PATH,
        map_location=device
    )

    print("Checkpoint loaded successfully.")

except Exception as e:

    raise RuntimeError(
        f"Failed to load checkpoint: {e}"
    )


# =========================
# GET CLASS NAMES
# =========================

if not isinstance(checkpoint, dict):

    raise RuntimeError(
        "Invalid checkpoint format."
    )


if "class_names" not in checkpoint:

    raise RuntimeError(
        "class_names not found in checkpoint."
    )


CLASSES = checkpoint["class_names"]

print("Classes:")
print(CLASSES)


# =========================
# CREATE RESNET50
# =========================

# IMPORTANT:
# Training was done using:
#
# model = models.resnet50(weights=weights)
# model.fc = nn.Linear(...)
#
# Therefore inference architecture
# must be exactly the same.

model = models.resnet50(
    weights=None
)


# =========================
# FINAL CLASSIFIER
# =========================

num_features = model.fc.in_features

model.fc = torch.nn.Linear(
    num_features,
    len(CLASSES)
)


# =========================
# GET STATE DICT
# =========================

if "model_state_dict" in checkpoint:

    state_dict = checkpoint[
        "model_state_dict"
    ]

elif "state_dict" in checkpoint:

    state_dict = checkpoint[
        "state_dict"
    ]

else:

    # In case checkpoint itself is state_dict
    state_dict = checkpoint


# =========================
# REMOVE module. PREFIX
# =========================

cleaned_state_dict = {}

for key, value in state_dict.items():

    if key.startswith("module."):

        key = key[7:]

    cleaned_state_dict[key] = value


# =========================
# LOAD TRAINED WEIGHTS
# =========================

try:

    model.load_state_dict(
        cleaned_state_dict,
        strict=True
    )

    print(
        "Successfully loaded trained "
        "cattle breed model."
    )

except Exception as e:

    raise RuntimeError(
        f"Failed to load model weights: {e}"
    )


# =========================
# MOVE MODEL TO DEVICE
# =========================

model = model.to(device)

model.eval()

print("Model ready for prediction.")


# =========================
# PREDICTION FUNCTION
# =========================

def predict_breed(image: Image.Image):

    """
    Predict cattle breed from a PIL image.

    Returns:
        raw_breed: predicted breed name
        raw_conf: confidence percentage
    """

    # Ensure RGB
    if image.mode != "RGB":

        image = image.convert("RGB")


    # =========================
    # PREPROCESS IMAGE
    # =========================

    img_tensor = transform(
        image
    ).unsqueeze(0).to(device)


    # =========================
    # MODEL INFERENCE
    # =========================

    with torch.no_grad():

        outputs = model(
            img_tensor
        )

        probabilities = torch.softmax(
            outputs,
            dim=1
        )

        confidence, pred_idx = torch.max(
            probabilities,
            dim=1
        )


    # =========================
    # GET PREDICTION
    # =========================

    predicted_index = pred_idx.item()

    raw_breed = CLASSES[
        predicted_index
    ]

    raw_conf = (
        confidence.item() * 100.0
    )


    return raw_breed, raw_conf


# =========================
# API COMPATIBILITY
# =========================

def predict(image: Image.Image):

    return predict_breed(image)