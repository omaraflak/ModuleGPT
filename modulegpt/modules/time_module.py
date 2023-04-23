from datetime import datetime
from modulegpt.api import ApiModule, ApiInterface, ApiResult


class TimeModule(ApiModule):
    def __init__(self):
        super().__init__("A module to get datetime")

    @staticmethod
    @ApiModule.api(ApiInterface(
        name="time",
        description="Gets the current datetime",
        parameters=[],
        result=ApiResult(type="str", description="A string of the format '%Y-%m-%d %H:%M:%S' represent the current datetime")
    ))
    def time() -> str:
        return datetime.today().strftime('%Y-%m-%d %H:%M:%S')
