from modulegpt.api import ApiModule, ApiInterface, ApiParameter, ApiResult


class MathModule(ApiModule):
    def __init__(self):
        super().__init__("A module to do math operations")

    @staticmethod
    @ApiModule.api(ApiInterface(
        name="add",
        description="Adds two integers together",
        parameters=[
            ApiParameter(name="a", type="int", description="First number"),
            ApiParameter(name="b", type="int", description="Second number")
        ],
        result=ApiResult(type="int", description="An integer that is the sum of `a` and `b`")
    ))
    def add(a: int, b: int) -> int:
        return a + b
