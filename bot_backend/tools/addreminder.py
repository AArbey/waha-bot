from pydantic import BaseModel, Field

from bot_backend.database import add_new_reminder

class AddReminderArgs(BaseModel):
    #chat_id, message, target_time, next_reminder_time, importance
    message: str = Field(..., description="The reminder message. Will be sent to the user at the specified time.")
    target_time: str = Field(..., description="The target time for the general event in YYYY-MM-DD HH:MM:SS format.")
    next_reminder_time: str = Field(..., description="The next reminder time in YYYY-MM-DD HH:MM:SS format. This is the time when the reminder will be sent to the user.")
    importance: int = Field(0, description="The importance of the reminder. Higher values indicate higher importance. Default is 0.")


def doAddReminder(args: AddReminderArgs, chat_id: str) -> str:

    add_new_reminder(
        chat_id=chat_id,
        message=args.message,
        target_time=args.target_time,
        next_reminder_time=args.next_reminder_time,
        importance=args.importance
    )