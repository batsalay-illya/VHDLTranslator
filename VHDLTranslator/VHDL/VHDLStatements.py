from __future__ import annotations
from typing import List, Tuple
from dataclasses import dataclass

from VHDL.VHDLDeclaration import VHDLDeclaration

@dataclass
class VHDLStatement:
    statement_class     : VHDLStatement # Variable for class reference
    parent              : VHDLStatement

    statement_name      : str

    behaviour_name      : str
    full_behaviour_name : str

    agent_name          : str

    def __hash__(self):
        return hash((self.statement_name, self.behaviour_name, self.full_behaviour_name, self.agent_name))

    def __eq__(self, other):
        if not isinstance(other, VHDLStatement):
            return False
        return (
            self.statement_name == other.statement_name and
            self.behaviour_name == other.behaviour_name and
            self.full_behaviour_name == other.full_behaviour_name and
            self.agent_name == other.agent_name
        )

    @staticmethod
    def from_tuple(statement_class: VHDLStatement, parent: VHDLStatement, info: Tuple[str, str, str, str]):
        return VHDLStatement(statement_class, parent, *info)

    def get_root_statement(self) -> VHDLStatement:
        if self.parent.statement_class in (ProcessStatement, BlockStatement):
            return self.parent
        
        return self.parent.get_root_statement()


@dataclass
class Entity(VHDLStatement):
    generic : List[VHDLDeclaration.Generic]
    port    : List[VHDLDeclaration.Port]

    def __init__(self, statement_info: VHDLStatement, generic: List[VHDLDeclaration.Generic], port: List[VHDLDeclaration.Port]):
        super().__init__(**vars(statement_info))

        self.generic = generic
        self.port    = port
    

@dataclass    
class Architecture(VHDLStatement):
    declarations : List[VHDLDeclaration]
    statements   : List[VHDLStatement]

    def __init__(self, statement_info: VHDLStatement, declarations: List[VHDLDeclaration], statements: List[VHDLStatement]):
        super().__init__(**vars(statement_info))

        self.declarations = declarations
        self.statements   = statements

@dataclass
class BlockStatement(VHDLStatement):
    expression              : str
    expression_with_agents  : str
    block_header            : None
    declarations            : List[VHDLDeclaration]
    statements              : List[VHDLStatement]

    def __init__(self, statement_info: VHDLStatement, expression: str, expression_with_agents: str,
                block_header: None, declarations: List[VHDLDeclaration], statements: List[VHDLStatement]):

        super().__init__(**vars(statement_info))

        self.expression               = expression
        self.expression_with_agents   = expression_with_agents
        self.block_header             = block_header
        self.declarations             = declarations
        self.statements               = statements


@dataclass
class ProcessStatement(VHDLStatement):
    sensitivity_list                : List[str]
    sensitivity_list_with_agents    : List[str]
    declarations                    : List[VHDLDeclaration]
    statements                      : List[VHDLStatement]

    def __init__(self, statement_info: VHDLStatement, sensitivity_list: List[str], 
                sensitivity_list_with_agents: List[str], 
                declarations: List[VHDLDeclaration], statements: List[VHDLStatement]):

        super().__init__(**vars(statement_info))

        self.sensitivity_list                = sensitivity_list
        self.sensitivity_list_with_agents    = sensitivity_list_with_agents
        self.declarations                    = declarations
        self.statements                      = statements
   
@dataclass
class ConcurrentProcedureCallStatement(VHDLStatement):
    ...

@dataclass
class ConcurrentAssertionStatement(VHDLStatement):
    ...

@dataclass
class ComponentInstantiationStatement(VHDLStatement):
    ...

@dataclass
class GenerateStatement(VHDLStatement):
    ...

@dataclass
class ConcurrentBreakStatement(VHDLStatement):
    ...

@dataclass
class SimultaneousStatement(VHDLStatement):
    pass

@dataclass
class SimpleSimultaneousStatement(SimultaneousStatement):
    expression              : str
    expression_with_agents  : str
    tolerance_aspect        : None

    def __init__(self, statement_info: VHDLStatement, expression: str, expression_with_agents: str, tolerance_aspect: None):
        super().__init__(
            parent=statement_info.parent,
            statement_name=statement_info.statement_name,
            behaviour_name=statement_info.behaviour_name,
            full_behaviour_name=statement_info.full_behaviour_name,
            agent_name=statement_info.agent_name,
        )

        self.expression              = expression
        self.expression_with_agents  = expression_with_agents
        self.tolerance_aspect        = tolerance_aspect        


@dataclass
class SimultaneousIfStatement(SimultaneousStatement):
    condition                       : str
    condition_with_agents           : str
    statements                      : List[SimultaneousStatement]
    elsif_condition                 : str
    elsif_condition_with_agents     : str
    elsif_statements                : List[SimultaneousStatement]
    else_statements                 : List[SimultaneousStatement]

    def __init__(self, statement_info: VHDLStatement, condition: str, condition_with_agents: str, statements: List[SimultaneousStatement], elsif_condition: str, 
    elsif_condition_with_agents: str, elsif_statements: List[SimultaneousStatement], else_statements: List[SimultaneousStatement]):

        super().__init__(**vars(statement_info))

        self.condition                       = condition
        self.condition_with_agents           = condition_with_agents
        self.statements                      = statements
        self.elsif_condition                 = elsif_condition
        self.elsif_condition_with_agents     = elsif_condition_with_agents
        self.elsif_statements                = elsif_statements
        self.else_statements                 = else_statements

@dataclass
class SimultaneousCaseStatement(SimultaneousStatement):
    expression              : str
    expression_with_agents  : str

    def __init__(self, statement_info: VHDLStatement, expression: str, expression_with_agents: str):
        super().__init__(**vars(statement_info))

        self.expression              = expression              
        self.expression_with_agents  = expression_with_agents  

@dataclass
class SimultaneousAlternative():
    ...

@dataclass
class WaitStatement(VHDLStatement):
    sensitivity_list                : str
    sensitivity_list_with_agents    : str
    condition                       : str
    condition_with_agents           : str
    timeout                         : None

    

    def __init__(self, statement_info: VHDLStatement, sensitivity_list: str, sensitivity_list_with_agents: str, 
                 condition: str, condition_with_agents: str, timeout: None):

        super().__init__(**vars(statement_info))

        self.sensitivity_list               = sensitivity_list
        self.sensitivity_list_with_agents   = sensitivity_list_with_agents
        self.condition                      = condition
        self.condition_with_agents          = condition_with_agents
        self.timeout                        = timeout

@dataclass
class AssertionStatement(VHDLStatement):
    assertion : None

    def __init__(self, statement_info: VHDLStatement, assertion: None):
        super().__init__(**vars(statement_info))

        self.assertion = assertion

@dataclass
class ReportStatement(VHDLStatement):
    report_expression               : str
    report_expression_with_agents   : str
    severity_expression             : str
    severity_expression_with_agents : str    

    def __init__(self, statement_info: VHDLStatement, report_expression: str, report_expression_with_agents: str, 
                 severity_expression: str, severity_expression_with_agents: str):

        super().__init__(**vars(statement_info))

        self.report_expression               = report_expression
        self.report_expression_with_agents   = report_expression_with_agents
        self.severity_expression             = severity_expression
        self.severity_expression_with_agents = severity_expression_with_agents


@dataclass
class SignalAssignment(VHDLStatement):
    target                  : str
    target_with_agent       : str
    delay_mechanism         : str
    waveform                : str
    waveform_with_agents    : str
    
    def __init__(self, statement_info: VHDLStatement, target: str, target_with_agent: str, 
                 delay_mechanism: str, waveform: str, waveform_with_agents: str):

        super().__init__(**vars(statement_info))

        self.target                  = target
        self.target_with_agent       = target_with_agent
        self.delay_mechanism         = delay_mechanism
        self.waveform                = waveform
        self.waveform_with_agents    = waveform_with_agents

@dataclass
class ConditionalSignalAssignment(VHDLStatement):
    target                  : str
    target_with_agent       : str
    opts                    : str
    conditional_waveforms   : ConditionalWaveform

    def __init__(self, statement_info: VHDLStatement, target: str, target_with_agent: str, 
                 opts: str, conditional_waveforms: ConditionalWaveform):

        super().__init__(**vars(statement_info))

        self.target                  = target
        self.target_with_agent       = target_with_agent
        self.opts                    = opts
        self.conditional_waveforms   = conditional_waveforms

@dataclass
class SelectedSignalAssignment(VHDLStatement):
    target                  : str
    target_with_agent       : str
    delay_mechanism         : str
    expression              : str
    expression_with_agents  : str
    selected_waveforms      : List[SelectedWaveform]

    def __init__(self, statement_info: VHDLStatement, target: str, target_with_agent: str, delay_mechanism: str,
                expression : str, expression_with_agents: str, selected_waveforms: List[SelectedWaveform]):

        super().__init__(**vars(statement_info))

        self.target                  = target
        self.target_with_agent       = target_with_agent
        self.delay_mechanism         = delay_mechanism
        self.expression              = expression
        self.expression_with_agents  = expression_with_agents
        self.selected_waveforms      = selected_waveforms

@dataclass
class SelectedWaveform:
    waveform                : str 
    waveform_with_agetns    : str
    choice                  : str
    choice_with_agent       : str


@dataclass
class ConditionalWaveform:
    waveform                : str
    waveform_with_agents    : str
    condition               : str
    condition_with_agents   : str
    conditional_waveforms   : ConditionalWaveform

@dataclass
class VariableAssignment(VHDLStatement):
    target                  : str
    target_with_agent      : str
    expression              : str
    expression_with_agents  : str

    def __init__(self, statement_info: VHDLStatement, target: str, target_with_agent: str,
                expression  : str, expression_with_agents: str):

        super().__init__(**vars(statement_info))

        self.target                  = target
        self.target_with_agent      = target_with_agent
        self.expression              = expression
        self.expression_with_agents  = expression_with_agents

@dataclass
class IfStatement(VHDLStatement):
    condition                       : str
    condition_with_agents           : str
    statements                      : List[VHDLStatement]
    elsif_condition                 : str
    elsif_condition_with_agents     : str
    elsif_statements                : List[VHDLStatement]
    else_statements                 : List[VHDLStatement]

    def __init__(self, statement_info: VHDLStatement, condition: str, condition_with_agents: str, statements: List[VHDLStatement],
                elsif_condition: str, elsif_condition_with_agents: str, elsif_statements: List[VHDLStatement], else_statements: List[VHDLStatement]):
        
        super().__init__(**vars(statement_info))

        self.condition                       = condition
        self.condition_with_agents           = condition_with_agents
        self.statements                      = statements
        self.elsif_condition                 = elsif_condition
        self.elsif_condition_with_agents     = elsif_condition_with_agents
        self.elsif_statements                = elsif_statements
        self.else_statements                 = else_statements

@dataclass
class CaseStatement(VHDLStatement):
    expression              : str
    expression_with_agents  : str
    case_alternatives       : List[CaseAlternative]

    def __init__(self, statement_info: VHDLStatement, expression: str, expression_with_agents: str, case_alternatives: List[CaseAlternative]):
        super().__init__(**vars(statement_info))

        self.expression              = expression
        self.expression_with_agents  = expression_with_agents
        self.case_alternatives       = case_alternatives

@dataclass
class CaseAlternative(VHDLStatement):
    choices             : str
    choices_with_agents : str
    statements          : List[VHDLStatement]

    def __init__(self, statement_info: VHDLStatement, choices: str, choices_with_agents: str, statements: List[VHDLStatement]):
        super().__init__(**vars(statement_info))

        self.choices             = choices
        self.choices_with_agents = choices_with_agents
        self.statements          = statements

@dataclass
class LoopStatement(VHDLStatement):
    iteration_scheme    : IterationScheme
    statements          : List[VHDLStatement]

    def __init__(self, statement_info: VHDLStatement, iteration_scheme: IterationScheme, statements: List[VHDLStatement]):
        super().__init__(**vars(statement_info))

        iteration_scheme    = iteration_scheme
        statements          = statements

@dataclass
class IterationScheme():
    pass

@dataclass
class WhileScheme(IterationScheme):
    condition               : str
    condition_with_agents   : str

    def __init__(self, statement_info: VHDLStatement, condition: str, condition_with_agents: str):
        super().__init__(**vars(statement_info))

        condition               = condition               
        condition_with_agents   = condition_with_agents   

@dataclass
class ForScheme(IterationScheme):
    ...

@dataclass
class NextStatement(VHDLStatement):
    ...

@dataclass
class ExitStatement(VHDLStatement):
    ...

@dataclass
class ReturnStatement(VHDLStatement):
    ...

@dataclass
class BreakStatement(VHDLStatement):
    ...

@dataclass
class ProcedureCallStatement(VHDLStatement):
    ...
