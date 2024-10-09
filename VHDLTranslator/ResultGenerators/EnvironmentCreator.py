from ResultGenerators.FileCreator import FileCreator
import traceback

from typing import List
from VHDL.VHDLData import VHDLData

class EnvironmentCreator(FileCreator): 

    def create_file(self, result_path : str, vhdlData : VHDLData):
        result_data : str = self.__get_environment_from_data(vhdlData)
        
        self._create_file(f"{result_path}.env_descript", result_data)
        
    def __get_environment_from_data(self, vhdlData : VHDLData):
        try:
            result_data : str = ""
            result_data += "environment(\n"
            result_data += f"\ttypes:obj({self.__get_types(vhdlData)});\n"
                
            result_data += f"\tattributes:obj({self.__get_attributes(vhdlData)});\n"
            result_data += f"\tagent_types:obj({self.__get_agent_types(vhdlData)});\n"  
            result_data += f"\tagents:obj({self.__get_agents(vhdlData)});\n"            

            result_data += f"\tinstances:obj({self.__get_instances(vhdlData)});\n"
            result_data += f"\taxioms:obj({self.__get_axioms(vhdlData)});\n"
            result_data += f"\tlogic_formula:obj({self.__get_logic_formula(vhdlData)})\n"
            result_data += ");"
            
            return result_data

        except Exception:
            print(traceback.format_exc())
            #print(traceback.exc_info()[2])
    
    # NEED TO FIX
    def __get_types(self, vhdlData : VHDLData) -> str:
        return "Nil"

    # NEED TO FIX
    def __get_attributes(self, vhdlData : VHDLData) -> str:
        return "Nil"
    
        result = ""
        index:int = 0

        for index in range(0, len(attributes)):
            result += f"\t\t{attributes[index].name}:{attributes[index].refactor_type()}"
            if index < len(attributes)-1:
                result += ",\n"
            else:
                result += "\n"
        return result
        
    # NEED TO FIX
    def __get_agent_types(self, vhdlData : VHDLData) -> str:
        return "Nil"

        result = ""
        max_length = len(agents)
        agent_index:int = 0
        variable_index:int = 0

        for i in range(0,len(agents)):
            if not agents[i].has_variables():
                max_length -= 1

        for agent_index in range(0, len(agents)):
            if not agents[agent_index].has_variables():
                continue
            
            result += f"\t\t{agents[agent_index].name}:obj(\n"
                
            for variable_index in range(0, len(agents[agent_index].variables)):
                result += f"\t\t\t{agents[agent_index].variables[variable_index].name}:{agents[agent_index].variables[variable_index].refactor_type()}"
                if variable_index < len(agents[agent_index].variables)-1:
                    result += ",\n"
                else:
                    result += f"\n"
                    
            if agent_index < max_length-1:
                result += "\t\t),\n"
            else:
                result += "\t\t)\n"
        return result
    
    # NEED TO FIX
    def __get_agents(self, vhdlData : VHDLData) -> str:
        return "Nil"

        result = ""
        index:int = 0
        
        for index in range(0, len(agents)):
            result += f"\t\t{agents[index].name}:obj({agents[index].name.lower()})"
            if index < len(agents)-1:
                result += ",\n"
            else:
                result += "\n"
                
        return result
    
    # NEED TO FIX
    def __get_instances(self, vhdlData : VHDLData) -> str:
        return "Nil"
    
    # NEED TO FIX
    def __get_axioms(self, vhdlData : VHDLData) -> str:
        return "Nil"
    
    # NEED TO FIX
    def __get_logic_formula(self, vhdlData : VHDLData) -> str:
        return "Nil"
    