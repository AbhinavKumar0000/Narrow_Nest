from PyPDF2 import PdfReader
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ATSProcessor:
    def __init__(self):
        self.keywords = {
            'python': 10, 'javascript': 8, 'java': 8, 'sql': 7,
            'experience': 5, 'development': 5, 'team': 4,
            'communication': 4, 'skills': 3
        }

    def calculate_score(self, resume_path):
        try:
            reader = PdfReader(resume_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text().lower()

            score = 0
            for keyword, value in self.keywords.items():
                if re.search(rf'\b{keyword}\b', text):
                    score += value

            max_possible = sum(self.keywords.values())
            final_score = (score / max_possible) * 100 if max_possible > 0 else 0
            return min(final_score, 100)
        except Exception as e:
            logger.error(f"Error processing resume: {e}")
            return 0