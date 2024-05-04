from typing import List
from VHDLAgent import VHDLAgent
from VHDLVariable import VHDLVariable

class Environment:
    def create_file(self, path:str, attributes:List[VHDLVariable], agents:List[VHDLAgent]):
        try:
            with open(f"{path}.env_descript", "w") as file:
                file.write("environment(\n")
                file.write("\ttypes:obj(Nil);\n")
                
                file.write(f"\tattributes:obj(\n{self.__get_attributes(attributes)}\t);\n")
                file.write(f"\tagent_types:obj(\n{self.__get_agent_types(agents)}\t);\n")  
                file.write(f"\tagents:obj(\n{self.__get_agents(agents)}\t);\n")            

                file.write("\tinstances:obj(Nil);\n")
                file.write("\taxioms:obj(Nil);\n")
                file.write("\tlogic_formula:obj(Nil)\n")
                file.write(");")
        except Exception as ex:
            print(f"Environment_creator: error, exception:{ex}")
            
    def __get_attributes(self, attributes:List[VHDLVariable]) -> str:
        result = ""
        index:int = 0

        for index in range(0, len(attributes)):
            result += f"\t\t{attributes[index].name}:{attributes[index].refactor_type()}"
            if index < len(attributes)-1:
                result += ",\n"
            else:
                result += "\n"
        return result
            
    def __get_agent_types(self, agents:List[VHDLAgent]) -> str:
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
    
    def __get_agents(self, agents:List[VHDLAgent]) -> str:
        result = ""
        index:int = 0
        
        for index in range(0, len(agents)):
            result += f"\t\t{agents[index].name}:obj({agents[index].name.lower()})"
            if index < len(agents)-1:
                result += ",\n"
            else:
                result += "\n"
                
        return result