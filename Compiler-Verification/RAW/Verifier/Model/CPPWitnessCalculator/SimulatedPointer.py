from typing import Any

from .CircuitElement import CPPSignal

class SimulatedPointer:
    def __init__(self, container: Any, key: Any, containerName: str):
        self.container = container
        self.containerName = containerName
        self.key = key

    def get_value(self, state) -> Any:
        """*ptr state-sensitive"""
        # 1. check if the value is written in the state log
        found, value = state.get_written_value(self.containerName, self.key)
        if found:
            return value

        # 2. read from the original container if not found in the state log
        try:
            if isinstance(self.key, str):
                return getattr(self.container, self.key)
            else:
                try:
                    return self.container[self.key]
                except (IndexError, KeyError) as e:
                    print(f"dereference error: cannot get key {self.key} in container {self.containerName}")
                    raise e
        except (AttributeError, IndexError, KeyError) as e:
            print(f"dereference error: cannot get key {self.key} in container {self.containerName}")
            raise e

    def set_value(self, value: Any, state):
        """*ptr = value state-sensitive"""

        is_branch_state = state.get_father() is not None and not state.is_function_root()

        if is_branch_state:
            # 1. record the write in the state log, do not modify the original container directly
            state.record_write(self.containerName, self.key, value)
        else:
            # 2. modify the original container
            try:
                original_item = self.container[self.key]

                if isinstance(original_item, CPPSignal):
                    original_item.assign_value(value)
                else:
                    self.container[self.key] = value

            except (AttributeError, IndexError, KeyError) as e:
                print(f"pointer assign error: cannot set key {self.key} in container {self.containerName}")
                raise e
            
    def __repr__(self) -> str:
        return f"&{self.containerName}[{repr(self.key)}]"