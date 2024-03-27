from fastapi import APIRouter, HTTPException
from dependencies.datahandler import Data
from dependencies.sql import SQL

router = APIRouter()


@router.get("/department/")
async def get_all_department_data():
    command = "SELECT * FROM `Department`"
    try:
        datas = await SQL.query(command)
        return Data.department_data_to_dict(datas)
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=500, detail=str(ex))
