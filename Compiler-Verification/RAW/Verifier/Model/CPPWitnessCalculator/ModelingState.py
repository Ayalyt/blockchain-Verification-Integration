from typing import Any, Optional


class ModelingState:
    def __init__(self, father=None, is_function_root: bool = False, name: str = ''):
        """
        Initializes a new state (scope).
        
        Args:
            father (Optional[ModelingState]): The parent state/scope.
            is_function_root (bool): Marks if this scope is a function boundary, preventing variable lookups from crossing it.
            init_constraints (Optional[list]): Initial path constraints.
        """
        self.__father = father
        self.__is_function_root: bool = is_function_root
        self.name = name

        self.__local_vars: dict[str, Any] = {}
        self.__lvar = None
        self.__expaux = None
        self.assigned_signals = set()


        # if father and not is_function_root:
        #     self.__lvar = father.__lvar
        #     self.__expaux = father.__expaux
        # else:
        #     self.__lvar = dict()
        #     self.__expaux = dict()

        self.deferred_writes: dict[tuple[str, Any], Any] = {}

    def get_father(self):
        return self.__father

    def is_function_root(self):
        return self.__is_function_root

    def fork(self, is_function_root: bool = False, arg_map: dict = None, name: str = ''):

        result = ModelingState(father=self, is_function_root=is_function_root, name=name)
        
        if arg_map is not None:
            for param_name, param_value in arg_map.items():
                if param_name == 'lvar':
                    result.set_lvar(param_value)
                elif param_name == 'expaux':
                    result.set_expaux(param_value)
                else:
                    result.define_local_var(param_name, param_value)

        if not is_function_root:
            if self.get_lvar() is not None:
                result.set_lvar(list(self.get_lvar()))
            if self.get_expaux() is not None:
                result.set_expaux(list(self.get_expaux()))

        return result

    def record_write(self, container_name: str, key: Any, value: Any):
        self.deferred_writes[(container_name, key)] = value

    # look up a written value along the state chain
    def get_written_value(self, container_name: str, key: Any) -> tuple[bool, Any]:
        lookup_key = (container_name, key)
        if lookup_key in self.deferred_writes:
            return True, self.deferred_writes[lookup_key]

        if self.__father and not self.__is_function_root:
            return self.__father.get_written_value(container_name, key)

        return False, None

    def set_lvar(self, lvar_array, is_merging: bool = False):
        if self.__lvar is not None and not is_merging:
            raise PermissionError(f'lvar has been setted!')
        self.__lvar = lvar_array

    def set_expaux(self, expaux_array, is_merging: bool = False):
        if self.__expaux is not None and not is_merging:
            raise PermissionError(f'expaux has been setted!')
        self.__expaux = expaux_array

    def get_local_var(self, name: str) -> Optional[Any]:

        if name == "lvar":
            return self.__lvar
        if name == "expaux":
            return self.__expaux

        if name in self.__local_vars:
            return self.__local_vars[name]

        if self.__father and not self.__is_function_root:
            return self.__father.get_local_var(name)
            
        raise KeyError(f'can not find local var {name}')

    def define_local_var(self, name: str, value: Any):

        self.__local_vars[name] = value

    def get_lvar(self):
        return self.__lvar

    def get_expaux(self):
        return self.__expaux

    def update_local_var_or_circuitElement(self, name: str, value: Any):
        current_scope = self
        while current_scope:
            if name in current_scope.__local_vars:

                if current_scope.__local_vars[name] != value:
                    self.__local_vars[name] = value
                break

            if current_scope.__is_function_root:
                raise NameError(f"assign to undeclared identifier '{name}'")
            current_scope = current_scope.__father


    def __str__(self):
        return self.name
