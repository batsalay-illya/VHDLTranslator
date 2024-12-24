import os, sys
import logging

from Debug import Debug

from CustomVhdlVisitor import CustomVhdlVisitor
from VHDL.VHDLStatements import *
from VHDL.VHDLDeclaration import *

from antlr4 import *

from VHDL.VHDLData import VHDLData
from ANTLR.vhdlLexer import vhdlLexer
from ANTLR.vhdlParser import vhdlParser

from ResultCreators.ActionCreator import ActionCreator
from ResultCreators.BehaviourCreator import BehaviourCreator
from ResultCreators.EnvironmentCreator import EnvironmentCreator


class ASCIIFileStream(FileStream):
    def __init__(self, file_name):
        super().__init__(file_name, encoding='ascii')

class UTF8FileStream(FileStream):
    def __init__(self, file_name):
        super().__init__(file_name, encoding='utf-8')

#Get path of .vhd file from command line
def get_filepath(output_log: logging.Logger) -> str:
    try:
        #D:\Work\Coding\VHDLTranslatorData\VHDL_Examples\hcms2905_driver_fsm.vhd
        #D:\Work\Coding\VHDLTranslatorData\To_Test\CaseIfExample.vhd
        #D:\Work\Coding\VHDLTranslatorData\To_Test\ConcurrentAssignmentExample.vhd
        #D:\Work\Coding\VHDLTranslatorData\To_Test\TypeUsageExample.vhd
        filepath = "D:\Work\Coding\VHDLTranslatorData\To_Test\CaseIfExample.vhd"
        #filepath = sys.argv[1]
        output_log.info(f"Reading file {filepath}")

        if os.path.exists(filepath):
            return filepath
            
        output_log.error("Invalid path or file name")
        sys.exit()

    except IndexError:
        output_log.error("Not enough arguments, file path expected")
        sys.exit()
        
    except Exception:
        output_log.error("Details:", exc_info=True)
        sys.exit()
  
#Read .vhd file using ANTLR
def translate_file(output_log : logging.Logger, filepath: str) -> VHDLData:
    try:
        file_stream : FileStream = None
        
        encoding : str = Debug.detect_encoding(output_log, filepath)

        if encoding == 'utf-8':
            file_stream = UTF8FileStream(filepath)      # Use UTF-8 encoding
        else:
            file_stream = FileStream(filepath)          # Use ASCII encoding as default

        lexer   = vhdlLexer(file_stream)
        stream  = CommonTokenStream(lexer)
        parser  = vhdlParser(stream)
        
        tree = parser.design_file()
        
        custom_visitor : CustomVhdlVisitor = CustomVhdlVisitor()
        custom_visitor.visit(tree)
        
        vhdlData       : VHDLData          = custom_visitor.get_vhdl_data()
        return vhdlData
        
    except Exception:
        output_log.error("Details:",exc_info=True)

def get_result_path(output_log : logging.Logger, vhd_path: str) -> str:
    try:
        result_path = os.path.join(os.getcwd(), "result")   #get 'result' folder path in program directory
        if not os.path.exists(result_path):                 #create 'result' folder in the program derictory if it does not exist
            os.makedirs(result_path)
            
        filename = os.path.basename(vhd_path)               #get name of .vhd file
        filename = filename.split('.')[0]                   #remove file type to get only file name
        return os.path.join(result_path, filename)          #return path for result files
    
    except Exception:
        output_log.error("Details:", exc_info=True)

def main():
    output_log : logging.Logger = Debug.get_logger("VHDLTranslator")
    
    try:
        vhdl_path : str = get_filepath(output_log)

        vhdlData = translate_file(output_log, vhdl_path)    

        result_path = get_result_path(output_log, vhdl_path)

        action_creator      : ActionCreator = ActionCreator()
        behaviour_creator   : BehaviourCreator = BehaviourCreator()
        environment_creator : EnvironmentCreator = EnvironmentCreator()
        
        action_creator.create_result(result_path, vhdlData)
        behaviour_creator.create_result(result_path, vhdlData)
        environment_creator.create_result(result_path, vhdlData)
        
    except Exception:
        output_log.error("Details:", exc_info=True)
    else:
        output_log.info("Code succesfully translated")
        output_log.info("Check 'result' folder in program directory")

if __name__ == "__main__":
    main()