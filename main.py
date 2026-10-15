import io
import os
from detector import CATTLE_DETECTION_THRESHOLD, detect_cattle
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from morphometrics import (
    extract_morphometrics,  # <--- NEW: Morphometrics module
)
from PIL import Image
from predict import predict, predict_all_breeds

app = FastAPI(
    title="Cattle Breed & Morphometrics API",
    description=(
        "AI-based cattle breed classification and physical morphometrics"
        " estimation using YOLOv8 and ResNet-50."
    ),
    version="2.1.0",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

if os.path.exists(STATIC_DIR):
  app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


@app.get("/", response_class=HTMLResponse)
async def get_index():
  index_path = os.path.join(TEMPLATES_DIR, "index.html")
  if not os.path.exists(index_path):
    raise HTTPException(status_code=404, detail="Index HTML file not found.")
  try:
    with open(index_path, "r", encoding="utf-8") as f:
      return HTMLResponse(content=f.read())
  except Exception as e:
    raise HTTPException(
        status_code=500, detail=f"Failed to load index page: {str(e)}"
    )


@app.get("/health")
async def health_check():
  return {
      "status": "ok",
      "message": "Cattle Breed & Morphometrics API is running",
      "cattle_detection_threshold": CATTLE_DETECTION_THRESHOLD,
  }


@app.post("/predict")
async def predict_image(file: UploadFile = File(...)):
  # 1. Validate File
  filename = file.filename or ""
  extension = os.path.splitext(filename)[1].lower()
  if extension not in ALLOWED_EXTENSIONS:
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "detail": (
                f"Invalid file format '{extension}'. Allowed formats are: JPG,"
                " JPEG, PNG."
            ),
        },
    )

  # 2. Read Image
  try:
    contents = await file.read()
    if not contents:
      return JSONResponse(
          status_code=400,
          content={"success": False, "detail": "Uploaded file is empty."},
      )
    image = Image.open(io.BytesIO(contents))
    image.verify()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
  except Exception as e:
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "detail": "Uploaded file could not be decoded as a valid image.",
        },
    )

  # 3. First-Stage Cattle Detection
  try:
    is_cattle, detect_conf, detected_class = detect_cattle(image)
  except Exception as e:
    print(f"YOLO detection exception: {str(e)}")
    is_cattle = False

  if not is_cattle:
    return JSONResponse(
        status_code=200,
        content={
            "success": False,
            "is_cattle": False,
            "message": "Not a cattle image",
            "predicted_breed": None,
            "confidence": None,
            "breed": None,
            "top_predictions": [],
            "morphometrics": None,
        },
    )

  # 4. Second-Stage Breed Prediction (ResNet)
  try:
    all_predictions = predict_all_breeds(image)
  except Exception as e:
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "detail": f"Breed prediction error: {str(e)}",
        },
    )

  # 5. Third-Stage Morphometrics Calculation (YOLOv8-Pose)
  try:
    morphometrics_data = extract_morphometrics(image)
  except Exception as e:
    print(f"Morphometrics calculation error: {str(e)}")
    morphometrics_data = {"calculated": False, "error": str(e)}

  # Format Breed Results
  top_predictions = []
  for item in all_predictions[:5]:
    formatted_b = item["raw_breed"].replace("_", " ").title()
    conf = round(float(item["confidence"]), 1)
    top_predictions.append({"breed": formatted_b, "confidence": conf})

  main_pred = top_predictions[0]

  # 6. Unified API Response
  return JSONResponse(
      content={
          "success": True,
          "is_cattle": True,
          "message": "Cattle detected and analyzed successfully",
          "predicted_breed": main_pred["breed"],
          "confidence": main_pred["confidence"],
          "breed": main_pred["breed"],
          "top_predictions": top_predictions,
          "morphometrics": morphometrics_data,  # <--- Added morphometrics output
          "detection": {"class": detected_class, "confidence": float(detect_conf)},
      }
  )


if __name__ == "__main__":
  import uvicorn

  uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)