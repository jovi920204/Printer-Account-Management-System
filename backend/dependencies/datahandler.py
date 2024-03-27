from typing import Tuple, List
from models.user import UserResponse
from models.permission import PermisstionResponse
from models.department import DepartmentResponse
from models.log import PrintLogResponse, DepositLogResponse


class Data:
    @staticmethod
    def column_to_dict(column_names: List[str], data) -> dict[str, any]:
        return {name: data[index] for index, name in enumerate(column_names)}

    @staticmethod
    def user_data_to_dict(raw_datas: List[Tuple[any]]) -> List[UserResponse]:
        column_names = ['userID', 'studentID', 'name', 'password',
                        'balance', 'permissionID', 'departmentID', 'page', 'sheet', 'task']
        return [UserResponse(**Data.column_to_dict(column_names, data)) for data in raw_datas]

    @staticmethod
    def permission_data_to_dict(raw_datas: List[Tuple[any]]) -> List[PermisstionResponse]:
        column_names = ['permissionID', 'name', 'management', '_print']
        return [PermisstionResponse(**Data.column_to_dict(column_names, data)) for data in raw_datas]

    @staticmethod
    def department_data_to_dict(raw_datas: List[Tuple[any]]) -> List[DepartmentResponse]:
        column_names = ['departmentID', 'name']
        return [DepartmentResponse(**Data.column_to_dict(column_names, data)) for data in raw_datas]

    @staticmethod
    def print_log_to_dict(raw_datas: List[Tuple[any]]) -> List[PrintLogResponse]:
        column_names = ['recordID', 'userID', 'time', 'device', 'size', 'color', 'duplex', 'pages', 'cost', 'copies',
                        'status']
        return [PrintLogResponse(**Data.column_to_dict(column_names, data)) for data in raw_datas]

    @staticmethod
    def deposit_log_to_dict(raw_datas: List[Tuple[any]]) -> List[DepositLogResponse]:
        column_names = ['time', 'userID', 'cash', 'balance', '_type', 'comment']
        return [DepositLogResponse(**Data.column_to_dict(column_names, data)) for data in raw_datas]

if __name__ == '__main__':
    import asyncio
    from backend.dependencies.sql import SQL
    from pprint import pprint

    command = "SELECT * FROM `User`"
    response = asyncio.run(SQL.query(command))
    pprint(response)
    # users = Data.department_data_to_dict(response)
    # pprint(users)
