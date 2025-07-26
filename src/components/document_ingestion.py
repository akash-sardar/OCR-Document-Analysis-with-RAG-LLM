import os
import sys
from glob import glob

import cv2
import numpy as np
from pdf2image import convert_from_path
import imutils as im

from src.entity.artifact_entity import DataIngestionArtifact
from src.entity.config_entity import DataIngestionConfig
from src.logger import get_logger
logger = get_logger(__name__)
from src.exception import srcException


class DocumentIngestion:
    def __init__(self,data_ingestion_config:DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise srcException(e,sys)


    def pdf_to_images(self, pdf_path, pdf_output_folder, popplar_path):
        try:
            # Ensure the output folder exists for PDF with its name
            os.makedirs(pdf_output_folder, exist_ok=True)

            # Open the pdf file
            pdf_document = convert_from_path(pdf_path, poppler_path=popplar_path)

            # get the total number of pages in the pdf
            total_pages = len(pdf_document)

            for page_no in range(total_pages):
                # Save the image to output_folder with page_no
                prefix = pdf_output_folder.split("\\")[-1]
                image_filename = str(prefix+"_"+f"page_{page_no + 1}.png")
                image_path = os.path.join(pdf_output_folder, image_filename)
                pdf_document[page_no].save(image_path, "PNG")

        except Exception as e:
            raise srcException(e, sys) from e                
    
    def process_multiple_pdfs(self):
        try:
            pdf_folder = self.data_ingestion_config.pdf_folder
            output_folder = self.data_ingestion_config.pdf_output_folder
            popplar_path = self.data_ingestion_config.popplar_path
            # create the output folder
            os.makedirs(output_folder, exist_ok=True)

            logger.info(f"Document Ingestion started, pdf_folder: {pdf_folder}, output_folder: {output_folder}")

            # List all files in the PDF folder
            pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('pdf')]

            for pdf_file in pdf_files:
                pdf_path = os.path.join(pdf_folder, pdf_file)

                # create pdf output folder
                pdf_output_folder = os.path.join(output_folder, os.path.splitext(pdf_file)[0])
                os.makedirs(pdf_output_folder, exist_ok=True)

                # convert the pdf to an image using pdf2image.pdf_to_images
                self.pdf_to_images(pdf_path, pdf_output_folder, popplar_path)
            
            logger.info(f"Document Ingestion completed, output_folder: {output_folder}")            
            data_ingestion_artifact = DataIngestionArtifact(pdf_output_folder=output_folder)

            return data_ingestion_artifact
          

        except Exception as e:
            logger.error(f"Error during document ingestion: {e}")
            raise srcException(e, sys) from e
    




    



        
