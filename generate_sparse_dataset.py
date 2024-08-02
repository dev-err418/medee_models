# from medee_library.scrape import get_data_to_create_question
import json

# data = get_data_to_create_question(claude=True)

with open("sparse.json", "r") as f:
    data = json.load(f)

print(data["0"])
