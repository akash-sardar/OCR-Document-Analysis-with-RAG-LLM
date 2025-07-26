import os
import sys
import pytesseract
from glob import glob
# from paddleocr import PaddleOCR
from dotenv import load_dotenv
load_dotenv()
pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT_PATH')

from src.entity.artifact_entity import ImagePreProcessingArtifact, ImageOCRTransformationArtifact
from src.entity.config_entity import ImageOCRTransformationConfig
from src.logger import get_logger
logger = get_logger(__name__)
from src.exception import srcException


class ImageOCRTransformation:
    def __init__(self, image_ocr_transformation_config = ImageOCRTransformationConfig, image_preprocessing_artifact = ImagePreProcessingArtifact):
        try:
            # self.paddle_ocr = PaddleOCR(lang='en')
            self.image_ocr_transformation_config = image_ocr_transformation_config
            self.image_preprocessing_artifact = image_preprocessing_artifact
        except Exception as e:
            raise srcException(e, sys)
    
    def ocr_with_tesseract(self, image_path)->str:
        # OCR Engine Modes:
        # 0. Legacy, 
        # 1. Neural Nets/LSTM (recommended), 
        # 2. Legacy + LSTM 
        # 3. Default
        # psm = Page Segmentation Mode
        # 3 - Fully automatic page segmentation, but no OSD (Orientation and Script Detection)
        # OEM 1 and PSM 3 is a solid default for most general-purpose OCR tasks
        custom_config = r'--oem 1 --psm 3'
        try:
            return pytesseract.image_to_string(image_path, output_type='string', config = custom_config, lang = 'eng')
        except Exception as e:
            logger.error(f"Error during tesseract OCR:{e}")
            return ""
        
    def ocr_with_paddleocr(self, image_path)->list:
        try:
            # return self.paddle_ocr.predict([image_path])
            return None
        except Exception as e:
            logger.error(f"Error during paddleocr OCR:{e}")
            return ""

    def perform_ocr(self):
        try:
            logger.info(f"OCR process started")
            input_folder = self.image_preprocessing_artifact.preprocessed_images_folder
            output_folder = self.image_ocr_transformation_config.ocr_output_folder
            mode = self.image_ocr_transformation_config.mode

            logger.info(f"OCR Mode: {mode}")
            logger.info(f"Input folder: {input_folder}")
            logger.info(f"Output folder: {output_folder}")

            image_folders = os.listdir(input_folder)
            logger.info(f"Found image folders: {image_folders}")

            for image_folder in image_folders:
                if "pytesseract" in mode.lower() or "hybrid" in mode.lower():
                    # for Tesseract folder
                    pyt_ocr_folder = os.path.join(output_folder, "PYTESSERACT", image_folder)
                    os.makedirs(pyt_ocr_folder, exist_ok=True)
                
                if "paddleocr" in mode.lower() or "hybrid" in mode.lower():
                    # for paddleocr folder
                    pocr_ocr_folder = os.path.join(output_folder, "PADDLEOCR", image_folder)
                    os.makedirs(pocr_ocr_folder, exist_ok=True)
                
                image_paths = glob(os.path.join(input_folder, image_folder, "*.jpg"))
                logger.info(f"Found images in {image_folder}: {len(image_paths)}")

                count_pyt = 1
                count_pocr = 1

                for image_path in image_paths:
                    # Get the file name without ".jpg" extension
                    file_name = image_path.split("\\")[-1][:-4]

                    if "pytesseract" in mode.lower() or "hybrid" in mode.lower():
                        # for pytesseract OCR text
                        pyt_ocr_txt = self.ocr_with_tesseract(image_path=image_path)
                        text_file_pyt = open(os.path.join(pyt_ocr_folder, f"{file_name}_pyt.txt"), "w", encoding = "utf-8")
                        text_file_pyt.write(pyt_ocr_txt)
                        text_file_pyt.close()
                        logger.debug(f"Pytesseract OCR generated: count {count_pyt}")
                        count_pyt+=1

                    if "paddleocr" in mode.lower() or "hybrid" in mode.lower():
                        # for pytesseract OCR text
                        pocr_list = self.ocr_with_paddleocr(image_path)
                        if pocr_list:
                            pocr_text_list = [x[1][0] for x in pocr_list[0]] # [Bounding box (4 corners), ("recognized_text", confidence_score) ]
                            text_file_pocr = open(os.path.join(pocr_ocr_folder, f"{file_name}_pocr.txt"), "w", encoding = "utf-8")
                            for text in pocr_text_list:
                                text_file_pocr.write(f"{text}\n")
                            text_file_pocr.close()
                            logger.debug(f"PaddleOCR OCR generated: count {count_pocr}")
                            count_pocr+=1
                        else:
                            pass
            
            logger.info(f"OCR completed: output_folder: {output_folder}")
            image_ocr_transformation_artifact = ImageOCRTransformationArtifact(ocr_texts_folder=output_folder)

            return image_ocr_transformation_artifact

        except Exception as e:
            logger.error("Error occurred in start_image_ocr", exc_info=True)
            raise srcException(e,sys) from e
    
