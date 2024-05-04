from typing import List
from VHDLAction import VHDLAction
from VHDLAgent import VHDLAgent
from VHDLVariable import VHDLVariable

class VHDLStructure:

    def __init__(self):
        self.__global_variables:List[VHDLVariable] = []
        self.__agents:List[VHDLAgent] = []

    @property
    def global_variables(self) -> List[VHDLVariable]:
        return self.__global_variables
    @property
    def agents(self) -> List[VHDLAgent]:
        return self.__agents
    
    def add_variable(self, vhdl_variable: VHDLVariable) -> None:
        self.__global_variables.append(vhdl_variable)

    def add_agent(self, vhdl_agent: VHDLAgent) -> None:
        self.__agents.append(vhdl_agent)
        
    def add_action(self, vhdl_action: VHDLAction) -> None:
        self.get_last_agent().add_action(vhdl_action)

    def get_last_agent(self) -> VHDLAgent:
        if not self.__agents:
            return None
        return self.__agents[-1]
    