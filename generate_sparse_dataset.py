from medee_library.scrape import get_data_to_create_question
import json

data = get_data_to_create_question(claude=True)

with open("sparse.json", "w") as f:
    json.dump(data, f, indent=4)
