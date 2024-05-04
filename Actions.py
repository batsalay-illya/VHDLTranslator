from typing import List
from VHDLAction import VHDLAction
from VHDLStructure import VHDLStructure
import Constants

class Actions:
    def __init__(self) -> None:
        self.__actions:List[VHDLAction] = []

    def create_file(self, path:str, vhdlStructure:VHDLStructure):
        for agent in vhdlStructure.agents:
            if agent.has_actions():
                self.add_actions(agent.actions)
                
        if not self.__actions:
            print("Action_creator: Error, action list is empty...")
            return
        
        with open(f"{path}.act", "w") as file:
            action: VHDLAction
            for index in range(0,len(self.__actions)):
                action_name = Constants.translated_actions[self.__actions[index].name]
                action_index = self.__actions[index].index
                
                if not self.__actions[index].condition:
                    action_condition = "1"
                else:
                    action_condition = self.__actions[index].condition
                    
                action_agent_name = self.__actions[index].agent_name
                action_preview = self.__actions[index].preview
                if not self.__actions[index].post_condition:
                    action_post_condition = "1"
                else:
                    action_post_condition = self.__actions[index].post_condition
                
                file.write(f"{action_name}_{action_index} = (({action_condition}) ->"+
                           f"(\"{action_agent_name}#{action_agent_name.lower()}: "+
                           f"action '{action_preview}';\") ({action_post_condition}))")
                
                if index < len(self.__actions)-1:
                    file.write(",\n")
            
    def add_action(self, action:VHDLAction) -> None:
        self.__actions.append(action)
        
    def add_actions(self, actions:List[VHDLAction]) -> None:
        for action in actions:
            self.__actions.append(action)
        