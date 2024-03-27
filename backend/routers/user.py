from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from dependencies.datahandler import Data
from dependencies.sql import SQL
from models.user import UserResponse, UserRequest, AddBalanceRequest

router = APIRouter()

@router.get("/user/")
async def get_all_user_data():
    command = "SELECT * FROM `User`"
    try:
        datas = await SQL.query(command)
        return Data.user_data_to_dict(datas)
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=500, detail=str(ex))


@router.get("/user/userID/{user_id}/")
async def get_user_by_id(user_id: int):
    command = "SELECT * FROM `User` WHERE `userID` = %s"
    try:
        datas = await SQL.query(command, (user_id,))
        return Data.user_data_to_dict(datas)
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=500, detail=str(ex))


@router.get("/user/studentID/{studentID}/")
async def get_user_by_studentID(studentID: str):
    command = "SELECT * FROM `User` WHERE `studentID` = %s;"
    try:
        datas = await SQL.query(command, (studentID,))
        return Data.user_data_to_dict(datas)
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=500, detail=str(ex))


@router.post("/user/")
async def create_user(user: UserRequest):
    if user.departmentID not in range(1, 4):
        raise HTTPException(status_code=400, detail="departmentID should be a 1, 2 or 3")
    elif user.permissionID not in range(1, 3):
        raise HTTPException(status_code=400, detail="permissionID should be a 1 or 2")
    elif await get_user_by_studentID(user.studentID):
        raise HTTPException(status_code=400, detail="the studentID has been used")

    current_id = await SQL.get_current_id()
    command = "INSERT INTO `User` (`userID`, `studentID`, `name`, `password`, `departmentID`, `permissionID`) \
                VALUES (%s,%s,%s,%s,%s,%s);"
    parameters = (current_id + 1, user.studentID, user.name,
                  user.password, user.departmentID, user.permissionID)
    try:
        await SQL.edit(command, parameters)
        return PlainTextResponse("create user successfully", status_code=200)
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=500, detail=str(ex))


@router.delete("/user/{user_id}/")
async def delete_user(user_id: int):
    target: list = await get_user_by_id(user_id)
    if not target:
        raise HTTPException(status_code=400, detail="the user does not exist")

    command = "DELETE FROM `User` WHERE `User`.`userID` = %s"
    try:
        await SQL.edit(command, (user_id,))
        return PlainTextResponse("delete user successfully", status_code=200)
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=500, detail=str(ex))


@router.put("/user/")
async def update_user(user: UserResponse):
    target: list = await get_user_by_id(user.userID)
    if not target:
        raise HTTPException(status_code=400, detail="the user does not exist")
    elif user.departmentID not in range(1, 4):
        raise HTTPException(status_code=400, detail="departmentID should be a 1, 2 or 3")
    elif user.permissionID not in range(1, 3):
        raise HTTPException(status_code=400, detail="permissionID should be a 1 or 2")
    elif user.balance < 0:
        raise HTTPException(status_code=400, detail="balance should not be a negative number")

    command = "UPDATE `User` SET `studentID` = %s, `name` = %s, `password` = %s, `permissionID` = %s, \
                `departmentID` = %s WHERE `User`.`userID` = %s;"
    parameters = (user.studentID, user.name, user.password,
                  user.permissionID, user.departmentID, user.userID)
    try:
        await SQL.edit(command, parameters)
        return PlainTextResponse("update user successfully", status_code=200)
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=500, detail=str(ex))


@router.get("/user/login/{studentID}/")
async def user_login(studentID: str):
    try:
        if datas := await get_user_by_studentID(studentID):
            return {"studentID": datas[0].studentID,
                    "password": datas[0].password,
                    "permissionID": datas[0].permissionID}
        return PlainTextResponse("the studentID does not exist", status_code=400)
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=500, detail=str(ex))

async def edit_user_balance(userID: int, balance: int):
    command = "UPDATE `User` SET balance = balance + %s WHERE `User`.`userID` = %s;"
    
    try:
        await SQL.edit(command, (balance, userID))
    except Exception as ex:
        print(ex)
        raise "SQL.edit error from table `User`"

@router.put("/user/balance/")
async def user_add_balance(info: AddBalanceRequest):
    target: list = await get_user_by_id(info.userID)
    if not target:
        raise HTTPException(status_code=400, detail="the user does not exist")
    if not info.type in range(3):
        raise HTTPException(status_code=400, detail="the type should be a 0, 1 or 2")
    if len(info.comment) > 30:
        raise HTTPException(status_code=400, detail="the comment is too long, should be less than 30 characters")
    
    try:
        await edit_user_balance(info.userID, info.balance)
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=500, detail=str(ex))
    
    command = "INSERT INTO `DepositLog` (`userID`, `cash`, `balance`, `type`, `comment`) \
            VALUES (%s,%s,%s,%s,%s);" 
    try:
        await SQL.edit(command, (*info.dict().values(),))
        return PlainTextResponse("operate successfully", status_code=200)
    except Exception as ex:
        print("SQL.edit error from table `DepositLog`")
        print(ex)
        raise HTTPException(status_code=500, detail=str(ex))