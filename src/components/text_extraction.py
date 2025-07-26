import os
import sys
import difflib # to match text sequences
from glob import glob

from src.entity.artifact_entity import ImageOCRTransformationArtifact
from src.entity.config_entity import TextExtractionConfig
from src.logger import logging
from src.exception import srcException
from src.utils.main_utils import read_files


class TextExtraction:
    def __init__(self, text_extraction_config = TextExtractionConfig, image_ocr_transformation_artifact = ImageOCRTransformationArtifact):
        self.image_ocr_transformation_artifact = image_ocr_transformation_artifact
        self.text_extraction_config = text_extraction_config
    
    def hybrid_txt(self, file_path_1, file_path_2):
        """
        Perform Hybrid text processing on two files

        Merge OCR outputs by two different systems:

        1. **Using file 1 as the base** OCR result
        2. **Finding words unique to each** OCR output 
        3. **Replacing similar words** (≥75% match) from file 1 with potentially better recognition from file 2
        4. **Preferring longer words** (assuming more complete character recognition)
        5. **Skipping digit-containing words** (OCR often misreads numbers)

        **Purpose:** Improve OCR accuracy by leveraging the best recognition from multiple OCR attempts. 
        If one engine reads "recegnition" and another reads "recognition" with 75%+ similarity, it replaces with the longer/better version.
   
        Parameters:
        - file_path_1 (str): The path to first file
        - file_path_2 (str): The path to second file

        Return:
        - str: The processed text
        """
        try:
            # Read the contents of files
            file_content_1 = read_files(file_path_1)
            file_content_2 = read_files(file_path_2)

            if not file_content_1 or not file_content_2:
                return file_content_1 or file_content_2

            final_text = file_content_1

            # Split the contents of each file into words
            words_in_file_1 = set(file_content_1.split())
            words_in_file_2 = set(file_content_2.split())

            # Find common words
            common_words = words_in_file_1.intersection(words_in_file_2)

            # find unique words in each file
            unique_words_in_file_1 = words_in_file_1 - common_words
            unique_words_in_file_2 = words_in_file_2 - common_words

            # Iterate through unique words and perform replacement based on similarity
            for word_in_file_1 in unique_words_in_file_1:
                for word_in_file_2 in unique_words_in_file_2:
                    # skip words containign digits
                    if any(char.isdigit() for char in word_in_file_1) or any(char.isdigit() for char in word_in_file_2):
                        continue
                    # Calculate similairty ration between words
                    seq = difflib.SequenceMatcher(None, word_in_file_1, word_in_file_2)
                    diff_ratio = seq.ratio() * 100

                    # If similarity ratio is above 75%, perform replacement
                    if diff_ratio >= 75.0:
                        if len(word_in_file_2) >= len(word_in_file_1):
                            final_text = final_text.replace(word_in_file_1, word_in_file_2)
            
            return final_text
        
        except Exception as e:
            raise srcException(e,sys) from e
    
    def get_hybridized_result(self)-> None:
        """
        Generate Hybridized results for OCR output files
        The function takes OCR results from both PyTesseract and PaddleOCR engines and combines them into a single, 
        presumably more accurate result using hybridization logic.

        - Expects an input directory containing two subdirectories - "PYTESSERACT" and "PADDLEOCR", 
        each with matching folder structures containing .txt files with OCR results.
        -  For each PyTesseract text file, it looks for a corresponding PaddleOCR file by replacing "pyt" with "pocr" in the filename
        - 


        Parameters:
        - input_dir (str): The input directory containing OCR output files
        - output_dir (str): The output directory
        - mode (str): The mode of oepration (default is "hybrid")

        Returns:
        -None

        """
        try:
            input_dir = self.image_ocr_transformation_artifact.ocr_texts_folder

            output_dir = self.text_extraction_config.text_output_folder
            mode = self.text_extraction_config.mode

            if mode == "hybrid":
                pytesseract_root_dir = os.path.join(input_dir, "PYTESSERACT")
                paddleocr_root_dir = os.path.join(input_dir, "PADDLEOCR")

                result_folder = os.path.join(output_dir, input_dir.split("\\")[-1])

                logger.info(f"result_folder: {result_folder}")

                os.makedirs(result_folder, exist_ok= True)

                logger.info(f"pytesseract_root_dir: {pytesseract_root_dir}")

                for pytesseract_folder in os.listdir(pytesseract_root_dir):
                    logger.info(f"pytesseract_folder: {pytesseract_folder}")
                    if not os.path.isdir(os.path.join(pytesseract_root_dir, pytesseract_folder)):
                        logger.error(f"No folders found Error: {os.path.join(pytesseract_root_dir, pytesseract_folder)}")
                        continue

                    pytesseract_folder_path = os.path.join(pytesseract_root_dir, pytesseract_folder)
                    paddleocr_folder_path = os.path.join(paddleocr_root_dir, pytesseract_folder)

                    logger.info(f"pytesseract_folder_path: {pytesseract_folder_path}")
                    logger.info(f"paddleocr_folder_path: {paddleocr_folder_path}")


                    pyt_file_paths = sorted(glob(os.path.join(pytesseract_folder_path, "*.txt")))
                    pocr_file_paths = sorted(glob(os.path.join(paddleocr_folder_path, "*.txt")))

                    for pyt_file_path in pyt_file_paths:
                        file_path_to_be_compared = os.path.join(paddleocr_folder_path, os.path.basename(pyt_file_path)).replace("pyt", "pocr")

                        if file_path_to_be_compared in pocr_file_paths:
                            # read the contents
                            pyt_file_content = read_files(pyt_file_path)
                            pocr_file_content = read_files(file_path_to_be_compared)

                            # get hybridized text
                            h_text = self.hybrid_txt(file_path_to_be_compared, pyt_file_path)

                            # Write results into text folder
                            text_folder = os.path.join(result_folder, pytesseract_folder)
                            os.makedirs(text_folder, exist_ok=True)
                            # text_name = f"{os.path.join(result_folder, pytesseract_folder)}"
                            text_file_path = text_folder.replace("_pyt", "")
                            logger.info(f"text_file_path: {text_file_path}")
                            text_file = open(text_file_path, "w")
                            text_file.write(h_text)
                            text_file.close()
            else:
                logger.error(f"No other modes available right now")
                raise srcException(f"No other modes available right now", sys)
        except Exception as e:
            raise srcException(e,sys) from e


