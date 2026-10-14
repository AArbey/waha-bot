from pydantic import BaseModel

from bot_backend.database import get_all_reminders_for_chat

class CheckRemindersArgs(BaseModel):
    pass

def doCheckReminders(args: CheckRemindersArgs, chat_id: str = None) -> str:
    return str(get_all_reminders_for_chat(chat_id=chat_id))