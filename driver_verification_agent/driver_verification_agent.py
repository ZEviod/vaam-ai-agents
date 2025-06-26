"""
# Driver Verification Agent
# Purpose: Automate the process of verifying driver identity and documents.
# Core Features:
# - Document upload & OCR
# - Face match & liveness check
# - Database cross-verification
# - Auto-approve/reject decisions
"""

import random
import pytesseract
from PIL import Image
import re

class DriverVerificationAgent:
    def __init__(self):
        self.ocr_data = {}
        self.face_results = {}
        self.db_results = {}
        self.decisions = {}

    def upload_document(self, driver_id, document):
        """Perform document upload and OCR extraction using pytesseract."""
        ocr_result = {'name': 'UNKNOWN', 'dob': 'UNKNOWN', 'licence_number': 'UNKNOWN'}
        try:
            img = Image.open(document)
            text = pytesseract.image_to_string(img)
            print(f"[OCR] Raw extracted text for {driver_id}:\n{text}")
            # Basic parsing for UK driving licence (customize as needed)
            name_match = re.search(r'Name[:\s]+([A-Z\s]+)', text, re.IGNORECASE)
            dob_match = re.search(r'Date of Birth[:\s]+(\d{2,4}[-/\.]\d{2}[-/\.]\d{2,4})', text, re.IGNORECASE)
            licence_match = re.search(r'Licence Number[:\s]+([A-Z0-9]+)', text, re.IGNORECASE)
            if name_match:
                ocr_result['name'] = name_match.group(1).strip()
            if dob_match:
                ocr_result['dob'] = dob_match.group(1).strip()
            if licence_match:
                ocr_result['licence_number'] = licence_match.group(1).strip()
        except Exception as e:
            print(f"[OCR] Error processing image: {e}")
        self.ocr_data[driver_id] = ocr_result
        print(f"[OCR] Extracted data for {driver_id}: {ocr_result}")
        return ocr_result

    def face_match_liveness(self, driver_id, selfie, id_photo):
        """Simulate face match and liveness check."""
        # In a real system, use a face recognition API
        # For demo, randomly pass or fail
        match = random.choice([True, False])
        liveness = random.choice([True, False])
        result = {'face_match': match, 'liveness': liveness}
        self.face_results[driver_id] = result
        print(f"[Face] Results for {driver_id}: {result}")
        return result

    def cross_verify_database(self, driver_id):
        """Ask user to check licence number on gov.uk and confirm validity."""
        ocr = self.ocr_data.get(driver_id)
        if not ocr:
            print("[DB] No OCR data found. Cannot verify.")
            self.db_results[driver_id] = False
            return False
        licence_number = ocr['licence_number']
        print(f"[DB] Please go to https://www.gov.uk/view-driving-licence and check licence number: {licence_number}")
        user_input = input("Is the licence valid? (yes/no): ").strip().lower()
        verified = user_input == 'yes'
        self.db_results[driver_id] = verified
        print(f"[DB] Cross-verification for {driver_id}: {verified}")
        return verified

    def auto_decision(self, driver_id):
        """Auto-approve or reject based on all checks."""
        ocr = self.ocr_data.get(driver_id)
        face = self.face_results.get(driver_id)
        db = self.db_results.get(driver_id)
        if ocr and face and db:
            if face['face_match'] and face['liveness'] and db:
                decision = 'APPROVED'
            else:
                decision = 'REJECTED'
        else:
            decision = 'REJECTED'
        self.decisions[driver_id] = decision
        print(f"[Decision] {driver_id}: {decision}")
        return decision

def main():
    agent = DriverVerificationAgent()
    driver_id = input("Enter driver ID: ").strip()
    licence_image = input("Upload driver's licence image (enter file path): ").strip()
    selfie_image = input("Upload driver's selfie image (enter file path): ").strip()
    # Process document upload & OCR
    agent.upload_document(driver_id, document=licence_image)
    # Process face match & liveness
    agent.face_match_liveness(driver_id, selfie=selfie_image, id_photo=licence_image)
    # Cross-verify licence number on gov.uk
    agent.cross_verify_database(driver_id)
    # Make auto decision
    agent.auto_decision(driver_id)

if __name__ == "__main__":
    main()
