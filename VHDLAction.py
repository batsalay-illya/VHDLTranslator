class VHDLAction:
    def __init__(self, name:str, condition:str, agent_name:str, preview:str, post_condition:str, index:int):
        self.__name:str = name
        self.__condition:str = condition
        self.__agent_name:str = agent_name
        self.__preview:str = preview
        self.__post_condition:str = post_condition
        self.__index:int = index

    @property
    def name(self):
        return self.__name
    
    @property
    def condition(self) -> str:
        return self.__condition
    
    @property
    def agent_name(self) -> str:
        return self.__agent_name
    
    @property
    def preview(self) -> str:
        return self.__preview
    
    @property
    def post_condition(self) -> str:
        return self.__post_condition
    
    @property
    def index(self) -> int:
        return self.__index

    @condition.setter
    def condition(self, condition: str):
        if not condition:
            print("Error, null condition")
            return
        self.__condition = condition
        
    @agent_name.setter
    def agent_name(self, agent_name: str):
        if not agent_name:
            print("Error, null name")
            return
        self.__agent_name = agent_name
        
    @preview.setter
    def preview(self, preview: str):
        if not preview:
            print("Error, null preview")
            return
        self.__preview = preview
        
    def add_action(self, action):
        self.__actions.append(action)
        
    def has_actions(self) -> bool:
        if not self.__actions:
            return False
        return True
    
    def get_last_action(self):
        if self.__actions:
            return self.__actions[-1]
    
    def get_behavior(self, result:str = "") -> str:
        if self.has_actions():
            pass
        return result
            