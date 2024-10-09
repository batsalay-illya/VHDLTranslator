from __future__ import annotations
from typing import List
from dataclasses import dataclass

from VHDL.VHDLDeclaration import VHDLDeclaration

@dataclass
class VHDLStatement:
    statement_name : str
    agent_name : str

@dataclass
class BlockStatement(VHDLStatement):
    expression              : str
    expression_with_agents  : str
    block_header            : None
    declarations            : List[VHDLDeclaration]
    statements              : List[VHDLStatement]

@dataclass
class ProcessStatement(VHDLStatement):
    sensitivity_list                : List[str]
    sensitivity_list_with_agents    : List[str]
    declarations                    : List[VHDLDeclaration]
    statements                      : List[VHDLStatement]
   
@dataclass
class ConcurrentProcedureCallStatement(VHDLStatement):
    ...

@dataclass
class ConcurrentAssertionStatement(VHDLStatement):
    ...

@dataclass
class ConcurrentSignalAssignmentStatement(VHDLStatement):
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

@dataclass
class SimultaneousIfStatement(SimultaneousStatement):
    condition                       : str
    condition_with_agents           : str
    statements                      : List[SimultaneousStatement]
    elsif_condition                 : str
    elsif_condition_with_agents     : str
    elsif_statements                : List[SimultaneousStatement]
    else_statements                 : List[SimultaneousStatement]

@dataclass
class SimultaneousCaseStatement(SimultaneousStatement):
    expression              : str
    expression_with_agents  : str

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

@dataclass
class AssertionStatement(VHDLStatement):
    assertion : None

@dataclass
class ReportStatement(VHDLStatement):
    report_expression               : str
    report_expression_with_agents   : str
    severity_expression             : str
    severity_expression_with_agents : str

@dataclass
class SignalAssignment(VHDLStatement):
    target                  : str
    target_with_agent       : str
    delay_mechanism         : str
    waveform                : str
    waveform_with_agents    : str
    
@dataclass
class ConditionalSignalAssignment(VHDLStatement):
    target                  : str
    target_with_agent       : str
    opts                    : str
    conditional_waveforms   : ConditionalWaveform
    
@dataclass
class ConditionalWaveforms():
    waveform                : str
    waveform_with_agents    : str
    condition               : str
    condition_with_agents   : str
    conditional_waveforms   : ConditionalWaveforms

@dataclass
class SelectedSignalAssignment(VHDLStatement):
    target                  : str
    target_with_agent       : str
    delay_mechanism         : str
    expression              : str
    expression_with_agents  : str
    selected_waveforms      : List[SelectedWaveform]

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
    target_with_agents      : str
    expression              : str
    expression_with_agents  : str

@dataclass
class IfStatement(VHDLStatement):
    condition                       : str
    condition_with_agents           : str
    statements                      : List[VHDLStatement]
    elsif_condition                 : str
    elsif_condition_with_agents     : str
    elsif_statements                : List[VHDLStatement]
    else_statements                 : List[VHDLStatement]

@dataclass
class CaseStatement(VHDLStatement):
    expression              : str
    expression_with_agents  : str
    case_alternatives       : List[CaseAlternative]

@dataclass
class CaseAlternative():
    choice     : str
    statements : List[VHDLStatement]

@dataclass
class LoopStatement(VHDLStatement):
    iteration_scheme    : IterationScheme
    statements          : List[VHDLStatement]

@dataclass
class IterationScheme():
    pass

@dataclass
class WhileScheme(IterationScheme):
    condition               : str
    condition_with_agents   : str

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
