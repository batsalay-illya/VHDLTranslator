from ResultGenerators.FileCreator import FileCreator
from VHDL.VHDLData import VHDLData

class BehaviourCreator(FileCreator): 

    def create_file(self, result_path : str, vhdlData : VHDLData):
        result_data : str = self.__get_behaviour_from_data(vhdlData)
        
        self._create_file(f"{result_path}.behp", result_data)
        
    # NEED TO FIX
    def __get_behaviour_from_data(self, vhdlData : VHDLData):
        return "Nil"
    
        try:
            if not vhdlStructure.agents:
                print("Behavior_creator: Error, action list is empty...")
                return
       
            result_data : str = ""
            result_data = "p0 = "
            
            
            if len(vhdlStructure.agents[0].actions) <= 0:
                print("Error, zero actions in architecture block...")
                return
              
            #go through actions in architecture block
            for index in range(0, len(vhdlStructure.agents[0].actions)):
                result_data += f"Sensetive({Constants.translated_actions[vhdlStructure.agents[0].actions[index].name]}_{vhdlStructure.agents[0].actions[index].index})"
                if index < len(vhdlStructure.agents[0].actions)-1:
                    result_data += " || "
                else:
                    if len(vhdlStructure.agents) > 0:
                        result_data += " || " 
                
            #go through agents in architecture block
            for index in range(1, len(vhdlStructure.agents)):
                result_data += f"Sensetive({vhdlStructure.agents[index].name}, {vhdlStructure.agents[index].sensetive_list})"
                if index < len(vhdlStructure.agents)-1:
                    result_data += " || "
            
            
            #check if .vhd code has sequential statements
            if len(vhdlStructure.agents)-1 <= 0:
                file.write(result_data)
                return
            result_data += ",\n"
            
            #go through agents and check if they has actions
            for index in range(1, len(vhdlStructure.agents)):
                
                if not vhdlStructure.agents[index].has_actions():
                    continue
                
                result_data += f"{vhdlStructure.agents[index].name.lower()} = ("
                
                #go through actions
                for act_index in range(0, len(vhdlStructure.agents[index].actions)):
                    result_data += f"{Constants.translated_actions[vhdlStructure.agents[index].actions[act_index].name]}_{vhdlStructure.agents[index].actions[act_index].index}"
                    if act_index < len(vhdlStructure.agents[index].actions)-1:
                        result_data += "; "
                    else:
                        result_data += ")\n"
                            
            return result_data

        except Exception:
            print(traceback.format_exc())
            #print(traceback.exc_info()[2])
       