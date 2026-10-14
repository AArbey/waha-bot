from pydantic import BaseModel, Field

from bot_backend.database import edit_reminder

class EditReminderArgs(BaseModel):
    reminder_id: int = Field(..., description="The ID of the reminder to edit.")
    # Optional fields for editing the reminder
    message: str = Field(None, description="The new reminder message. Will be sent to the user at the specified time.")
    target_time: str = Field(None, description="The new target time for the general event in YYYY-MM-DD HH:MM:SS format.")
    next_reminder_time: str = Field(None, description="The new next reminder time in YYYY-MM-DD HH:MM:SS format. This is the time when the reminder will be sent to the user.")
    importance: int = Field(None, description="The new importance of the reminder. Higher values indicate higher importance. Default is 0.")


def doEditReminder(args: EditReminderArgs, chat_id: str) -> str:
    edit_reminder(
        reminder_id=args.reminder_id,
        message=args.message,
        target_time=args.target_time,
        next_reminder_time=args.next_reminder_time,
        importance=args.importance
    )