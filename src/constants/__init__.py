import os
from datetime import date

# Data Ingestion Constants
PIPELINE_NAME: str = "Data"
ARTIFACT_DIR: str = "artifacts"
PDF_FOLDER: str = "pdfs"
PDF_OUTPUT_FOLDER: str = "pdf-outputs"
POPPLAR_PATH = "D:\\Softwares\\Poppler\\poppler-24.08.0\\Library\\bin"

# Image Preprocessing constants and hyperparameters
PREPROCESSED_OUTPUT_FOLDER:str = "preprocessed_images"
BLUR_KERNEL_SIZE: tuple = (1,1)
RESIZE_TARGET_SIZE: tuple = (1600, 1200)
SKEW_DELTA: int = 1
SKEW_LIMIT: int = 5

# Image OCR Transformation constants and hyperparameters
OCR_OUTPUT_FOLDER:str = "ocr_texts"
OCR_MODE:str = "hybrid"

# Text Extraction constants and hyperparameters
TEXT_OUTPUT_FOLDER:str = "text_outputs"