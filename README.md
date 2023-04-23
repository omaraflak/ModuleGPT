# Module GPT

ModuleGPT is my attempt to make an AI assistant that has access to APIs that you can easily customize.
This is inspired by this [article](https://techcommunity.microsoft.com/t5/fasttrack-for-azure/how-chatgpt-plugins-could-work/ba-p/3761483) and [AutoGPT](https://github.com/Significant-Gravitas/Auto-GPT).

# Usage

```python
from modulegpt.chat import Chat
from modulegpt.oracle import Oracle
from modulegpt.modules.math_module import MathModule
from modulegpt.modules.time_module import TimeModule
from modulegpt.modules.twitter_module import TwitterModule


chat = Chat(
    openai_organization="<organization>",
    openai_api_key="<api_key>",
    oracle=Oracle([
        MathModule(),
        TimeModule(),
        TwitterModule()
    ])
)

chat.start()
```

# How it works

Under the hood, ChatGPT is fed with the following instructions:

```
You are a virtual assistant that helps users with their questions by relying on
information from HTTP APIs that can be queried via the System. When the user asks a question, you should determine whether
you need to fetch information from the API to properly answer it. If so, you will
gather the parameters you need by asking questions to the user, and then ask the System to run the
request for you. When you are ready to ask for a request, you should specify it using
the following syntax:

<oracle>{"module_name": "<module_name>", "api_name": "<api_name>", "parameters": "<list of string values to provide to the api, in the order they were declared in the specification>"}</oracle>

Replace the placeholders with the necessary values the user provides during the interaction, and do not
use placeholders. The System will make the actual HTTP request to get data for you, and it will then provide
the response body which you may use to formulate your answer to the user.
You should not respond with code, but rather provide an answer directly.

All the APIs provided do not need any credentials, use them at will.

The following APIs are available to you:

{
  "api_module_interfaces": [
    {
      "api_module": "MathModule_1",
      "api_interface": {
        "name": "add",
        "description": "Adds two integers together",
        "parameters": [
          {
            "name": "a",
            "type": "int",
            "description": "First number"
          },
          {
            "name": "b",
            "type": "int",
            "description": "Second number"
          }
        ],
        "result": {
          "type": "int",
          "description": "An integer that is the sum of `a` and `b`"
        }
      }
    },
    {
      "api_module": "TimeModule_1",
      "api_interface": {
        "name": "time",
        "description": "Gets the current datetime",
        "parameters": [],
        "result": {
          "type": "str",
          "description": "A string of the format '%Y-%m-%d %H:%M:%S' represent the current datetime"
        }
      }
    },
    {
      "api_module": "TwitterModule_1",
      "api_interface": {
        "name": "tweet",
        "description": "Tweets a message to the public",
        "parameters": [
          {
            "name": "text",
            "type": "str",
            "description": "Text to tweet"
          }
        ],
        "result": {
          "type": "bool",
          "description": "Whether or not the tweet was published successfully"
        }
      }
    }
  ]
}
```

When the assistant outputs the `<oracle></oracle>` tags, then the message is not shown in the console but is instead parsed and passed to the correct ApiModule that can handle it.

# ApiModule

Creating a new ApiModule is quite simple.

```python
from modulegpt.api import ApiModule, ApiInterface, ApiParameter, ApiResult


class MathModule(ApiModule):
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
```

Your class needs to inherit from `ApiModule` and the exposed methods should be decorated with `@ApiModule.api`.

Then pass that module to the `Oracle` when building it, and that's it!