from fastapi import APIRouter, HTTPException
from dependencies.datahandler import Data
from dependencies.sql import SQL

router = APIRouter()


@router.get("/permission/")
async def get_all_permission_data():
    command = "SELECT * FROM `Permission`"
    try:
        datas = await SQL.query(command)
        return Data.permission_data_to_dict(datas)
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=500, detail=str(ex))
