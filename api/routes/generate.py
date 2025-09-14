from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse,JSONResponse
import os

router = APIRouter()
from services.generator import generate_redeem_code

import traceback

import databases 
from services.logging import logger

from settings.config import Types

redeem_code_types = Types.redeem_code_types

import datetime


@router.post("/redeem/generate/")
async def generate_redeem(request: Request):
    try:
        authorization = request.headers.get("Authorization")

        if not authorization:
            return JSONResponse(status_code=401, content={"error": "Authorization header not found."})
        if authorization.startswith("Bearer "):
            authorization = authorization.replace("Bearer ", "")
        authorization = authorization.strip()
        if authorization != "Goahfo9uqehrflokanfijuvahfgiu89whnfjkgb234":
            return JSONResponse(status_code=401, content={"error": "Invalid authorization token."})
        
        try:
            # Parse request body
            data = await request.json()
        except:
            data = {}
        
        logger.info(f"Received request to generate redeem code with data: {data}")

        selected_code_type = data.get("code_type") # subscription
        code_validity = int(data.get("validity",30)) # 0 for unlimited

        print(selected_code_type, code_validity)

        if not selected_code_type or code_validity == None:
            return JSONResponse(status_code=400, content={"error": "Missing required fields.","fields": "code_type, validity","example": {"code_type": "no_prefix","validity": 0}})
        
        if selected_code_type not in redeem_code_types:
            return JSONResponse(status_code=400, content={"error": "Invalid code type.","valid_types": list(redeem_code_types.keys())})

        code_expires_at = datetime.datetime.now() + datetime.timedelta(days=30)
        code = generate_redeem_code()
        await databases.redeem_codes.insert(
            code=code,
            code_type='subscription',
            code_value=selected_code_type,
            valid_for_days=None if code_validity == 0 else code_validity,
            expires_at=code_expires_at,
            claimed=False,
            claimed_by=None,
            claimed_at=None
        )
        return JSONResponse(status_code=200, content={"data": {"code": code, "code_type": selected_code_type, "validity": code_validity, "expires_at": code_expires_at.strftime("%Y-%m-%d %H:%M:%S %Z")}})
    except Exception as e:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=500, content={"error": str(e)})