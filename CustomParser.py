import re
import Constants
from Actions        import Actions
from Behavior       import Behavior
from Environment    import Environment
from VHDLAction     import VHDLAction
from VHDLAgent      import VHDLAgent
from VHDLStructure  import VHDLStructure
from VHDLVariable   import VHDLVariable


class CustomParser:
    def __init__(self, behavior: Behavior = None, environment: Environment = None, actions: Actions = None):
        self.__vhdlStructure = VHDLStructure()
        self.__behavior = behavior
        self.__environment = environment
        self.__actions = actions
        self.__all_variables : list = list()

    @property
    def vhdlStructure(self) -> VHDLStructure:
        return self.__vhdlStructure
    
    def parse_line(self, line:str) -> bool:
        try:
            splitted_line = re.findall(r"[\w']+|--\w+|--|<=|:=|:\w+|[^\w\s]", line)
            
            if self.skip_useless(splitted_line):
                return
            if self.parse_agent(splitted_line):
                return
            if self.parse_variable(splitted_line):
                return
            if self.parse_action(splitted_line):
                return
            
        except Exception as ex:
            print(f"Exception | CustomParser.parse_line() | Ex:{ex}")
            return None 

    def skip_useless(self, line: list) -> bool:
        if '--' in line[0] or "end" in line[0]:
            return True
        return False
    
    def parse_agent(self, line: list) -> bool:
        try:  
            if Constants.VHDL_ARCHITECTURE in line:
                self.__vhdlStructure.add_agent(VHDLAgent(line[1].capitalize()))
                return True
            
            if any(word in line for word in Constants.agents):
                self.__vhdlStructure.add_agent(VHDLAgent(line[0].capitalize()))
                sensetive_list:str = ""
                if "(" in line:
                    start_sensetive_index = line.index("(")
                    end_sensetive_index = line.index(")")
                    for i in range(start_sensetive_index+1, end_sensetive_index):
                        sensetive_list += line[i]
                    self.__vhdlStructure.get_last_agent().add_sensetive_list(sensetive_list)
                return True
            
            return False
        
        except Exception as ex:
            print(f"Exception | CustomParser.parse_agent() | Ex:{ex} | return None")
            return True
        
    def parse_variable(self, line: list) -> bool:
        try:
            for word in line:
                if word == ":":
                    if self.__vhdlStructure.get_last_agent() == None:
                        agent = None
                        agent_name = str()
                    else:
                        agent = self.__vhdlStructure.get_last_agent()
                        agent_name = self.__vhdlStructure.get_last_agent().name
                    
                    first_var_index = 0
                    if "port" in line[0].lower():
                        first_var_index = 2
                        
                    if any(word in line for word in Constants.variables):
                        first_var_index = 1
                    
                    
                    declaration_index:int = line.index(":")
                    
                    if line[declaration_index+1] in Constants.port_variable_types:
                        type_index = declaration_index+2
                    else:
                        type_index = declaration_index+1;

                    last_var_index = declaration_index-1
                    if last_var_index - first_var_index == 0:
                        if agent == None:
                            self.__vhdlStructure.add_variable(VHDLVariable(line[last_var_index], line[type_index], agent_name))
                        else:
                            self.__vhdlStructure.get_last_agent().add_variable(VHDLVariable(line[last_var_index], line[type_index], agent_name))
                        self.__all_variables.append(VHDLVariable(line[last_var_index], line[type_index], agent_name))
                        return True

                    variable_list:list = list()
                    i = first_var_index
                    for i in range(first_var_index, last_var_index+1):
                        if i%2 == first_var_index%2:
                            variable_list.append(line[i])
                    
                    for name in variable_list:
                        if agent == None:
                            self.__vhdlStructure.add_variable(VHDLVariable(name, line[type_index], agent_name))
                        else:
                            self.__vhdlStructure.get_last_agent().add_variable(VHDLVariable(name, line[type_index], agent_name))
                        self.__all_variables.append(VHDLVariable(name, line[type_index], agent_name))
                    return True
            return False
        
        except Exception as ex:
            print(f"Exception | CustomParser.parse_variable() | Ex:{ex} | return None")
            return True

    def parse_action(self, line: list) -> bool:
        try:
            if any(word in line for word in Constants.assign_actions):
                action_line_index = next((line.index(word) for word in line if word in Constants.assign_actions), None)
                
                preview = ' '.join(line[action_line_index-1 : len(line)-1])
                
                index = 0
                post_condition = "" 
                for index in range(0,len(line)-1):
                    variable = next((variable for variable in self.__all_variables if line[index] == variable.name), None)
                    if variable is not None:
                        if not variable.agent:
                            post_condition += variable.name
                        else:
                            post_condition += f"{variable.agent.lower()}.{variable.name}"
                    else:
                        if index == action_line_index:
                            post_condition += " = "
                        else:
                            post_condition += line[index]
                            
                if self.__vhdlStructure.get_last_agent().has_actions():
                    action_index = 1+self.__vhdlStructure.get_last_agent().actions[-1].index
                else:
                    action_index = 1
                    
                self.__vhdlStructure.get_last_agent().add_action(VHDLAction(line[action_line_index],"",self.__vhdlStructure.get_last_agent().name, preview, post_condition, action_index))
                
                return True
            return False
        
        except Exception as ex:
            print(f"Exception | CustomParser.parse_action() | Ex:{ex} | return None")
            return True
