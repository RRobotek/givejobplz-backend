import logging

from services import gh

import os
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
import random
import json







router = APIRouter()


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


@router.get("/{username}")
async def summary(username: str):
    summary = gh.summarize_github_profile(username)

    return {"summary": summary}

