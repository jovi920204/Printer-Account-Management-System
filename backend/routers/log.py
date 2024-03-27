from fastapi import APIRouter, HTTPException
from dependencies.datahandler import Data
from dependencies.sql import SQL

router = APIRouter()


@router.get("/log/print/")
async def get_all_print_log():
    command = "SELECT * FROM `PrintLog`"
    try:
        datas = await SQL.query(command)
        return Data.print_log_to_dict(datas)
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=500, detail=str(ex))
    

@router.get("/log/deposit/")
async def get_all_deposit_log():
    command = "SELECT * FROM `DepositLog`"
    try:
        datas = await SQL.query(command)
        return Data.deposit_log_to_dict(datas)
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=500, detail=str(ex))
