from __future__ import annotations
from dataclasses import dataclass

from typing import List, Dict
from enum import Enum

from VHDL.VHDLStatements import *
from VHDL.VHDLDeclaration import *


# Other
#region Other

@dataclass
class ParameterSpecification():
    identifier : str
    discrete_range : DiscreteRange

@dataclass
class DiscreteRange():
    range_decl  : None
    subtype     : str
    subtype_js  : str

@dataclass
class IndexConstraint():
    pass

class VHDLFunctions(Enum):
    length = "'length"
    conv_std_logic_vector = "conv_std_logic_vector"
 
#endregion

@dataclass
class VHDLDesign:
    # primary_unity
    entity              : Entity    = None
    configuration       : None      = None
    package_declaration : None      = None

    # secondary_unit
    architecture        : Architecture  = None
    package_body        : None          = None

@dataclass
class VHDLData:
    design_list : List[VHDLDesign]

    agent_types     : Dict[(str, str), List[VHDLDeclaration]]
    agents          : List[VHDLStatement]
    declarations    : List[VHDLDeclaration]
    build_in_functions : List[VHDLFunctions]

    def has_type_declaration(self):
        return any(isinstance(declaration, TypeDeclaration) for declaration in self.declarations)

    def get_types(self):
        return [declaration for declaration in self.declarations if isinstance(declaration, TypeDeclaration)]