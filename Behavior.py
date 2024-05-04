from typing import List
from VHDLAction import VHDLAction
from VHDLStructure import VHDLStructure
import Constants

class Behavior:

    def create_file(self, path:str, vhdlStructure:VHDLStructure) -> None: 
        if not vhdlStructure.agents:
            print("Behavior_creator: Error, action list is empty...")
            return
        
        with open(f"{path}.behp", "w") as file:
            result = "p0 = "
            
            """
            agents[0] contains the list of all concurrent statements,
            other agents contains sequential statements
            """
            
            if len(vhdlStructure.agents[0].actions) <= 0:
                print("Error, zero actions in architecture block...")
                return
              
            #go through actions in architecture block
            for index in range(0, len(vhdlStructure.agents[0].actions)):
                result += f"Sensetive({Constants.translated_actions[vhdlStructure.agents[0].actions[index].name]}_{vhdlStructure.agents[0].actions[index].index})"
                if index < len(vhdlStructure.agents[0].actions)-1:
                    result += " || "
                else:
                    if len(vhdlStructure.agents) > 0:
                        result += " || " 
                
            #go through agents in architecture block
            for index in range(1, len(vhdlStructure.agents)):
                result += f"Sensetive({vhdlStructure.agents[index].name}, {vhdlStructure.agents[index].sensetive_list})"
                if index < len(vhdlStructure.agents)-1:
                    result += " || "
            
            
            #check if .vhd code has sequential statements
            if len(vhdlStructure.agents)-1 <= 0:
                file.write(result)
                return
            result += ",\n"
            
            #go through agents and check if they has actions
            for index in range(1, len(vhdlStructure.agents)):
                
                if not vhdlStructure.agents[index].has_actions():
                    continue
                
                result += f"{vhdlStructure.agents[index].name.lower()} = ("
                
                #go through actions
                for act_index in range(0, len(vhdlStructure.agents[index].actions)):
                    result += f"{Constants.translated_actions[vhdlStructure.agents[index].actions[act_index].name]}_{vhdlStructure.agents[index].actions[act_index].index}"
                    if act_index < len(vhdlStructure.agents[index].actions)-1:
                        result += "; "
                    else:
                        result += ")\n"
                            
            file.write(result)
            
    def add_action(self, action:VHDLAction) -> None:
        self.__actions.append(action)
        
    def add_actions(self, actions:List[VHDLAction]) -> None:
        for action in actions:
            self.__actions.append(action)
