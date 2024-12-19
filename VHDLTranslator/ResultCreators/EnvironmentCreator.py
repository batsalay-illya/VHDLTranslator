import traceback

from typing import List

from Debug import Debug
from ResultCreators.ResultFile import ResultFile
from VHDL.VHDLData import EnumerationTypeDefinition, VHDLData
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
        if not vhdlData.declaration_list:
            return "Nil"

        types : List[TypeDeclaration] = [
            type_declaration for type_declaration in vhdlData.declaration_list
            if isinstance(type_declaration, TypeDeclaration)
        ]

        if not types:
            return "Nil"

        result : str = ",\n".join(f"\t\t{t.name}TYPE:obj(\n\t\t\t" +
            (",\n\t\t\t".join(t.type_definition.enumeration_literals) if isinstance(t.type_definition, EnumerationTypeDefinition) else "") +
            "\n\t\t)"
            for t in types
        )
        result = self.__put_content_inside_brackets(result)

        return result

    def __get_attributes(self, vhdlData: VHDLData) -> str:
        if not vhdlData.declaration_list:
            return "Nil"

        type_declarations : List[TypeDeclaration] = [type_declaration for type_declaration in vhdlData.declaration_list if isinstance(type_declaration, TypeDeclaration)]

        if not type_declarations:
            return "Nil"

        temp : List[str] = [f"{declaration.name}:{declaration.name}TYPE" for declaration in type_declarations]
        result : str = ',\n'.join(temp)

        result = self.__add_indentation(result, 2)
        result = self.__put_content_inside_brackets(result)

        return result
        
    def __get_agent_types(self, vhdlData: VHDLData) -> str:
        if not vhdlData.declaration_list:
            return "Nil"

        result : str = ""
        agent_content : str = ""
        index_x : int = 1

        agent_keys = vhdlData.sorted_declaration_list.keys()

        for agent_name in list(agent_keys):
            agent_declarations_lenght : int = len(vhdlData.sorted_declaration_list[agent_name])
            if agent_declarations_lenght == 0:
                result += f"\t\t{agent_name}:obj(Nil)"
                continue
            
            result += f"\t\t{agent_name}:obj("

            agent_content = ",\n".join(f"\t\t\t{declaration.name}:{declaration.subtype_indication_js}" for declaration in vhdlData.sorted_declaration_list[agent_name] if isinstance(declaration, (Port, SignalDeclaration, VariableDeclaration)))

            result += self.__put_content_inside_brackets(agent_content, 2)

            index_x += 1
            if index_x > len(vhdlData.sorted_declaration_list.keys()):
                result += f")"
            else:
                result += f"),\n"
                
        result = self.__put_content_inside_brackets(result)

        return result
    
    def __get_agents(self, vhdlData: VHDLData) -> str:
        if not vhdlData.agent_list:
            return "Nil"

        result : str = ""

        result = ",\n".join(f"\t\t{agent.statement_name}:obj({agent.agent_name})" for agent in vhdlData.agent_list)

        result = self.__put_content_inside_brackets(result)

        return result
    
    def __get_instances(self, vhdlData: VHDLData) -> str:
        return "Nil"
    
    def __get_axioms(self, vhdlData: VHDLData) -> str:
        return "Nil"

        if not vhdlData.entity.generic:
            return "Nil"

        result : str = ",\n".join(f"{generic.name}:{generic.subtype_indication_js}" for generic in vhdlData.entity.generic)

        result = self.__add_indentation(result, 2)
        result = self.__put_content_inside_brackets(result)

        return result
    
    def __get_logic_formula(self, vhdlData: VHDLData) -> str:
        if not vhdlData.declaration_list:
            return "Nil"

        declarations_with_axiom = [declaration for declaration in vhdlData.declaration_list if hasattr(declaration, 'expression') and not isinstance(declaration, Generic)]

        result : str = " &&\n".join(f"\t\t{declaration.name} == {declaration.expression}" for declaration in declarations_with_axiom if declaration.expression is not None)

        result = self.__put_content_inside_brackets(result)

        return result

    def __add_indentation(self, content: str, indentation_amount: int = 1) -> str:
        return '\n'.join(('\t' * indentation_amount) + line for line in content.splitlines())

    def __put_content_inside_brackets(self, content: str, indentation_amount: int = 1) -> str:
        return "\n" + content + "\n" + (indentation_amount*"\t")
        