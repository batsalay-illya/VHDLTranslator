from ResultGenerators.FileCreator import FileCreator
from VHDL.VHDLData import VHDLData

class ActionCreator(FileCreator): 

    def create_file(self, result_path : str, vhdlData : VHDLData):
        result_data : str = self.__get_action_from_data(vhdlData)
        
        self._create_file(f"{result_path}.act", result_data)
        
    def __get_action_from_data(self, vhdlData : VHDLData):
        return "Nil"
    
        # NEED TO FIX
        try:
            result_data : str = ""

            for agent in vhdlStructure.agents:
                if agent.has_actions():
                    self.add_actions(agent.actions)
                
            if not self.__actions:
                print("Action_creator: Error, action list is empty...")
                return
            
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
                    
                        
            return result_data
                        
        except Exception:
            print(traceback.format_exc())
            #print(traceback.exc_info()[2])