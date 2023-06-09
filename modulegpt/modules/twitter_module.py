from modulegpt.api import ApiModule, ApiInterface, ApiParameter, ApiResult


class TwitterModule(ApiModule):
    def __init__(self):
        super().__init__("A module to interact with Twitter")

    @ApiModule.api(ApiInterface(
        name="tweet",
        description="Tweets a message to the public",
        parameters=[
            ApiParameter(name="text", type="str", description="Text to tweet")
        ],
        result=ApiResult(type="bool", description="Whether or not the tweet was published successfully")
    ))
    def tweet(self, text: str) -> bool:
        return True
