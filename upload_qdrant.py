"""
Permet de vectoriser toutes les recommendations markdown de reco médicales en local et de les upload sur qdrant
"""

from medee_library.qdrant import is_reco_created
from medee_library.scrape import get_data

collection_name = "reco_alibaba"

if __name__ == "__main__":
    is_reco_created(collection_name)
    get_data(collection_name)
