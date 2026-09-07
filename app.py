import io
import os

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image

from predict import predict


# =========================
# FASTAPI APP
# =========================

app = FastAPI(
    title="Cattle Breed Prediction API",
    description=(
        "AI-based cattle breed classification "
        "using trained ResNet50 model"
    ),
    version="2.0.0"
)


# =========================
# DIRECTORY PATHS
# =========================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

STATIC_DIR = os.path.join(
    BASE_DIR,
    "static"
)

TEMPLATES_DIR = os.path.join(
    BASE_DIR,
    "templates"
)


# =========================
# STATIC FILES
# =========================

if os.path.exists(STATIC_DIR):
    app.mount(
        "/static",
        StaticFiles(directory=STATIC_DIR),
        name="static"
    )


# =========================
# ALLOWED FILE TYPES
# =========================

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png"
}


# =========================
# HOME PAGE
# =========================

@app.get(
    "/",
    response_class=HTMLResponse
)
async def get_index():

    index_path = os.path.join(
        TEMPLATES_DIR,
        "index.html"
    )

    if not os.path.exists(index_path):
        raise HTTPException(
            status_code=404,
            detail="Index HTML file not found."
        )

    try:
        with open(
            index_path,
            "r",
            encoding="utf-8"
        ) as f:
            content = f.read()

        return HTMLResponse(
            content=content
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load index page: {str(e)}"
        )


# =========================
# HEALTH CHECK
# =========================

@app.get("/health")
async def health_check():

    return {
        "status": "ok",
        "message": "Cattle Breed Prediction API is running"
    }


# =========================
# PREDICTION API
# =========================

@app.post("/predict")
async def predict_image(
    file: UploadFile = File(...)
):

    # =========================
    # 1. VALIDATE FILE NAME
    # =========================

    filename = file.filename or ""

    extension = os.path.splitext(
        filename
    )[1].lower()

    if extension not in ALLOWED_EXTENSIONS:

        return JSONResponse(
            status_code=400,
            content={
                "detail": (
                    f"Invalid file format '{extension}'. "
                    "Allowed formats are: JPG, JPEG, PNG."
                )
            }
        )


    # =========================
    # 2. READ IMAGE
    # =========================

    try:

        contents = await file.read()

        if not contents:

            return JSONResponse(
                status_code=400,
                content={
                    "detail": "Uploaded file is empty."
                }
            )

        # Open image
        image = Image.open(
            io.BytesIO(contents)
        )

        # Verify image
        image.verify()

        # Re-open after verification
        image = Image.open(
            io.BytesIO(contents)
        ).convert("RGB")

    except Exception as e:

        print(
            "Image processing error:",
            str(e)
        )

        return JSONResponse(
            status_code=400,
            content={
                "detail": (
                    "Uploaded file could not be "
                    "decoded as a valid image."
                )
            }
        )


    # =========================
    # 3. MODEL PREDICTION
    # =========================

    try:

        raw_breed, raw_conf = predict(
            image
        )

    except Exception as e:

        print(
            "Prediction error:",
            str(e)
        )

        return JSONResponse(
            status_code=500,
            content={
                "detail": (
                    f"Model prediction error: {str(e)}"
                )
            }
        )


    # =========================
    # 4. FORMAT RESULT
    # =========================

    formatted_breed = (
        raw_breed
        .replace("_", " ")
        .title()
    )

    confidence = round(
        float(raw_conf),
        2
    )


    # =========================
    # 5. API RESPONSE
    # =========================

    return JSONResponse(
        content={
            "breed": formatted_breed,
            "confidence": confidence
        }
    )


# =========================
# RUN SERVER
# =========================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )