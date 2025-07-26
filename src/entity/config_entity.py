import os
from src.constants import *
from dataclasses import dataclass
from datetime import datetime

TIMESTAMP: str = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")


@dataclass
class PipelineConfig:
    pipeline_name: str = PIPELINE_NAME
    # artifact_dir: str = os.path.join(pipeline_name,ARTIFACT_DIR)
    artifact_dir: str = ARTIFACT_DIR
    timestamp: str = TIMESTAMP

pipeline_config: PipelineConfig = PipelineConfig()



@dataclass
class DataIngestionConfig:
    pdf_folder: str = os.path.join(pipeline_config.artifact_dir, PDF_FOLDER)
    pdf_output_folder: str = os.path.join(pipeline_config.artifact_dir, PDF_OUTPUT_FOLDER)
    # pdf_output_folder: str = PDF_OUTPUT_FOLDER
    popplar_path: str = POPPLAR_PATH


@dataclass
class ImagePreProcessingConfig:
    output_folder: str = os.path.join(pipeline_config.artifact_dir, PREPROCESSED_OUTPUT_FOLDER)
    blur_kernel_size: tuple = BLUR_KERNEL_SIZE
    target_size: tuple = RESIZE_TARGET_SIZE
    delta: int = SKEW_DELTA
    limit: int = SKEW_LIMIT


@dataclass
class ImageOCRTransformationConfig:
    ocr_output_folder: str = os.path.join(pipeline_config.artifact_dir, OCR_OUTPUT_FOLDER)
    mode: str = OCR_MODE


@dataclass
class TextExtractionConfig:
    text_output_folder: str = os.path.join(pipeline_config.artifact_dir, TEXT_OUTPUT_FOLDER)
    mode: str = OCR_MODE