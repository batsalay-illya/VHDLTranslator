import traceback

from typing import List

from Debug import Debug
from ResultCreators.ResultFile import ResultFile
from VHDL.VHDLData import VHDLData, VHDLFunctions
from VHDL.VHDLDeclaration import *

class EnvironmentCreator(ResultFile): 

    def __init__(self):
        self.output_log = Debug.get_logger("EnvironmentCreator")

    def create_result(self, result_path: str, vhdlData: VHDLData):
        try:
            result_file = self._create_file(f"{result_path}.env_descript")

            result_file.write("environment(\n")
            result_file.write(f"\ttypes:obj({self.__get_types(vhdlData)});\n")
                
            result_file.write(f"\tattributes:obj({self.__get_attributes(vhdlData)});\n")
            result_file.write(f"\tagent_types:obj({self.__get_agent_types(vhdlData)});\n")  
            result_file.write(f"\tagents:obj({self.__get_agents(vhdlData)});\n")            

            result_file.write(f"\tinstances:obj({self.__get_instances(vhdlData)});\n")
            result_file.write(f"\taxioms:obj({self.__get_axioms(vhdlData)});\n")
            result_file.write(f"\tlogic_formula:obj({self.__get_logic_formula(vhdlData)})\n")
            result_file.write(");")

            result_file.close()
        
        except Exception:
            self.output_log.error("Environment result status ... Fail", exc_info=True)
        else:
            self.output_log.info("Environment result status ... Success")
    
    def __get_types(self, vhdlData: VHDLData) -> str:
        if not vhdlData.has_type_declaration():
            return "Nil"

        result : str = ""
        types : List[TypeDeclaration] = vhdlData.get_types()

        for _type in types:
            if isinstance(_type, EnumerationType):
                result += f"\t\t{_type.name}:("
                result +=  ",".join(enumeration_literal for enumeration_literal in _type.enumeration_literals)
                result += ")"

        result = self.__put_content_inside_brackets(result)

        return result

    def __get_attributes(self, vhdlData: VHDLData) -> str:
        if not vhdlData.build_in_functions and not [declaration for declaration in vhdlData.declarations if isinstance(declaration, Generic)]:
            return "Nil"

        result : str = ""

        for func in vhdlData.build_in_functions:
            if func is VHDLFunctions.conv_std_logic_vector:
                result += f"conv_std_logic_vector:(int,int) -> Bits(8)"
                
            if func is VHDLFunctions.length:
                result += f"length:(Bits(8)) -> int"

            result += ",\n"

        result += ',\n'.join(f"{declaration.name}:{declaration.subtype_indication_js}" for declaration in vhdlData.declarations if isinstance(declaration, Generic))

        result = self.__add_indentation(result, 2)
        result = self.__put_content_inside_brackets(result)

        return result
        
    def __get_agent_types(self, vhdlData: VHDLData) -> str:
        if not vhdlData.declarations:
            return "Nil"

        x : int = 0
        x_max : int = len(vhdlData.agent_types.keys())-1
        result : str = ""

        result += "\n"

        for (statement_name, agent_name), declarations in vhdlData.agent_types.items():
            if len(declarations) == 0:
                result += f"\t\t{statement_name}:obj(Nil)"
            else:
                result += f"\t\t{statement_name}:obj(\n"
                result += ",\n".join(
                    f"\t\t\t{declaration.name}:({declaration.subtype_indication_js})" 
                    for declaration in declarations
                    if not isinstance(declaration, TypeDeclaration)
                )
                result += "\n\t\t)"
                
            if x < x_max:
                result += ",\n"
            else:
                result += "\n"

            x+=1

        result += "\t"

        return result
    
    def __get_agents(self, vhdlData: VHDLData) -> str:
        if not vhdlData.agents:
            return "Nil"

        result : str = ",\n".join(f"\t\t{agent.statement_name}:obj({agent.agent_name})" for agent in vhdlData.agents)

        result = self.__put_content_inside_brackets(result)

        return result
    
    def __get_instances(self, vhdlData: VHDLData) -> str:
        return "Nil"
    
    def __get_axioms(self, vhdlData: VHDLData) -> str:
        return "Nil"
    
    def __get_logic_formula(self, vhdlData: VHDLData) -> str:
        result : str = ""

        result += " &&\n".join(
            f"\t\t{declaration.agent_name}.{declaration.name} == {declaration.expression_with_agents}"
            for declaration in vhdlData.declarations
            if isinstance(declaration, (Port, SignalDeclaration, VariableDeclaration)) and declaration.expression_with_agents is not None
        )

        if len([declaration for declaration in vhdlData.declarations if isinstance(declaration, Generic)]):
            result += " &&\n"

        result += " &&\n".join(
            f"\t\t{declaration.name} == {declaration.expression_with_agents}"
            for declaration in vhdlData.declarations
            if isinstance(declaration, Generic)
        )

        if not result:
            return "Nil"

        result = self.__put_content_inside_brackets(result)

        return result

    def __add_indentation(self, content: str, indentation_amount: int = 1) -> str:
        return '\n'.join(('\t' * indentation_amount) + line for line in content.splitlines())

    def __put_content_inside_brackets(self, content: str, indentation_amount: int = 1) -> str:
        return "\n" + content + "\n" + (indentation_amount*"\t")
        