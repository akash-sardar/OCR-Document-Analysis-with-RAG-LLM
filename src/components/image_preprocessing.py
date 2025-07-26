import os
import sys
from glob import glob

import cv2
import numpy as np
import imutils as im

from src.entity.artifact_entity import DataIngestionArtifact, ImagePreProcessingArtifact
from src.entity.config_entity import ImagePreProcessingConfig
from src.logger import get_logger
logger = get_logger(__name__)
from src.exception import srcException


class ImagePreProcessing:
    def __init__(self, image_processing_config = ImagePreProcessingConfig, data_ingestion_artifact = DataIngestionArtifact):
        try:
            self.image_processing_config = image_processing_config
            self.data_ingestion_artifact = data_ingestion_artifact
        except Exception as e:
            raise srcException(e,sys)

    def determine_score(self, arr, angle):
        """
        Determines the skew correction score for image deskewing.
        The score measures text line sharpness.
        - When text is properly aligned, horizontal projections show sharp peaks and valleys
        - Misaligned text creates smoother transtions, resulting in difference between consecutive histogram values

        Usage:  Loop testing multiple angles to find the one that maximizes the score, indicating optimal deskewing

        Parameters:
        - arr: Input amage array
        - angle: Rotation angle to test
        """
        # rotate the image by an angle
        data = im.rotate(arr, angle)

        # Sum pixel values across each row, creating horizontal projection histogram
        histogram = np.sum(data, axis=1, dtype = float)

        # Calulcate sum of squared difference between consecutive histogram values
        score = np.sum((histogram[1:] - histogram[:-1])**2, dtype = float)
        return histogram, score
    
    def correct_skew(self, image, delta=1, limit = 5):
        """
        Corrects skewed text in images
        """
        try:
            # convert image to grayscale
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Apply binary thresholding with Otsu's method to create white text on black background
            # Image Thresholding : Convert Grayscale images to binary(black/white) by comparing each pixel
            #                      to a threshold value. (thres<pixel 255 else 0)
            # Otsu's method: Finds optimal threshold by maximizing inter-class variance between foreground and background pixels
            # Binary Inversion: Creates white text on black background for better edge detection
            binary_thresholded_image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

            # Skew detection by Peak-Valley Analysis of horizontal projection
            scores = []
            angles = np.arange(-limit, limit + delta, delta)
            for angle in angles:
                histogram, score = self.determine_score(binary_thresholded_image, angle)
                scores.append(score)
            
            best_angle = angles[scores.index(max(scores))]
            h,w = image.shape
            center = (w //2, h//3)

            # Create rotation matrix centered - slightly above image center
            M = cv2.getRotationMatrix2D(center, best_angle, 1.0)

            # Apply rotation using cubic interpolation with border replication
            # Affine Transformations: Linear mappings preserving parallel lines
            # Cubic Interpolation: Higher-order polynomial fitting for smooth pixel value estimation during rotation
            # Border Handling: Replication extends edge pixels to fill empty regions after transformation
            rotated = cv2.warpAffine(image, M, (w,h), flags=cv2.INTER_CUBIC, borderMode = cv2.BORDER_REPLICATE)

            # Find angle with highest score
            return best_angle, rotated
        
        except Exception as e:
            raise srcException(e, sys)
    
    def deocument_image_rotation(self, image):
        delta = self.image_processing_config.delta
        limit = self.image_processing_config.limit
      
        best_angle, rotated_image = self.correct_skew(image, delta, limit)
        return best_angle, rotated_image
    
    def preprocess_and_resize_image(self, image_path, blur_kernel_size=(5,5), target_size=(800, 600)):
        """
        Resizing ensures consistent dimensions for batch processing

        """
        try:
            # Loading the image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Applying Gaussian Blur to:
            # - reduce noise
            # - prepare for edge detection
            # - downsample preparation
            # - create depth of field
            blurred_image = cv2.GaussianBlur(image, blur_kernel_size, 0)
            
            # Get original dimensions
            original_height, original_width = blurred_image.shape[:2]
            target_width, target_height = target_size
            
            # Calculate scaling factors
            width_scale = target_width / original_width
            height_scale = target_height / original_height
            
            # Choose minimum scale to maintain aspect ratio
            scale = min(width_scale, height_scale)
            
            # Calculate new dimensions
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            
            # Resize image while preserving aspect ratio
            resized_image = cv2.resize(blurred_image, (new_width, new_height))
            
            return resized_image
        except Exception as e:
            raise srcException(e, sys)

    
    def get_preprocessed_images(self)->ImagePreProcessingArtifact:
        """
        Main fucntion of image preprocessing pipeline that preprocessed and stores image
        before OCR read
        """
        try:
            # Get artifact from previous component
            data_ingestion_artifact = self.data_ingestion_artifact

            # get config
            input_folder = data_ingestion_artifact.pdf_output_folder
            output_folder = self.image_processing_config.output_folder
            blur_kernel_size = self.image_processing_config.blur_kernel_size
            target_size = self.image_processing_config.target_size

            logger.info(f"Image preprocessing started, \n\tinput_folder: {input_folder}, \n\toutput_folder: {output_folder}")

            # Ensure the output folder exists
            os.makedirs(output_folder, exist_ok=True)

            pdf_image_folders = os.listdir(input_folder)

            for pdf_image_folder in pdf_image_folders:
                output_subfolder = os.path.join(output_folder, pdf_image_folder)
                os.makedirs(output_subfolder, exist_ok=True)

                image_paths = glob(os.path.join(input_folder, pdf_image_folder)+'\\*.png')

                for image_path in image_paths:
                    preprocessed_image = self.preprocess_and_resize_image(image_path, blur_kernel_size, target_size)
                    angle, preprocessed_image = self.deocument_image_rotation(preprocessed_image)

                    logger.info(f"Angle of preprocessed images: {angle}")

                    preprocessed_image_filename = image_path.split("\\")[-1].split(".png")[0] + ".jpg"
                    success = cv2.imwrite(os.path.join(output_subfolder, preprocessed_image_filename), preprocessed_image)
                    if not success:
                        raise ValueError(f"Failed to write image: {preprocessed_image_filename}")
            
            logger.info(f"Image preprocessing completed, output_folder: {output_folder}")

            image_preprocessing_artifact = ImagePreProcessingArtifact(preprocessed_images_folder=output_folder)

            return image_preprocessing_artifact

        except Exception as e:
            raise srcException(e, sys)                   

