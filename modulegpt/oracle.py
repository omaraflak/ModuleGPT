from typing import Any
from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin
from modulegpt.api import ApiInterface, ApiModuleInterface, ApiModule


@dataclass
class OracleInterface(DataClassJsonMixin):
    api_module_interfaces: list[ApiModuleInterface]

    @classmethod
    def from_api_modules(cls, api_modules: list[ApiModule]) -> 'OracleInterface':
        return OracleInterface([
            api_module_interface
            for module in api_modules
            for api_module_interface in module.api_module_interfaces()
        ])


@dataclass
class OracleRequest(DataClassJsonMixin):
    module_name: str
    api_name: str
    parameters: list[str]


class Oracle:
    def __init__(self, modules: list[ApiModule]):
        self.oracle_interface = OracleInterface.from_api_modules(modules)
        self.apis = self._apis(modules)
        self.modules: dict[str, ApiModule] = {
            module.uid(): module
            for module in modules
        }

    def call(self, oracle_request_json: str) -> str:
        request = OracleRequest.from_json(oracle_request_json)
        module = self.modules[request.module_name]
        api = self.apis[request.module_name][request.api_name]
        return str(module.call(request.api_name, Oracle._format_values(api, request.parameters)))

    def interface(self) -> str:
        return self.oracle_interface.to_json(indent=2)

    @staticmethod
    def _format_values(api_interface: ApiInterface, parameters: list[str]) -> dict[str, Any]:
        values: dict[str, Any] = dict()
        for param, value in zip(api_interface.parameters, parameters):
            if param.type == "int":
                values[param.name] = int(value)
            elif param.type == "float":
                values[param.name] = float(value)
            elif param.type == "str":
                values[param.name] = str(value)
            elif param.type == "bool":
                values[param.name] = bool(value)
            else:
                raise Exception(f"Parameter type '{param.type}' not supported")
        return values

    @staticmethod
    def _apis(modules: list[ApiModule]) -> dict[str, dict[str, ApiInterface]]:
        apis = dict()
        for module in modules:
            apis[module.uid()] = dict()
            for api_module_interface in module.api_module_interfaces():
                apis[module.uid()][api_module_interface.api_interface.name] = api_module_interface.api_interface
        return apis