import json
import logging

logger = logging.getLogger(__name__)

def convert_to_json(function):
    """
    Converts data returned by function to JSON.
    """
    def export(*args, **kwargs):
        filename, data = function(*args, **kwargs)
        logger.info("Converting %s to JSON file.", filename)
        with open(f"../json/{filename}.json", "w+", encoding="utf-8") as file:
            file.write(json.dumps(data, ensure_ascii=False, indent=4))
        logger.info("%s converted to json/%s.json successfully!", *filename)
    return export
