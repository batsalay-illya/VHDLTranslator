import os
import sys
from CustomParser import CustomParser
from Environment import Environment
from Behavior import Behavior
from Actions import Actions
from VHDLVariable import VHDLVariable

customParser = CustomParser()   
environment = Environment()
behavior = Behavior()
actions = Actions()         

#Get path of .vhd file from command line
def get_filepath() -> str:
    try:
        filepath = str(sys.argv[1])
        if os.path.exists(filepath):
            return filepath
            
        print(f"Invalid path or file name...")
        sys.exit()

    except IndexError:
        print("Not enough arguments, file path expected...")
        sys.exit()
  
#Read .vhd file line by line and parse it
def translate_file(filepath:str) -> None:
    global customParser
    global behavior
    global environment
    global actions
    
    customParser = CustomParser(behavior, environment, actions)

    with open(filepath) as file:
        for line in file:
            if line.isspace():                                  #skip blank lines
                continue

            customParser.parse_line(line)

def get_result_path(vhd_path:str) -> str:
    result_path = os.path.join(os.getcwd(), "result")   #get 'result' folder path in program directory
    if not os.path.exists(result_path):                 #create 'result' folder in the program derictory if it does not exist
        os.makedirs(result_path)
        
    filename = os.path.basename(vhd_path)               #get name of .vhd file
    filename = filename.split('.')[0]                   #remove file type to get only file name
    return os.path.join(result_path, filename)          #return path for result files

def main():
    global behavior
    global environment
    global actions
    try:
        vhd_path : str = get_filepath()
        translate_file(vhd_path)    

        result_path = get_result_path(vhd_path)

        actions.create_file(result_path, customParser.vhdlStructure)
        behavior.create_file(result_path, customParser.vhdlStructure)
        environment.create_file(result_path, customParser.vhdlStructure.global_variables, customParser.vhdlStructure.agents)

        print("Check 'result' folder in program directory...")
        
    except Exception as ex:
        print(f"Exception: {ex}")
        return

if __name__ == "__main__":
    main()
    