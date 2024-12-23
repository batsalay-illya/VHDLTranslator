import traceback
import Constants as const

from typing import Tuple
from ResultCreators.ResultFile import ResultFile
from VHDL.VHDLData import VHDLData, VHDLDesign
from VHDL.VHDLStatements import *

class BehaviourCreator(ResultFile): 
    def __init__(self) -> None:
        pass

    def create_result(self, result_path : str, vhdlData : VHDLData):
        try:
            result_file = self._create_file(f"{result_path}.behp")

            self.__iterate_trough_designs(vhdlData, result_file)

            result_file.close()

        except Exception:
            print("Behaviour result status ... Fail")
            print(traceback.format_exc())
        else:
            print("Behaviour result status ... Success")
        
    def __iterate_trough_designs(self, vhdlData: VHDLData, result_file) -> None:
        for design in vhdlData.design_list:
            if design.architecture is None: continue

            self.__write_concurrent_behaviour(design, result_file)
            self.__write_sequential_behaviour(design, result_file)

    def __write_concurrent_behaviour(self, vhdlDesign: VHDLDesign, result_file) -> None:
        concurrent_behaviour : str = "beh0 = "
        statements : List[VHDLStatement] = vhdlDesign.architecture.statements
        
        concurrent_behaviour += " || ".join(self.__get_concurrent_statement(statement) for statement in statements)
        result_file.write(f"{concurrent_behaviour},\n")

    def __get_concurrent_statement(self, statement: any) -> str:
        if isinstance(statement, BlockStatement):
            pass

        if isinstance(statement, ConcurrentProcedureCallStatement):
            pass

        if isinstance(statement, ConcurrentAssertionStatement):
            pass

        if isinstance(statement, ConcurrentBreakStatement):
            pass

        if isinstance(statement, (SelectedSignalAssignment, ConditionalSignalAssignment)):
            return f"Sensitive({statement.full_behaviour_name})"

        if isinstance(statement, ProcessStatement):
            if not statement.sensitivity_list:
                 return f"Sensitive({statement.statement_name})"

            sensitivity_list : str = ""
            for index in range(len(statement.sensitivity_list)):
                sensitivity_list += f"sensitive(snv{statement.sensitivity_list[index]})"
                if index+1 < len(statement.sensitivity_list):
                    sensitivity_list += " || "

            return f"Sensitive({statement.statement_name}, {sensitivity_list})"


    def __write_sequential_behaviour(self, vhdlDesign: VHDLDesign, result_file):
        for statement in vhdlDesign.architecture.statements:
            self.__visit_statement(statement, result_file)

    def __visit_statement(self, statement : VHDLStatement, result_file):
        if isinstance(statement, ProcessStatement):
            result_file.write(f"{statement.statement_name} = (")
            result_file.write("; ".join(self.__get_behaviours(statement.statements)))
            result_file.write("),\n")

            # Visit childs
            self.__visit_childs(statement.statements, result_file)


        if isinstance(statement, IfStatement):
            result_file.write(f"{statement.full_behaviour_name} = (")
            result_file.write(" + ".join(self.__get_behaviours(statement.statements)))
            if statement.elsif_statements:
                result_file.write(" + !")
                result_file.write(" + !".join(self.__get_behaviours(statement.elsif_statements)))

            if statement.else_statements:
                result_file.write(" + !")
                result_file.write(" + !".join(self.__get_behaviours(statement.else_statements)))

            result_file.write("),\n")

            # Visit childs
            self.__visit_childs(statement.statements, result_file)
            self.__visit_childs(statement.elsif_statements, result_file) if statement.elsif_statements else None
            self.__visit_childs(statement.else_statements, result_file) if statement.else_statements else None


        if isinstance(statement, CaseStatement):
            self.__visit_childs(statement.case_alternatives, result_file)

        if isinstance(statement, CaseAlternative):
            result_file.write(f"{statement.full_behaviour_name} = (")
            result_file.write("; ".join(self.__get_behaviours(statement.statements)))
            result_file.write("),\n")

            self.__visit_childs(statement.statements, result_file)

        if isinstance(statement, const.SIMPLE_ASSIGN_STATEMENTS):
            return

    def __visit_childs(self, childs : VHDLStatement, result_file):
        for statement in childs:
            self.__visit_statement(statement, result_file)

    def __get_behaviours(self, statement_list: List[VHDLStatement]):
        result : List[str] = []

        for statement in statement_list:
            if statement.statement_class is CaseStatement:
                result.append((" + ").join([alternative.full_behaviour_name for alternative in statement.case_alternatives]))
                continue

            result.append(statement.full_behaviour_name)

        return result