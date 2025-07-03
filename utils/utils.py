import json
from datetime import datetime

PROCESSED_FILE = "processed.json"

def load_processed():
    try:
        with open(PROCESSED_FILE, "r") as file:
            return set(json.load(file))
    except FileNotFoundError:
        return set()

def save_processed(processed_ids):
    with open(PROCESSED_FILE, "w") as file:
        json.dump(list(processed_ids), file)

def is_message_from_date(msg_datetime, target_date):
    """ Check if the message date is from the target date.

    Args:
        msg_datetime: datetime object
        target_date: "yyyy-mm-dd"
    """
    return msg_datetime.strftime("%Y-%m-%d") == target_date
