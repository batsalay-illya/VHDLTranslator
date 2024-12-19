import traceback

from ResultCreators.ResultFile import ResultFile
from VHDL.VHDLData import VHDLData, VHDLDesign
from VHDL.VHDLStatements import *

class ActionCreator(ResultFile): 

    def create_result(self, result_path : str, vhdlData : VHDLData):
        try:
            result_file = self._create_file(f"{result_path}.act")

            self.__iterate_trough_designs(vhdlData, result_file)

            result_file.close()

        except Exception:
            print("Action result status ... Fail")
            print(traceback.format_exc())
        else:
            print("Action result status ... Success")

    def __iterate_trough_designs(self, vhdlData: VHDLData, result_file) -> None:
        for design in vhdlData.design_list:
            if design.architecture is None: continue

            self.__write_actions_from_design(design, result_file)

    def __write_actions_from_design(self, vhdl_design: VHDLDesign, result_file):
        for statement in vhdl_design.architecture.statements:
            self.__visit_statement(statement, result_file)

    def __visit_statement(self, statement : VHDLStatement, result_file):
        if isinstance(statement, ProcessStatement):
            for process_statement in statement.statements:
                self.__visit_statement(process_statement, result_file)


        if isinstance(statement, IfStatement):
            result_file.write(f"{statement.full_behaviour_name} = (({statement.condition_with_agents}) ->(\"{statement.get_root_statement().statement_name}#{statement.get_root_statement().agent_name}: action '{statement.condition}';\") (1)),\n")

            for if_statement in statement.statements:
                self.__visit_statement(if_statement, result_file)

            for elsif_statement in statement.elsif_statements:
                self.__visit_statement(elsif_statement, result_file)

            for else_statement in statement.else_statements:
                self.__visit_statement(else_statement, result_file)

        if isinstance(statement, CaseStatement):
            for alternative in statement.case_alternatives:
                self.__visit_statement(alternative, result_file)

        if isinstance(statement, CaseAlternative):
            result_file.write(f"{statement.full_behaviour_name} = (({statement.choices_with_agents}) ->(\"{statement.get_root_statement().statement_name}#{statement.get_root_statement().agent_name}: action '{statement.choices}';\") (1)),\n")
            for alt_statement in statement.statements:
                self.__visit_statement(alt_statement, result_file)

        if isinstance(statement, SignalAssignment):
            result_file.write(f"{statement.full_behaviour_name} = ((1) ->(\"{statement.get_root_statement().statement_name}#{statement.get_root_statement().agent_name}: action '{statement.target} <= {statement.waveform}';\") ({statement.target_with_agent} = {statement.waveform_with_agents})),\n")

        if isinstance(statement, VariableAssignment):
            result_file.write(f"{statement.full_behaviour_name} = ((1) ->(\"{statement.get_root_statement().statement_name}#{statement.get_root_statement().agent_name}: action '{statement.target} <= {statement.expression}';\") ({statement.target_with_agent} = {statement.expression_with_agents})),\n")