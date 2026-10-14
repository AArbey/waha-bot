from pydantic import BaseModel, Field

from bot_backend.database import remove_reminder

class RemoveReminderArgs(BaseModel):
    reminder_id: int = Field(..., description="The ID of the reminder to remove.")

def doRemoveReminder(args: RemoveReminderArgs) -> str:
    remove_reminder(args.reminder_id)