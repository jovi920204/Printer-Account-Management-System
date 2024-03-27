from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import PlainTextResponse, JSONResponse
from models.printer import PrintRequest, CallbackStatus
from models.user import UserResponse
from fastapi import UploadFile, File, Depends
import aiofiles
from routers.user import edit_user_balance
from dependencies.sql import SQL
from dependencies.ScheduleServer import ScheduleServer
from dependencies.Printer import Work
import win32con
from datetime import datetime
import os
import json

from routers.user import get_user_by_studentID

router = APIRouter()

scheduleServer = ScheduleServer()
price = json.load(open('price.json'))

@router.get("/printer/names/")
async def get_all_printer_name() -> list:
    return scheduleServer.GetAllPrintersName()


async def save_file(file: UploadFile, filename: str) -> bool:
    path = 'user_files/'
    try:
        async with aiofiles.open(path+filename, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        return True
    except Exception as e:
        print(e)
        return False


def check_balance(print_info: PrintRequest, user: UserResponse) -> int:
    cost = print_info.pages
    if print_info.color == 0:
        if print_info.size == 0:
            cost *= price["gray_A4"]
        else:
            cost *= price["gray_A3"]
    else:
        if print_info.size == 0:
            cost *= price["color_A4"]
        else:
            cost *= price["color_A3"]
    return -1 if user.balance < cost else cost


@router.post("/printer/print/", response_class=JSONResponse)
async def user_print(print_info: PrintRequest = Depends(), file: UploadFile = File(...)):
    if print_info.color not in range(0, 2):
        raise HTTPException(status_code=400, detail="color should be 0 or 1")
    if print_info.duplex not in range(0, 3):
        raise HTTPException(status_code=400, detail="duplex should be 0, 1 or 2")
    if print_info.size not in range(0, 2):
        raise HTTPException(status_code=400, detail="size should be 0 or 1")
    if print_info.copies < 1:
        raise HTTPException(status_code=400, detail="copies should be greater than 0")
    if print_info.printer >= len(await get_all_printer_name()):
        raise HTTPException(status_code=400, detail="printer not exist")

    # get user infomation
    try:
        user = await get_user_by_studentID(print_info.studentID)
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=500, detail=str(ex))
    if not user:
        raise HTTPException(status_code=400, detail="user not exist")
    
    # check user balance are enough for requiring cost or not
    if (cost := check_balance(print_info, user[0])) == -1:
        raise HTTPException(status_code=400, detail="balance not enough")

    # rename file
    file_extension = file.filename.split('.')[-1]
    filename = f'{print_info.studentID}.{file_extension}'
    if not await save_file(file, filename):
        raise HTTPException(status_code=500, detail="error occurred when saving file")

    # mapping to win32con value
    '''
        顏色: 
            win32con.DMCOLOR_COLOR          彩色
            win32con.DMCOLOR_MONOCHROME     灰階
        雙面: 
            win32con.DMDUP_SIMPLEX          單面
            win32con.DMDUP_VERTICAL         以短邊翻面
            win32con.DMDUP_HORIZONTAL       以長邊翻面
        大小:
            win32con.DMPAPER_A3             A3
            win32con.DMPAPER_A4             A4
    '''

    # mapping for win32 api, not sql data
    colors = [win32con.DMCOLOR_MONOCHROME, win32con.DMCOLOR_COLOR]
    duplexs = [win32con.DMDUP_SIMPLEX,
               win32con.DMDUP_VERTICAL, win32con.DMDUP_HORIZONTAL]
    sizes = [win32con.DMPAPER_A4, win32con.DMPAPER_A3]

    # call printer
    work = Work(filename, colors[print_info.color],
                print_info.copies, duplexs[print_info.duplex], sizes[print_info.size])
    if not scheduleServer.AddWorkToPrinter(print_info.printer, work):
        raise HTTPException(status_code=500, detail="error occurred when adding work to printer")
    
    # calling edit_user_balance in routers/user.py
    try:
        await edit_user_balance(user[0].userID, -cost)
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=500, detail=str(ex))
    
    # TODO: remove file
    filepath = rf'.\user_files\{filename}'
    try:
        os.remove(filepath)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=200, detail="print success but, error occurred when removing file")

    # record print log
    print_info.studentID = user[0].userID
    callback_time: str = await print_log(print_info, cost)
    response = {"userID": user[0].userID, "time": callback_time}
    return JSONResponse(status_code=200, content=jsonable_encoder(response))


def debug_print_info(print_info: PrintRequest):
    msg = f'studentID: {print_info.studentID}\n'
    msg += f'printer: {print_info.printer}\n'
    msg += f'pages: {print_info.pages}\n'
    if print_info.color == 1:
        msg += 'color: 彩色\n'
    else:
        msg += 'color: 灰階\n'
    if print_info.duplex == 0:
        msg += 'duplex: 單面\n'
    elif print_info.duplex == 1:
        msg += 'duplex: 以短邊翻面\n'
    else:
        msg += 'duplex: 以長邊翻面\n'
    if print_info.size == 0:
        msg += 'size: A4\n'
    else:
        msg += 'size: A3\n'
    msg += f'copies: {print_info.copies}'
    print(msg)


async def print_log(print_info: PrintRequest, cost: int) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    command = "INSERT INTO `PrintLog` (`cost`, `time`, `userID`, `device`, `size`, `color`, `duplex`, `pages`, `copies`) \
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);"
    try:
        await SQL.edit(command, (cost, now, *print_info.dict().values()))
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=500, detail=str(ex))
    return now


@router.put("/printer/status/")
async def callback_status(info: CallbackStatus):
    command = "UPDATE `PrintLog` SET `status` = %s WHERE `PrintLog`.`userID` = %s AND `PrintLog`.`time` = %s;"
    try:
        await SQL.edit(command, (info.status, info.user_id, info.time))
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=500, detail=str(ex))
    return PlainTextResponse(status_code=200, content=f"update status success\nStatus: {info.status}")
