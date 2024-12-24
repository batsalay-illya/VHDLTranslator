from VHDL.VHDLStatements import ProcessStatement, SignalAssignment, VariableAssignment


vhdl_types = {
    "bit" : "bool",
    "bit_vector" : "(int)->bool",
    "std_logic" : "bool",
    "std_logic_vector" : "Bits",

    "integer" : "int",
    "natural" : "int",
    "positive" : "int",
    "real" : "double",

    "array" : "Array[]",
    "record" : "NON-DIFINED",

    "boolean" : "bool",
    "character" : "char",
    "string" : "String"
}

MODULE = "module"

CONCURRENT_STATEMENTS = [ProcessStatement]

SIMPLE_ASSIGN_STATEMENTS = (SignalAssignment, VariableAssignment)