import os, sys, traceback
from CustomVhdlVisitor import CustomVhdlVisitor
from VHDL.VHDLStatements import *
from VHDL.VHDLDeclaration import *

from antlr4 import *

from VHDL.VHDLData import VHDLData
from ANTLR.vhdlLexer import vhdlLexer
from ANTLR.vhdlParser import vhdlParser
from ResultGenerators.ActionCreator import ActionCreator
from ResultGenerators.BehaviourCreator import BehaviourCreator
from ResultGenerators.EnvironmentCreator import EnvironmentCreator

class Debug():
    def print_vhdl_all_declarations(data: VHDLData, skip_data_check: bool = False):
        print("##### DEBUG_DECLARATIONS #####")
        print("{")

        if not skip_data_check:
            print(f"\t data is None: {'True' if data.entity is None else 'False'}")
        
        if not data.declaration_list:
            print(f"\t declaration list is empty...")
        else:
            print(f"\t declaration list length:{len(data.declaration_list)}")
            print(f"\t declaration list:")
            for declaration in data.declaration_list:
                print(f"\t {declaration}")

        print("}\n")

    def print_vhdl_entity(data: VHDLData, skip_data_check: bool = False):
        print("##### DEBUG_ENTITY #####")
        print("{")

        if not skip_data_check:
            print(f"\t data is None: {'True' if data.entity is None else 'False'}")
        
        print(f"\t identifier: {data.entity.name}")

        if data.entity is not None:

            # Port
            if not data.entity.port:
                print("\t entity.port: None")
            else:
                print("\t entity.port: ")
                for port in data.entity.port:
                    print(f"\t [name:{port.name}, agent_name:{port.agent_name}, signal_mode:{port.signal_mode}, subtype_indication:{port.subtype_indication}, expression:{port.expression}];")

            print()

            # Generic
            if not data.entity.generic:
                print("\t entity.generic: None")
            else:
                print("\t entity.generic: ")
                for generic in data.entity.generic:
                    print(f"\t [name:{generic.name}, agent_name:{generic.agent_name}, subtype_indication:{generic.subtype_indication}, expression:{generic.expression}];")

        else:
            print(f"\tentity is None...")        

        print("}\n")
        
    def print_vhdl_architecture(data: VHDLData, skip_data_check: bool = False, more_details: bool = False):
        print("##### DEBUG_ARCHITECTURE #####")
        print("{")

        if not skip_data_check:
            print(f"\t data is None: {'True' if data.entity is None else 'False'}")
        
        print(f"\t identifier: {data.architecture.name}")
                    
        Debug.print_vhdl_architecture_declarations(data, skip_data_check = True, is_sub_call = True)

        Debug.print_vhdl_architecture_statements(data, skip_data_check = True, is_sub_call = True, more_details = True)

        print("}")

    def print_vhdl_architecture_declarations(data: VHDLData, skip_data_check: bool = False, is_sub_call: bool = False):
        if not is_sub_call:
            print("##### DEBUG_ARCHITECTURE_DECLARATIONS #####")
            print("{")

        if not skip_data_check:
            print(f"\t data is None: {'True' if data.entity is None else 'False'}")
        
        print("\t architecture.declarations:", end="")
        Debug.print_vhdl_declaration(data.architecture.declarations)
              
        if not is_sub_call:
            print("}")

    def print_vhdl_architecture_statements(data: VHDLData, skip_data_check: bool = False, is_sub_call: bool = False, more_details: bool = False):
        if not is_sub_call:
            print("##### DEBUG_ARCHITECTURE_DECLARATIONS #####")
            print("{")

        if not skip_data_check:
            print(f"\t data is None: {'True' if data.entity is None else 'False'}")
       
        if not data.architecture.statements:
            print("\t architecture.statements is empty...")
        else:
            if more_details:
                print("\t architecture.statements:")

                print("\t [")
                for statement in data.architecture.statements:
                    #print(f"\t\t {statement};\n")
                    Debug.print_vhdl_statement(statement, tab_amount=2)
                print("\t ]")

            else:
                print(f"\t architecture.statements length:{len(data.architecture.statements)}")

        if not is_sub_call:
            print("}")

    def print_vhdl_declaration(declaration_list : List[VHDLDeclaration], tab_index : int = 1):
        tab : str = "\t"

        if not declaration_list:
            print("None")
            return

        print()

        print(f"{tab_index * tab}[")

        for declaration in declaration_list:
            print(f"{tab_index * tab} {declaration}")

        print(f"{tab_index * tab}]")

    def print_vhdl_statement(statement: any, tab_amount : int = 1):
        tab : str = "\t"

        if isinstance(statement, BlockStatement):
            print(f"{tab_amount * tab} {statement}")

        if isinstance(statement, ProcessStatement):
            print(f"{tab_amount * tab} ProcessStatement \n{tab_amount * tab} [")
            print(f"{(tab_amount+1) * tab} name = {statement.statement_name},")
            print(f"{(tab_amount+1) * tab} agent_name = {statement.agent_name},")

            if not statement.sensitivity_list:
                print(f"{(tab_amount+1) * tab} sensetivity_list = None,")
                print(f"{(tab_amount+1) * tab} sensetivity_list_with_agents = None,")
            else:
                print(f"{(tab_amount+1) * tab} sensetivity_list = {statement.sensitivity_list}")
                print(f"{(tab_amount+1) * tab} sensetivity_list_with_agents = {statement.sensitivity_list_with_agents}")

            if not statement.declarations:
                print(f"{(tab_amount+1) * tab} declarations = None,")
            else:
                print(f"{(tab_amount+1) * tab} declarations: \n{(tab_amount+1) * tab} [")
                for declaration in statement.declarations:
                    print(f"{(tab_amount+2) * tab}{declaration};")
                print(f"{(tab_amount+1) * tab} ]")

            if not statement.statements:
                print(f"{(tab_amount+1) * tab} statements = None")
            else:
                print(f"{(tab_amount+1) * tab} statements \n{(tab_amount+1) * tab} [")
                for sub_statement in statement.statements:
                    Debug.print_vhdl_statement(sub_statement, tab_amount+2)
                print(f"{(tab_amount+1) * tab} ]")

            print(f"{tab_amount * tab} ]")

        if isinstance(statement, ConcurrentProcedureCallStatement):
            print(f"{tab_amount * tab} {statement}")

        if isinstance(statement, ConcurrentAssertionStatement):
            print(f"{tab_amount * tab} {statement}")

        if isinstance(statement, ConcurrentSignalAssignmentStatement):
            print(f"{tab_amount * tab} {statement}")

        if isinstance(statement, ComponentInstantiationStatement):
            print(f"{tab_amount * tab} {statement}")

        if isinstance(statement, GenerateStatement):
            print(f"{tab_amount * tab} {statement}")

        if isinstance(statement, ConcurrentBreakStatement):
            print(f"{tab_amount * tab} {statement}")

        if isinstance(statement, SimultaneousStatement):
            print(f"{tab_amount * tab} {statement}")

        if isinstance(statement, WaitStatement):
            print(f"{tab_amount * tab} {statement}")

        if isinstance(statement, AssertionStatement):
            print(f"{tab_amount * tab} {statement}")

        if isinstance(statement, ReportStatement):
            print(f"{tab_amount * tab} {statement}")

        if isinstance(statement, SignalAssignment):
            print(f"{tab_amount * tab} {statement}")

        if isinstance(statement, ConditionalSignalAssignment):
            print(f"{tab_amount * tab} ConditionalSignalAssignment \n{tab_amount * tab} [")

            print(f"{(tab_amount+1) * tab} name = {statement.statement_name},")
            print(f"{(tab_amount+1) * tab} agent_name = {statement.agent_name},")
            print(f"{(tab_amount+1) * tab} target = {statement.target},")
            print(f"{(tab_amount+1) * tab} target_with_agent = {statement.target_with_agent},")
            print(f"{(tab_amount+1) * tab} opts = {statement.opts if statement.opts is not None else None},")
            Debug.print_vhdl_statement(statement.conditional_waveforms, tab_amount+1)

            print(f"{tab_amount * tab} ]")

        if isinstance(statement, ConditionalWaveform):
            print(f"{tab_amount * tab} ConditionalWaveform \n{tab_amount * tab} [")

            print(f"{(tab_amount+1) * tab} waveform = {statement.waveform},")
            print(f"{(tab_amount+1) * tab} waveform_with_agents = {statement.waveform_with_agents},")
            print(f"{(tab_amount+1) * tab} condition = {statement.condition},")
            if statement.conditional_waveforms is not None:
                Debug.print_vhdl_statement(statement.conditional_waveforms, tab_amount+1)

            print(f"{tab_amount * tab} ]")

        if isinstance(statement, SelectedSignalAssignment):
            print(f"{tab_amount * tab} {statement}")

        if isinstance(statement, VariableAssignment):
            print(f"{tab_amount * tab} {statement}")

        if isinstance(statement, IfStatement):
            print(f"{tab_amount * tab} IfStatement \n{tab_amount * tab} [")
            print(f"{(tab_amount+1) * tab} name = {statement.statement_name},")
            print(f"{(tab_amount+1) * tab} agent_name = {statement.agent_name},")

            print(f"{(tab_amount+1) * tab} condition = {statement.condition},")
            print(f"{(tab_amount+1) * tab} condition_with_agents = {statement.condition_with_agents},")

            # Is statements
            if not statement.statements:
                print(f"{(tab_amount+1) * tab} statements = None")
            else:
                print(f"{(tab_amount+1) * tab} statements \n{(tab_amount+1) * tab} [")
                for sub_statement in statement.statements:
                    Debug.print_vhdl_statement(sub_statement, tab_amount+2)
                print(f"{(tab_amount+1) * tab} ]")

            print(f"{(tab_amount+1) * tab} elsif_condition = {statement.elsif_condition},")
            print(f"{(tab_amount+1) * tab} elsif_condition_with_agents = {statement.elsif_condition_with_agents},")

            # Elsif statements
            if not statement.elsif_statements:
                print(f"{(tab_amount+1) * tab} elsif_statements = None")
            else:
                print(f"{(tab_amount+1) * tab} elsif_statements \n{(tab_amount+1) * tab} [")
                for sub_statement in statement.elsif_statements:
                    Debug.print_vhdl_statement(sub_statement, tab_amount+2)
                print(f"{(tab_amount+1) * tab} ]")

            # Else statements
            if not statement.else_statements:
                print(f"{(tab_amount+1) * tab} else_statements = None")
            else:
                print(f"{(tab_amount+1) * tab} else_statements \n{(tab_amount+1) * tab} [")
                for sub_statement in statement.else_statements:
                    Debug.print_vhdl_statement(sub_statement, tab_amount+2)
                print(f"{(tab_amount+1) * tab} ]")

            print(f"{tab_amount * tab} ]")
           
        if isinstance(statement, CaseStatement):
            print(f"{tab_amount * tab} {statement}")

        if isinstance(statement, LoopStatement):
            print(f"{tab_amount * tab} {statement}")

        if isinstance(statement, NextStatement):
            print(f"{tab_amount * tab} {statement}")

        if isinstance(statement, ExitStatement):
            print(f"{tab_amount * tab} {statement}")

        if isinstance(statement, ReturnStatement):
            print(f"{tab_amount * tab} {statement}")

        if isinstance(statement, BreakStatement):
            print(f"{tab_amount * tab} {statement}")

        if isinstance(statement, ProcedureCallStatement):
            print(f"{tab_amount * tab} {statement}")

#Get path of .vhd file from command line
def get_filepath() -> str:
    try:
        filepath = sys.argv[1]
        print(f"Reading file {filepath}")

        if os.path.exists(filepath):
            return filepath
            
        print(f"Invalid path or file name...")
        sys.exit()

    except IndexError:
        print("Not enough arguments, file path expected...")
        sys.exit()
        
    except Exception:
        print(traceback.format_exc())
        #print(traceback.exc_info()[2])
        sys.exit()
  
#Read .vhd file using ANTLR
def translate_file(filepath: str) -> VHDLData:
    try:
        file_stream = FileStream(filepath)

        lexer   = vhdlLexer(file_stream)
        stream  = CommonTokenStream(lexer)
        parser  = vhdlParser(stream)
        
        tree = parser.design_file()
        
        custom_visitor : CustomVhdlVisitor = CustomVhdlVisitor()
        custom_visitor.visit(tree)
        
        vhdlData       : VHDLData          = custom_visitor.get_vhdl_data()
        return vhdlData
        
    except Exception:
        print(traceback.format_exc())
        #print(traceback.exc_info()[2])

def get_result_path(vhd_path: str) -> str:
    try:
        result_path = os.path.join(os.getcwd(), "result")   #get 'result' folder path in program directory
        if not os.path.exists(result_path):                 #create 'result' folder in the program derictory if it does not exist
            os.makedirs(result_path)
            
        filename = os.path.basename(vhd_path)               #get name of .vhd file
        filename = filename.split('.')[0]                   #remove file type to get only file name
        return os.path.join(result_path, filename)          #return path for result files
    
    except Exception:
        print(traceback.format_exc())
        #print(traceback.exc_info()[2])

def main():
    try:
        vhd_path : str = get_filepath()
        vhdlData = translate_file(vhd_path)    

        result_path = get_result_path(vhd_path)

        action_creator      : ActionCreator = ActionCreator()
        behaviour_creator   : BehaviourCreator = BehaviourCreator()
        environment_creator : EnvironmentCreator = EnvironmentCreator()
        
        action_creator.create_file(result_path, vhdlData)
        behaviour_creator.create_file(result_path, vhdlData)
        environment_creator.create_file(result_path, vhdlData)
        
        #Debug.print_vhdl_all_declarations(data = vhdlData, skip_data_check = True)
        #Debug.print_vhdl_entity(data = vhdlData, skip_data_check = True)
        #Debug.print_vhdl_architecture(data = vhdlData, skip_data_check = True)
        
    except Exception:
        print(traceback.format_exc())
        ##print(traceback.exc_info()[2])

    else:
        print("Code succesfully translated.")
        print("Check 'result' folder in program directory...")

if __name__ == "__main__":
    main()
    