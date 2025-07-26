from dataclasses import dataclass


@dataclass
class DataIngestionArtifact:
    pdf_output_folder:str


@dataclass
class ImagePreProcessingArtifact:
    preprocessed_images_folder:str


@dataclass
class ImageOCRTransformationArtifact:
    ocr_texts_folder:str

