#!/bin/env python
import uvicorn
from uvicorn.config import LOGGING_CONFIG
from starlette.responses import RedirectResponse
from routers import user, permission, department, printer, log
from fastapi import FastAPI
from dotenv import load_dotenv
from os import getenv


app = FastAPI()


@app.get('/')  # redirect to docs
async def root():
    return RedirectResponse(url='/docs')


# ======================== Test Part =========================
# import aiofiles
# from fastapi import UploadFile
# @app.post("/uploadfile/")
# async def create_upload_file(file: UploadFile):
#     async with aiofiles.open(f'user_files/{file.filename}', 'wb') as out_file:
#         content = await file.read()
#         await out_file.write(content)
#     return {"filename": file.filename}

app.include_router(user.router)
app.include_router(permission.router)
app.include_router(department.router)
app.include_router(printer.router)
app.include_router(log.router)


# ========================= Run Part =========================
if __name__ == '__main__':
    load_dotenv()
    host = getenv("API_HOST")
    port = int(getenv("API_PORT"))

    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "[%(asctime)s] %(levelprefix)s %(message)s"
    LOGGING_CONFIG["formatters"]["access"][
        "fmt"] = '[%(asctime)s] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
    uvicorn.run(app,
                host=host,
                port=port)
