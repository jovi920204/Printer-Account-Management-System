import aiomysql
import asyncio
from dotenv import load_dotenv
from os import getenv

load_dotenv()
host = getenv("SQL_HOST")
port = int(getenv("SQL_PORT"))
user = getenv("SQL_USER")
password = getenv("SQL_PASSWORD")
db = getenv("SQL_DB")

class SQL:
    @staticmethod
    async def register(loop: asyncio.AbstractEventLoop) -> aiomysql.Pool:
        return await aiomysql.create_pool(host=host, port=port,
                                          user=user, password=password,
                                          db=db, loop=loop)

    @staticmethod
    async def close(pool) -> None:
        pool.close()
        await pool.wait_closed()

    @staticmethod
    async def query(command: str, parameter: tuple = (), loop: asyncio.AbstractEventLoop = None):
        if loop is None:
            loop = asyncio.get_event_loop()
        pool: aiomysql.Pool = await SQL.register(loop)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(command, parameter)
                result = await cursor.fetchall()
        await SQL.close(pool)
        return result

    @staticmethod
    async def edit(command: str, parameter: tuple = (), loop: asyncio.AbstractEventLoop = None):
        if loop is None:
            loop = asyncio.get_event_loop()
        pool: aiomysql.Pool = await SQL.register(loop)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(command, parameter)
                await conn.commit()
        await SQL.close(pool)

    @staticmethod
    async def get_current_id() -> int:
        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        command = 'SELECT * FROM `User` ORDER BY `userID` DESC LIMIT 1'
        result = await SQL.query(command, loop=loop)
        return result[0][0]


if __name__ == '__main__':
    current_id = asyncio.run(SQL.get_current_id())
    datas = (current_id+1, 'sqli', 'fix', '...', 1)
    command = f"INSERT INTO `User` (`userID`, `studentID`, `name`, `password`, `departmentID`) \
                VALUES (%s,%s,%s,%s,%s);"
    asyncio.run(SQL.edit(command, datas))
