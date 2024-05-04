import VHDLAgent
import Constants

class VHDLVariable:
    
    def __init__(self, var_name:str, var_type:str, var_agent:str):
        self.__agent:str = var_agent
        self.__name:str = var_name
        self.__type:str = var_type
    
    @property
    def agent(self) -> VHDLAgent:
        return self.__agent

    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def type(self) -> str:
        return self.__type
    
    @type.setter
    def type(self, var_type:str):
        if not var_type:
            print("Error, type is not defined")
            return
        self.__type = var_type
        
    def refactor_type(self) -> str:
        return Constants.translated_variables[self.__type.lower()]