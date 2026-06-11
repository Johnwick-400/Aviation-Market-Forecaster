import pdfplumber
import pandas as pd
import os

# Stub for DGCA PDF Extraction
# DGCA publishes monthly PDFs. Once downloaded to data/raw/dgca/, this script will parse them.

RAW_DIR = "../data/raw/dgca"
PROCESSED_DIR = "../data/processed"

def extract_dgca_traffic(pdf_path):
    print(f"Extracting tables from {pdf_path}...")
    extracted_data = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    # Clean and append table data
                    # Note: DGCA tables vary, so strict index mapping will be required based on the specific PDF layout
                    extracted_data.extend(table)
                    
        if extracted_data:
            # Convert to DataFrame
            df = pd.DataFrame(extracted_data[1:], columns=extracted_data[0])
            print(f"✅ Extracted {len(df)} rows.")
            return df
        else:
            print("⚠️ No tables found.")
            return None
    except Exception as e:
        print(f"❌ Error parsing {pdf_path}: {e}")
        return None

if __name__ == "__main__":
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    print("Drop DGCA PDFs into data/raw/dgca/ then run this script.")
