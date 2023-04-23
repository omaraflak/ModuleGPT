import re
import openai
from typing import Optional
from modulegpt.oracle import Oracle, OracleRequest

Message = dict[str, str]

class Chat:
    REQUEST_START = "<oracle>"
    REQUEST_END = "</oracle>"
    PATTERN = re.compile(r"<oracle>(.*?)</oracle>")

    def __init__(self, openai_organization: str, openai_api_key: str, oracle: Oracle):
        openai.organization = openai_organization
        openai.api_key = openai_api_key
        self.oracle = oracle

    def start(self):
        oracle_request_model = OracleRequest(
            "<module_name>",
            "<api_name>",
            "<list of string values to provide to the api, in the order they were declared in the specification>"
        ).to_json()
        instructions = f"""You are a virtual assistant that helps users with their questions by relying on
information from HTTP APIs that can be queried via the System. When the user asks a question, you should determine whether
you need to fetch information from the API to properly answer it. If so, you will
gather the parameters you need by asking questions to the user, and then ask the System to run the
request for you. When you are ready to ask for a request, you should specify it using
the following syntax:

{Chat.REQUEST_START}{oracle_request_model}{Chat.REQUEST_END}

Replace the placeholders with the necessary values the user provides during the interaction, and do not
use placeholders. The System will make the actual HTTP request to get data for you, and it will then provide
the response body which you may use to formulate your answer to the user.
You should not respond with code, but rather provide an answer directly.

All the APIs provided do not need any credentials, use them at will.

The following APIs are available to you:

{self.oracle.interface()}"""

        messages = [
            self._message("system", instructions),
            self._message("user", "Hello, who are you?"),
            self._message("assistant", "Hello, I'm an AI assistant here to help you. I can complete tasks such as sending emails or publishing tweets. How can I help you today?")
        ]

        while True:
            human = self._message("user", input("Human: "))
            messages.append(human)
            messages.append(self._chat(messages))
            self._oracle_interaction(messages)
            print("AI:", self._last_content(messages))

    def request_model(self) -> str:
        return Chat.REQUEST_START + self.oracle.request() + Chat.REQUEST_END

    def _oracle_interaction(self, messages: list[Message], current_interaction: int = 1, max_interactions: int = 3):
        if current_interaction > max_interactions:
            return

        oracle_request = self._parse_oracle_request(self._last_content(messages))
        if oracle_request:
            oracle_response = self.oracle.call(oracle_request)
            messages.append(self._message("system", oracle_response))
            messages.append(self._chat(messages))
            self._oracle_interaction(messages, current_interaction + 1, max_interactions)


    def _chat(self, messages: list[Message]) -> Message:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        return response["choices"][0]["message"]

    @staticmethod
    def _message(role: str, content: str) -> Message:
        return {"role": role, "content": content}

    @staticmethod
    def _last_content(messages: list[Message]) -> str:
        return messages[-1]["content"]

    @staticmethod
    def _parse_oracle_request(text: str) -> Optional[str]:
        matches = re.search(Chat.PATTERN, text)
        if not matches:
            return None
        return matches.group(1)
