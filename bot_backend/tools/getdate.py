import requests
from pydantic import BaseModel, Field, ValidationError
import datetime

class GetDateArgs(BaseModel):
    pass

def doGetDate(args: GetDateArgs) -> str:
    return str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))