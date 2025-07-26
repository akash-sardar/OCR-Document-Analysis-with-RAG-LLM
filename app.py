import os
from dotenv import load_dotenv
load_dotenv()
poppler_path = os.getenv("POPPLER_PATH")

from src.pipeline.pipeline import pipeline

if __name__ =="__main__":
    pipe = pipeline()
    pipe.run_pipeline()