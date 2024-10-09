from dataclasses import dataclass
from typing import List


@dataclass
class VHDLDeclaration():
    name       : str
    agent_name : str

@dataclass
class Port(VHDLDeclaration):
    signal_mode             : str
    subtype_indication      : str
    subtype_indication_js   : str
    expression              : str
    expression_with_agents  : str

@dataclass
class Generic(VHDLDeclaration):
    subtype_indication      : str
    subtype_indication_js   : str
    expression              : str
    expression_with_agents  : str

@dataclass
class SubprogramBody(VHDLDeclaration):
    specification       : None
    declarations        : List[VHDLDeclaration]
    #statements          : List[VHDLStatement]
    subprogram_kind     : None

@dataclass
class TypeDeclaration(VHDLDeclaration):
    identifier      : str
    type_definition : str

@dataclass
class SubtypeDeclaration(VHDLDeclaration):
    identifier              : str
    subtype_indication      : str
    subtype_indication_js   : str

@dataclass
class ConstantDeclaration(VHDLDeclaration):
    subtype_indication      : str
    subtype_indication_js   : str
    expression              : str
    expression_with_agents  : str

@dataclass
class SignalDeclaration(VHDLDeclaration):
    subtype_indication      : str
    subtype_indication_js   : str
    signal_kind             : str
    expression              : str
    expression_with_agents  : str

@dataclass
class VariableDeclaration(VHDLDeclaration):
    subtype_indication      : str
    subtype_indication_js   : str
    expression              : str
    expression_with_agents  : str

@dataclass
class FileDeclaration(VHDLDeclaration):
    identifier_list         : List[str]
    subtype_indication      : str
    subtype_indication_js   : str
    file_open_information   : None

@dataclass
class AliasDeclaration(VHDLDeclaration):
    designator  : None
    indication  : None
    name        : None
    signature   : None

@dataclass
class ComponentDeclaration(VHDLDeclaration):
    identifier      : str
    generic_clause  : List[Generic]
    port_clause     : List[Port]

@dataclass
class AttributeDeclaration(VHDLDeclaration):
    label_colon : str
    name        : str

@dataclass
class AttributeSpecification(VHDLDeclaration):
    designator              : None
    specification           : None
    expression              : str
    expression_with_agents  : str

@dataclass
class ConfigurationSpecification(VHDLDeclaration):
    component_specification : None
    binding_indication      : None

@dataclass
class DisconnectionSpecification(VHDLDeclaration):
    guarded_signal_specification    : None
    expression                      : str
    expression_with_agents          : str

@dataclass
class StepLimitSpecification(VHDLDeclaration):
    quantity_specification : None
    expression                      : str
    expression_with_agents          : str

@dataclass
class UseClause(VHDLDeclaration):
    selected_name : List[str]

@dataclass
class GroupTemplateDeclaration(VHDLDeclaration):
    identifier              : str
    entity_class_entry_list : None

@dataclass
class GroupDeclaration(VHDLDeclaration):
    name                    : str
    group_constituent_list  : None

@dataclass
class NatureDeclaration(VHDLDeclaration):
    identifier          : str
    nature_definition   : None

@dataclass
class SubnatureDeclaration(VHDLDeclaration):
    identifier              : str
    subnature_indication    : None

@dataclass
class QuantityDeclaration(VHDLDeclaration):
    free_quantity_declaration   : None
    branch_quantity_declaration : None
    source_quantity_declaration : None

@dataclass
class TerminalDeclaration (VHDLDeclaration):
    identifier_list         : List[str]
    subnature_indication    : None