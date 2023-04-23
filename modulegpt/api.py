import inspect
from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin
from typing import Any, TypeVar, Callable
from modulegpt.identifiable import Identifiable

T = TypeVar("T")


@dataclass
class ApiParameter(DataClassJsonMixin):
    name: str
    type: str
    description: str


@dataclass
class ApiResult(DataClassJsonMixin):
    type: str
    description: str


@dataclass
class ApiInterface(DataClassJsonMixin):
    name: str
    description: str
    parameters: list[ApiParameter]
    result: ApiResult

    def __hash__(self) -> int:
        return hash(self.name)


@dataclass
class ApiModuleInterfaces(DataClassJsonMixin):
    api_module: str
    description: str
    api_interfaces: list[ApiInterface]


class ApiModule(Identifiable):
    __API_ATTR = "__api_interface"

    def __init__(self, description: str):
        super().__init__()
        self.description = description


    @staticmethod
    def api(api_interface: ApiInterface) -> Callable[[T], T]:
        def wrapper(callable: T) -> T:
            setattr(callable, ApiModule.__API_ATTR, api_interface)
            return callable
        return wrapper

    def call(self, api_name: str, parameters: dict[str, Any]) -> Any:
        return self._api_by_name(api_name)(**parameters)

    def api_module_interfaces(self) -> ApiModuleInterfaces:
        return ApiModuleInterfaces(self.uid(), self.description, [
            getattr(method, ApiModule.__API_ATTR)
            for _, method in inspect.getmembers(self, lambda x: inspect.ismethod(x) or inspect.isfunction(x))
            if hasattr(method, ApiModule.__API_ATTR)
        ])

    def _api_by_name(self, api_name: str) -> Callable:
        for name, method in inspect.getmembers(self, lambda x: inspect.ismethod(x) or inspect.isfunction(x)):
            if hasattr(method, ApiModule.__API_ATTR) and name == api_name:
                return method
        raise Exception(f"Could not find api '{api_name}' in module '{self.uid()}'")
