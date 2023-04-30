import json
from typing import Any
from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin
from modulegpt.api import ApiInterface, ApiModuleInterfaces, ApiModule


@dataclass
class OracleInterface(DataClassJsonMixin):
    api_module_interfaces: list[ApiModuleInterfaces]

    @classmethod
    def from_api_modules(cls, api_modules: list[ApiModule]) -> 'OracleInterface':
        return OracleInterface([module.api_module_interfaces() for module in api_modules])


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

    def call(self, request: OracleRequest) -> str:
        module = self.modules.get(request.module_name)
        if not module:
            raise ValueError(f"No module named {request.module_name}")
        api = self.apis[request.module_name].get(request.api_name)
        if not api:
            raise ValueError(f"No api named {request.api_name}")
        return str(module.call(request.api_name, Oracle._format_values(api, request.parameters)))

    def interface(self) -> str:
        d = self.oracle_interface.to_dict(encode_json=True).get("api_module_interfaces")
        return json.dumps(d, indent=2)

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
            for api_interface in module.api_module_interfaces().api_interfaces:
                apis[module.uid()][api_interface.name] = api_interface
        return apis