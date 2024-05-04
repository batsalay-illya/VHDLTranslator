from typing import List
from VHDLAction import VHDLAction
from VHDLVariable import VHDLVariable

class VHDLAgent:
    def __init__(self, name:str):
        self.__name:str = name
        self.__variables:List[VHDLVariable] = []
        self.__actions:List[VHDLAction] = []
        self.__sensetive_list:str = ""

    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def variables(self) -> List[VHDLVariable]:
        return self.__variables
    
    @property
    def actions(self) -> List[VHDLAction]:
        return self.__actions
    
    @property
    def sensetive_list(self) -> str:
        return self.__sensetive_list
    
    def add_variable(self, variable: VHDLVariable):
        self.__variables.append(variable)
        
    def add_action(self, action: VHDLAction):
        self.__actions.append(action)
    
    def add_sensetive_list(self, sensetive_list:str):
        self.__sensetive_list = sensetive_list
        
    def has_variables(self) -> bool:
        if not self.__variables:
            return False
        return True
    
    def has_actions(self) -> bool:
        if not self.__actions:
            return False
        return True

    def get_last_action(self) -> VHDLAction:
        if self.__actions:
            return self.__actions[-1] 