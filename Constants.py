agents = ["process", "block", "generate"]

assign_actions = ["<=", ":="]
condition_action = ["if"]

variables = ["signal", "variable", "constant"]
port_variable_types = ["in", "out"]
translated_variables = {r'std_logic' : "bool", r'integer' : "int", r'\d+\sdownto\s\d+' : r'\d+'}
translated_actions = {"<=":"asn", ":=":"v_asn", "if": "if"}
end_token = ["end", ";"]

VHDL_ARCHITECTURE = "architecture"