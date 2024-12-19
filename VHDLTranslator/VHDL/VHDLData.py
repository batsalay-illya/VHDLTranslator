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

# Type definition
#region Type definition
@dataclass
class TypeDefinition():
    pass

@dataclass
class AccessTypeDefinition():
    subtype     : str
    subtype_js  : str

@dataclass
class FileTypeDefinition():
    subtype     : str
    subtype_js  : str

@dataclass
class UnconstrainedArrayDefinition():
    subtype_definition : List[str]
    subtype     : str
    subtype_js  : str

@dataclass
class ConstrainedArrayDefinition():
    index_constraint    : IndexConstraint
    subtype             : str
    subtype_js          : str

@dataclass
class RecordTypeDefinition():
    pass

@dataclass
class EnumerationTypeDefinition():
    enumeration_literals : List[str]
    
#endregion
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

    sorted_declaration_list : Dict[str, List[VHDLDeclaration]]
    declaration_list : List[VHDLDeclaration]
    agent_list : List[VHDLStatement]

    def sorted_declaration_list_append(self, key: str, declaration: List[VHDLDeclaration]):
        if key in self.sorted_declaration_list:
            self.sorted_declaration_list[key].extend(declaration)
        else:
            self.sorted_declaration_list[key] = declaration