from __future__ import annotations
from dataclasses import dataclass

from typing import List, Dict

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

    agent_types     : Dict[str, List[VHDLDeclaration]]
    agents          : List[VHDLStatement]
    declarations    : List[VHDLDeclaration]

    def has_type_declaration(self):
        return any(isinstance(declaration, TypeDeclaration) for declaration in self.declarations)

    def get_types(self):
        return [declaration for declaration in self.declarations if isinstance(declaration, TypeDeclaration)]