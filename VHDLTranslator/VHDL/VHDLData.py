from __future__ import annotations
from dataclasses import dataclass

from typing import List

from VHDL.VHDLStatements import VHDLStatement
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
class ScalarTypeDefinition():
    pass

@dataclass
class CompositeTypeDefinition():
    pass

@dataclass
class AccessTypeDefinition():
    pass

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
#endregion

#endregion

@dataclass
class MainData:
    name : str

#region Entity  
@dataclass
class Entity(MainData):
    generic : List[Generic]
    port    : List[Port]
#endregion

#region Architecture
@dataclass    
class Architecture(MainData):
    declarations : List[VHDLDeclaration]
    statements   : List[VHDLStatement]
#endregion    

@dataclass
class VHDLData:
    entity           : Entity
    architecture     : Architecture
    
    declaration_list : List[VHDLDeclaration]
    