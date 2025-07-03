import os
from dotenv import load_dotenv
from instagrapi import Client
from utils.utils import is_message_from_date

load_dotenv()

TARGET_DATE = os.getenv("TARGET_DATE")
ACCOUNT_USERNAME = os.getenv("INSTAGRAM_USERNAME")
ACCOUNT_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

print(ACCOUNT_USERNAME)

class InstagramClient:
    """
    Handles login and message operations.
    """
    def __init__(self):
        self.cl = Client()
        self.cl.login(ACCOUNT_USERNAME, ACCOUNT_PASSWORD)

    def fetch_unread_msgs(self, target_date=TARGET_DATE, inbox_amount=1):
        """
        Fetch unread messages on the target date.
        """
        inbox = self.cl.direct_threads(amount=inbox_amount)
        target_msgs = []

        for thread in inbox:
            # Shows whether read (0) or unread (1) using thread.read_state
            if thread.read_state == 1:
                for msg in thread.messages:
                    if msg.user_id != self.cl.user_id_from_username(ACCOUNT_USERNAME):
                        created_at = msg.timestamp
                        if is_message_from_date(created_at, TARGET_DATE) and msg.item_type == 'text' and msg.text is not None and msg.text.strip() != "":
                            target_msgs.append({
                                "user_id": msg.user_id,
                                "thread_id": thread.id,
                                "text": msg.text,
                                "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
                            })
        return target_msgs

    def reply_to_dm(self, user_id, text):
        """
        Send a reply to a DM.
        """
        self.cl.direct_send(text, user_ids=[user_id])

# myClient = InstagramClient()
# print(myClient.fetch_unread_msgs())
