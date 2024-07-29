"""
Permet de générer un dataset d'une question par chunk
"""

from medee_library.scrape import get_data_to_create_question
import json

data = get_data_to_create_question()

with open("dense.json", "w") as f:
    json.dump(data, f, indent=4)
