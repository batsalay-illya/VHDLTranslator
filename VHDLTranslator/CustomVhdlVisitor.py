import logging

from typing import Tuple
from Debug import Debug

from ANTLR.vhdlVisitor import vhdlVisitor
from ANTLR.vhdlParser import vhdlParser

from VHDL.VHDLData import *
from VHDL.VHDLStatements import *
from VHDL.VHDLDeclaration import *

import Constants as const

class CustomVhdlVisitor(vhdlVisitor):

    class StatementManager():
        def __init__(self, visitor):
            self.__visitor : CustomVhdlVisitor = visitor
            self.output_log = Debug.get_logger("Visitor")

            self.__statement_name_mapping = {
                ProcessStatement    : "process",
                
                IfStatement         : "if",
                CaseStatement       : "case",

                SignalAssignment    : "signal_assignment",
                VariableAssignment  : "variable_assignment"
            }

            self.__behaviour_name_mapping = {
                ProcessStatement    : "process",

                IfStatement         : "if",
                CaseStatement       : "case",
                CaseAlternative     : "when",
                
                SignalAssignment    : "asn",
                ConditionalSignalAssignment : "asn",
                VariableAssignment  : "vasn"
            }

            self.__agent_name_mapping = {
                Entity              : "module",
                Architecture        : "arc",

                ProcessStatement    : "p",
                BlockStatement      : "b"
            }
             
            self.__statement_index = {cls: 0 for cls in self.__statement_name_mapping}
            self.__behaviour_index = {cls: 0 for cls in self.__behaviour_name_mapping}
            self.__agent_index = {cls: 0 for cls in self.__agent_name_mapping}

        def __get_statement_name(self, cls, ctx):
            if hasattr(ctx, "label_colon"):
                if ctx.label_colon(): return self.__visitor.visit(ctx.label_colon())

            elif hasattr(ctx, "identifier"):
                if ctx.identifier(): return ctx.identifier(0).getText()

            if cls not in self.__statement_name_mapping:
                self.output_log.warning(f"Class not found {cls} in statement_name_mapping, return None...")
                return None

            self.__statement_index[cls] += 1
            name : str = self.__statement_name_mapping[cls]
            index : int = self.__statement_index[cls]
            return f"{name}_{index}"

        def __get_behaviour_name(self, cls):
            if cls in (Entity, Architecture):
                return None

            if cls not in self.__behaviour_name_mapping:
                self.output_log.warning(f"Class not found {cls} in behaviour_name_mapping, return None...")
                return None

            self.__behaviour_index[cls] += 1
            name : str = self.__behaviour_name_mapping[cls]
            index : int = self.__behaviour_index[cls]
            return f"{name}_{index}"

        def __get_full_behaviour_name(self, cls, parent: VHDLStatement):
            if cls in (Entity, Architecture):
                return None



            if cls in (ProcessStatement, BlockStatement, ConditionalSignalAssignment) or parent.statement_class is ProcessStatement:
                name : str = self.__behaviour_name_mapping[cls]
                index : int = self.__behaviour_index[cls]
                return f"{name}_{index}"

            if cls is CaseAlternative:
                name : str = self.__behaviour_name_mapping[cls]
                index : int = self.__behaviour_index[cls]
                if parent.parent.statement_class is ProcessStatement:
                    return f"{name}_{index}"

                return f"{parent.parent.behaviour_name}.{parent.parent.behaviour_name}_{name}_{index}.body"

            name : str = self.__behaviour_name_mapping[cls]
            index : int = self.__behaviour_index[cls]
            return f"{parent.behaviour_name}.{parent.behaviour_name}_{name}_{index}"

        def __get_agent_name(self, cls, parent: VHDLStatement):
            if (cls in (Entity, Architecture)):
                if self.__agent_index[cls] == 0:
                    self.__agent_index[cls] += 1
                    return self.__agent_name_mapping[cls]
            
            if cls in (ProcessStatement, BlockStatement):
                self.__agent_index[cls] += 1
                return f"{self.__agent_name_mapping[cls]}_{self.__agent_index[cls]}"

            return None

        def get_statement_general_info(self, cls, ctx, parent: VHDLStatement) -> Tuple[str, str, str, str]:
            if cls is None:
                self.__visitor.debug.write_error_to_log("Given unknown class as parameter in 'get_agent_name' function, return 'unknown'")
                return None, None, None, None

            if ctx is None:
                self.__visitor.debug.write_error_to_log("Given context is None")

            statement_name = self.__get_statement_name(cls, ctx)
            behaviour_name = self.__get_behaviour_name(cls)
            full_behaviour_name = self.__get_full_behaviour_name(cls, parent)
            agent_name     = self.__get_agent_name(cls, parent)

            return statement_name, behaviour_name, full_behaviour_name, agent_name

    class DeclarationManager():
        def __init__(self, visitor):
            self.__visitor : CustomVhdlVisitor = visitor
            self.output_log = Debug.get_logger("Visitor")

            self.__declaration_name_mapping = {
                ...
            }
             
        def __get_declaration_name(self, cls, ctx):
            ...

        def __get_declaration_type(self, cls, ctx):
            ...

        def __get_declaration_value(self, cls, ctx):
            ...

    def __init__(self):
        self.vhdlData           = self._initialize_vhdl_data()
        self.statement_manager  = self.StatementManager(self)
        self.output_log         = Debug.get_logger("Visitor")

    def visitDesign_file(self, ctx:vhdlParser.Design_fileContext):
        '''
        design_file
            : (design_unit)* EOF
            ;
        '''

        Debug.write_visit_to_log(self.output_log, "Design_file")

        design_list : List[VHDLDesign] = [
            self.visit(design)
            for design in ctx.design_unit()
        ]

        self.vhdlData.design_list = design_list

        self.output_log.debug(f"{len(design_list)} designs found")
    
    def visitDesign_unit(self, ctx:vhdlParser.Design_unitContext) -> VHDLDesign:
        '''
        design_unit
            : context_clause library_unit
            ;
        '''

        Debug.write_visit_to_log(self.output_log, "Design_unit")

        # context_clause

        # library_unit
        return self.visitLibrary_unit(ctx.library_unit())
    
    def visitLibrary_unit(self, ctx:vhdlParser.Library_unitContext) -> VHDLDesign: 
        '''
        library_unit
            : secondary_unit
            | primary_unit
            ;
        '''

        Debug.write_visit_to_log(self.output_log, "Library_unit")

        entity, configuration, package_declaration = self.visitPrimary_unit(ctx.primary_unit()) if ctx.primary_unit() else (None, None, None)
         
        architecture, package_body = self.visitSecondary_unit(ctx.secondary_unit()) if ctx.secondary_unit() else (None, None)

        return VHDLDesign(entity, configuration, package_declaration, architecture, package_body)

    def visitPrimary_unit(self, ctx:vhdlParser.Primary_unitContext):
        '''
        primary_unit
            : entity_declaration
            | configuration_declaration
            | package_declaration
            ;
        '''
        
        Debug.write_visit_to_log(self.output_log, "Primary_unit")

        entity = self.visit(ctx.entity_declaration()) if ctx.entity_declaration() else None

        configuration = self.visit(ctx.configuration_declaration()) if ctx.configuration_declaration() else None

        package_declaration = self.visit(ctx.package_declaration()) if ctx.package_declaration() else None

        return entity, configuration, package_declaration

    def visitSecondary_unit(self, ctx:vhdlParser.Secondary_unitContext):
        '''
        secondary_unit
            : architecture_body
            | package_body
            ;
        '''
        
        Debug.write_visit_to_log(self.output_log, "Secondary_unit")

        architecture = self.visit(ctx.architecture_body()) if ctx.architecture_body() else None
         
        package_body = self.visit(ctx.package_body()) if ctx.package_body() else None

        return architecture, package_body

    #Entity
    #region Entity

    def visitEntity_declaration(self, ctx : vhdlParser.Entity_declarationContext) -> Entity:
        '''
        entity_declaration
            : ENTITY identifier IS entity_header entity_declarative_part (BEGIN entity_statement_part)? END (
                ENTITY
            )? (identifier)? SEMI
            ;
        '''

        Debug.write_visit_to_log(self.output_log, "Entity_declaration")
        
        statement_info : VHDLStatement = VHDLStatement.from_tuple(Entity, None, self.statement_manager.get_statement_general_info(Entity, ctx, None))
        self.output_log.debug(f"entity - statement_name:{statement_info.statement_name}, behaviour_name:{statement_info.behaviour_name}, full_behaviour_name:{statement_info.full_behaviour_name}, agent_name:{statement_info.agent_name}")

        generic, port = self.visitEntity_header(ctx.entity_header(), statement_info.agent_name)

        entity = Entity(statement_info, generic, port)
        
        self.append_declarations(generic, entity)
        self.append_declarations(port, entity)
        self.append_agent(statement_info)

        return entity

    def visitEntity_header(self, ctx:vhdlParser.Entity_headerContext, agent_name: str) -> Tuple[List[Generic], List[Port]]:
        '''
        entity_header
            : (generic_clause)? (port_clause)?
            ;
        '''

        Debug.write_visit_to_log(self.output_log, "Entity_header")

        generic = self.visitGeneric_clause(ctx.generic_clause(), agent_name) if ctx.generic_clause() else []  
        port = self.visitPort_clause(ctx.port_clause(), agent_name) if ctx.port_clause() else []
        return generic, port
    
    # Generic
    def visitGeneric_clause(self, ctx:vhdlParser.Generic_clauseContext, agent_name: str = None):
        '''
        generic_clause
            : GENERIC LPAREN generic_list RPAREN SEMI
            ;
        '''

        Debug.write_visit_to_log(self.output_log, "Generic_clause")

        return self.visitGeneric_list(ctx.generic_list(), agent_name)

    def visitGeneric_list(self, ctx:vhdlParser.Generic_listContext, agent_name: str = None) -> List[Generic]:
        '''
        generic_list
            : interface_constant_declaration (SEMI interface_constant_declaration)*
            ;
        '''
        generic_list : List[Generic] = []
        
        for declaration in ctx.interface_constant_declaration():
            generic_list.extend(self.visitInterface_constant_declaration(declaration, agent_name))
        
        self.output_log.debug(f"{len(generic_list)} generic elements was found")
        return generic_list

    def visitInterface_constant_declaration(self, ctx:vhdlParser.Interface_constant_declarationContext, agent_name: str = None) -> List[Generic]:
        '''
        interface_constant_declaration
            : (CONSTANT)? identifier_list COLON (IN)? subtype_indication (VARASGN expression)?
            ;
        '''
        generic_list : List[Generic] = []

        identifier_list         : List[str] = self.visit(ctx.identifier_list())
        subtype_indication      : str = None
        subtype_indication_js   : str = None

        expression              : str = None
        expression_with_agents  : str = None

        subtype_indication, subtype_indication_js = self.visit(ctx.subtype_indication())
        expression, expression_with_agents = self.visit(ctx.expression()) if ctx.expression() else (None, None)

        generic_list : List[Generic] = [
            Generic(identifier, const.MODULE, subtype_indication, subtype_indication_js, expression, expression_with_agents)
            for identifier in identifier_list
        ]

        #self.vhdlData.declaration_list.extend(generic_list)
        #self.vhdlData.sorted_declaration_list_append(agent_name, [generic_list])

        return generic_list

    # Port
    def visitPort_clause(self, ctx:vhdlParser.Port_clauseContext, agent_name: str = None) -> List[Port]:
        '''
        port_clause
            : PORT LPAREN port_list RPAREN SEMI
            ;
        '''

        Debug.write_visit_to_log(self.output_log, "Port_clause")

        return self.visitPort_list(ctx.port_list(), agent_name)

    def visitPort_list(self, ctx:vhdlParser.Port_listContext, agent_name: str = None):
        '''
        port_list
            : interface_port_list
            ;
        '''

        return self.visitInterface_port_list(ctx.interface_port_list(), agent_name)

    def visitInterface_port_list(self, ctx:vhdlParser.Interface_port_listContext, agent_name: str = None) -> List[Port]:
        '''
        interface_port_list
            : interface_port_declaration (SEMI interface_port_declaration)*
            ;
        '''
        port_list : List[Port] = []
        
        for declaration in ctx.interface_port_declaration():
            port_list.extend(self.visitInterface_port_declaration(declaration, agent_name))
        
        self.output_log.debug(f"{len(port_list)} port elements was found")
        return port_list

    def visitInterface_port_declaration(self, ctx:vhdlParser.Interface_port_declarationContext, agent_name: str = None) -> List[Port]:
        '''
        interface_port_declaration
            : identifier_list COLON (signal_mode)? subtype_indication (BUS)? (VARASGN expression)?
            ;
        '''
        
        port_list               : List[Port] = []

        identifier_list         : List[str] = self.visit(ctx.identifier_list())
        signal_mode             : str = ctx.signal_mode().getText() if ctx.signal_mode() else None
        subtype_indication      : str = None
        subtype_indication_js   : str = None
        expression              : str = None
        expression_with_agents  : str = None

        subtype_indication, subtype_indication_js = self.visit(ctx.subtype_indication())

        if ctx.expression():
            expression, expression_with_agents = self.visit(ctx.expression())

        for identifier in identifier_list :
            port : Port = Port(identifier, "module", signal_mode, subtype_indication, subtype_indication_js, expression, expression_with_agents)

            port_list.append(port)

            #self.vhdlData.declaration_list.append(port)
            #self.vhdlData.sorted_declaration_list_append(agent_name, [port])

        return port_list

    #endregion

    #Architecture
    #region Architecture

    def visitArchitecture_body(self, ctx:vhdlParser.Architecture_bodyContext) -> Architecture:
        '''
        architecture_body
            : ARCHITECTURE identifier OF identifier IS architecture_declarative_part BEGIN architecture_statement_part END (
                ARCHITECTURE
            )? (identifier)? SEMI
            ;
        '''

        Debug.write_visit_to_log(self.output_log, "Architecture_body")

        statement_info : VHDLStatement = VHDLStatement.from_tuple(Architecture, None, self.statement_manager.get_statement_general_info(Architecture, ctx, None))
        self.output_log.debug(f"architecture - statement_name:{statement_info.statement_name}, behaviour_name:{statement_info.behaviour_name}, full_behaviour_name:{statement_info.full_behaviour_name}, agent_name:{statement_info.agent_name}")
        self.append_agent(statement_info)

        architecture_declarative_part : List[VHDLDeclaration] = []
        architecture_statement_part   : List[VHDLStatement] = []

        architecture_declarative_part = self.visitArchitecture_declarative_part(ctx.architecture_declarative_part(), statement_info)
        architecture_statement_part = self.visitArchitecture_statement_part(ctx.architecture_statement_part(), statement_info)

        architecture : Architecture = Architecture(statement_info, architecture_declarative_part, architecture_statement_part)

        return architecture

    def visitArchitecture_declarative_part(self, ctx:vhdlParser.Architecture_declarative_partContext, parent: VHDLStatement = None) -> List[VHDLDeclaration]:
        '''
        architecture_declarative_part
            : (block_declarative_item)*
            ;
        '''
        
        Debug.write_visit_to_log(self.output_log, "Architecture_declarative_part")

        declarations : List[VHDLDeclaration] = []

        for item in ctx.block_declarative_item():
            declarative_item = self.visitBlock_declarative_item(item, parent)

            if isinstance(declarative_item, List):
                for item in declarative_item:
                    declarations.append(item)
            else:
                declarations.append(declarative_item)

        #self.append_declarations(declarations, parent)
        return declarations

    def visitArchitecture_statement_part(self, ctx:vhdlParser.Architecture_statement_partContext, parent: VHDLStatement = None) -> List[VHDLDeclaration]:
        '''
        architecture_statement_part
            : (architecture_statement)*
            ;
        '''
        
        Debug.write_visit_to_log(self.output_log, "Architecture_statement_part")

        statement_list : List[VHDLStatement] = []
        
        for statement in ctx.architecture_statement():
            statement_list.append(self.visitArchitecture_statement(statement, parent))

        return statement_list
    

    def visitArchitecture_statement(self, ctx:vhdlParser.Architecture_statementContext, parent: VHDLStatement = None) -> VHDLStatement:
        '''
        architecture_statement
            : block_statement
            | process_statement
            | ( label_colon)? concurrent_procedure_call_statement
            | ( label_colon)? concurrent_assertion_statement
            | ( label_colon)? ( POSTPONED)? concurrent_signal_assignment_statement
            | component_instantiation_statement
            | generate_statement
            | concurrent_break_statement
            | simultaneous_statement
            ;
        '''

        if ctx.block_statement():
            return self.visitBlock_statement(ctx.block_statement(), parent)

        if ctx.process_statement():
            return self.visitProcess_statement(ctx.process_statement(), parent)

        if ctx.concurrent_procedure_call_statement():
            return self.visitConcurrent_procedure_call_statement(ctx.concurrent_procedure_call_statement(), parent)

        if ctx.concurrent_assertion_statement():
            return self.visitConcurrent_assertion_statement(ctx.concurrent_assertion_statement(), parent)

        if ctx.concurrent_signal_assignment_statement():
            return self.visitConcurrent_signal_assignment_statement(ctx.concurrent_signal_assignment_statement(), parent)

        if ctx.component_instantiation_statement():
            return self.visitComponent_instantiation_statement(ctx.component_instantiation_statement(), parent)

        if ctx.generate_statement():
            return self.visitGenerate_statement(ctx.generate_statement(), parent)

        if ctx.concurrent_break_statement():
            return self.visitConcurrent_break_statement(ctx.concurrent_break_statement(), parent)

        if ctx.simultaneous_statement():
            return self.visitSimultaneous_statement(ctx.simultaneous_statement(), parent)

    #endregion

    # Declarations
    #region Declarations
    '''
    : subprogram_declaration
            | subprogram_body
            | type_declaration
            | subtype_declaration
            | constant_declaration
            | signal_declaration
            | variable_declaration
            | file_declaration
            | alias_declaration
            | component_declaration
            | attribute_declaration
            | attribute_specification
            | configuration_specification
            | disconnection_specification
            | step_limit_specification
            | use_clause
            | group_template_declaration
            | group_declaration
            | nature_declaration
            | subnature_declaration
            | quantity_declaration
            | terminal_declaration 
    '''

    def visitSubtype_declaration(self, ctx:vhdlParser.Subtype_declarationContext, agent_name:str = None) -> SubtypeDeclaration:
        '''
        subtype_declaration
            : SUBTYPE identifier IS subtype_indication SEMI
            ;
        '''

        return self.visitChildren(ctx)

    def visitConstant_declaration(self, ctx:vhdlParser.Constant_declarationContext, agent_name:str = None) -> List[ConstantDeclaration]:
        '''
        constant_declaration
            : CONSTANT identifier_list COLON subtype_indication (VARASGN expression)? SEMI
            ;
        '''

        constant_list           : List[ConstantDeclaration] = []

        identifier_list         : List[str] = self.visit(ctx.identifier_list())
        subtype_indication      : str = None
        subtype_indication_js   : str = None

        expression              : str = None
        expression_with_agents  : str = None

        subtype_indication, subtype_indication_js = self.visit(ctx.subtype_indication())

        if ctx.expression():
            expression, expression_with_agents = self.visit(ctx.expression())

        for identifier in identifier_list:
            constant : ConstantDeclaration = ConstantDeclaration(identifier, agent_name, subtype_indication, subtype_indication_js, expression, expression_with_agents)

            constant_list.append(constant)

            self.vhdlData.declaration_list.append(constant)
            self.vhdlData.sorted_declaration_list_append(agent_name, [constant])

        return constant_list

    def visitSignal_declaration(self, ctx:vhdlParser.Signal_declarationContext, agent_name:str = None) -> List[SignalDeclaration]:
        '''
        signal_declaration
            : SIGNAL identifier_list COLON subtype_indication (signal_kind)? (VARASGN expression)? SEMI
            ;
        '''

        signal_list : List[SignalDeclaration] = []

        identifier_list : List[str] = self.visit(ctx.identifier_list())
        subtype_indication      : str = None
        subtype_indication_js   : str = None
        signal_kind             : str = None
        expression              : str = None
        expression_with_agents  : str = None

        subtype_indication, subtype_indication_js = self.visit(ctx.subtype_indication())

        if ctx.signal_kind():
            signal_kind = ctx.signal_kind().getText()

        if ctx.expression():
            expression, expression_with_agents = self.visit(ctx.expression())

        if len(identifier_list) > 1:
            for identifier in identifier_list:
                signal : SignalDeclaration = SignalDeclaration(identifier, agent_name, subtype_indication, subtype_indication_js, signal_kind, expression, expression_with_agents)

                signal_list.append(signal)

            return signal_list
        
        return SignalDeclaration(identifier_list[0], agent_name, subtype_indication, subtype_indication_js, signal_kind, expression, expression_with_agents)

    def visitVariable_declaration(self, ctx:vhdlParser.Variable_declarationContext, agent_name:str = None) -> List[VariableDeclaration]:
        '''
        variable_declaration
            : (SHARED)? VARIABLE identifier_list COLON subtype_indication (VARASGN expression)? SEMI
            ;
        '''

        variable_list           : List[VariableDeclaration] = []

        identifier_list         : List[str] = self.visit(ctx.identifier_list())
        subtype_indication      : str = None
        subtype_indication_js   : str = None
        expression              : str = None
        expression_with_agents  : str = None

        subtype_indication, subtype_indication_js = self.visit(ctx.subtype_indication())

        if ctx.expression():
            expression, expression_with_agents = self.visit(ctx.expression())

        for identifier in identifier_list:
            variable : VariableDeclaration = VariableDeclaration(identifier, agent_name, subtype_indication, subtype_indication_js, expression, expression_with_agents)

            variable_list.append(variable)

        return variable_list


    # Type declaration
    #region Type declaration
    def visitType_declaration(self, ctx:vhdlParser.Type_declarationContext, agent_name:str = None) -> TypeDeclaration:
        '''
        type_declaration
            : TYPE identifier (IS type_definition)? SEMI
            ;
        '''

        identifier      : str = ctx.identifier().getText()
        #type_definition : TypeDeclaration = None

        if ctx.type_definition():
            return self.visitType_definition(ctx.type_definition(), identifier, agent_name)

        #return TypeDeclaration(identifier, agent_name, type_definition)

    def visitType_definition(self, ctx:vhdlParser.Type_definitionContext, name: str = None, agent_name: str = None):
        '''
        type_definition
            : scalar_type_definition
            | composite_type_definition
            | access_type_definition
            | file_type_definition
            ;
        '''

        if ctx.scalar_type_definition():
            return self.visitScalar_type_definition(ctx.scalar_type_definition(), name, agent_name)

        if ctx.composite_type_definition():
            return self.visitComposite_type_definition(ctx.composite_type_definition(), name, agent_name)

        if ctx.access_type_definition():
            return self.visitAccess_type_definition(ctx.access_type_definition(), name, agent_name)

        if ctx.file_type_definition():
            return self.visitFile_type_definition(ctx.file_type_definition(), name, agent_name)

    def visitEnumeration_type_definition(self, ctx:vhdlParser.Enumeration_type_definitionContext, name: str = None, agent_name: str = None):
        '''
        enumeration_type_definition
            : LPAREN enumeration_literal (COMMA enumeration_literal)* RPAREN
            ;
        '''

        enumeration_literals : List[str] = []

        for index in range(len(ctx.enumeration_literal())):
            enumeration_literals.append(self.visit(ctx.enumeration_literal(index)))

        return EnumerationType(name, agent_name, enumeration_literals)
    #endregion

    # NOT IMPLEMENTED, WORK IN PROGRESS....
    #region NOT_IMPLEMENTED
    def visitFile_declaration(self, ctx:vhdlParser.File_declarationContext, agent_name:str = None) -> FileDeclaration:
        '''
        file_declaration
            : FILE identifier_list COLON subtype_indication (file_open_information)? SEMI
            ;
        '''

        return self.visitChildren(ctx)

    def visitAlias_declaration(self, ctx:vhdlParser.Alias_declarationContext, agent_name:str = None) -> AliasDeclaration:
        '''
        alias_declaration
            : ALIAS alias_designator (COLON alias_indication)? IS name (signature)? SEMI
            ;
        '''

        return self.visitChildren(ctx)

    def visitComponent_declaration(self, ctx:vhdlParser.Component_declarationContext, agent_name:str = None) -> ComponentDeclaration:
        '''
        component_declaration
            : COMPONENT identifier (IS)? (generic_clause)? (port_clause)? END COMPONENT (identifier)? SEMI
            ;
        '''

        return self.visitChildren(ctx)

    def visitAttribute_declaration(self, ctx:vhdlParser.Attribute_declarationContext, agent_name:str = None) -> AttributeDeclaration:
        '''
        attribute_declaration
            : ATTRIBUTE label_colon name SEMI
            ;
        '''

        return self.visitChildren(ctx)

    def visitAttribute_specification(self, ctx:vhdlParser.Attribute_specificationContext, agent_name:str = None) -> AttributeSpecification:
        '''
        attribute_specification
            : ATTRIBUTE attribute_designator OF entity_specification IS expression SEMI
            ;
        '''

        return self.visitChildren(ctx)

    def visitConfiguration_specification(self, ctx:vhdlParser.Configuration_specificationContext, agent_name:str = None) -> ConfigurationSpecification:
        '''
        configuration_specification
            : FOR component_specification binding_indication SEMI
            ;
        '''

        return self.visitChildren(ctx)

    def visitStep_limit_specification(self, ctx:vhdlParser.Step_limit_specificationContext, agent_name:str = None) -> StepLimitSpecification:
        '''
        step_limit_specification
            : LIMIT quantity_specification WITH expression SEMI
            ;
        '''

        return self.visitChildren(ctx)

    def visitUse_clause(self, ctx:vhdlParser.Use_clauseContext, agent_name:str = None) -> UseClause:
        '''
        use_clause
            : USE selected_name (COMMA selected_name)* SEMI
            ;
        '''
    
        return self.visitChildren(ctx)

    def visitGroup_template_declaration(self, ctx:vhdlParser.Group_template_declarationContext, agent_name:str = None) -> GroupTemplateDeclaration:
        '''
        group_template_declaration
            : GROUP identifier IS LPAREN entity_class_entry_list RPAREN SEMI
            ;
        '''

        return self.visitChildren(ctx)

    def visitGroup_declaration(self, ctx:vhdlParser.Group_declarationContext, agent_name:str = None) -> GroupDeclaration:
        '''
        group_declaration
            : GROUP label_colon name LPAREN group_constituent_list RPAREN SEMI
            ;
        '''

        return self.visitChildren(ctx)

    def visitNature_declaration(self, ctx:vhdlParser.Nature_declarationContext, agent_name:str = None) -> NatureDeclaration:
        '''
        nature_declaration
            : NATURE identifier IS nature_definition SEMI
            ;
        '''

        return self.visitChildren(ctx)

    def visitSubnature_declaration(self, ctx:vhdlParser.Subnature_declarationContext, agent_name:str = None) -> SubnatureDeclaration:
        '''
        subnature_declaration
            : SUBNATURE identifier IS subnature_indication SEMI
            ;
        '''

        return self.visitChildren(ctx)

    def visitQuantity_declaration(self, ctx:vhdlParser.Quantity_declarationContext, agent_name:str = None) -> QuantityDeclaration:
        '''
        quantity_declaration
            : free_quantity_declaration
            | branch_quantity_declaration
            | source_quantity_declaration
            ;
        '''

        return self.visitChildren(ctx)

    def visitTerminal_declaration(self, ctx:vhdlParser.Terminal_declarationContext, agent_name:str = None) -> TerminalDeclaration:
        '''
        terminal_declaration
            : TERMINAL identifier_list COLON subnature_indication SEMI
            ;
        '''

        return self.visitChildren(ctx)

    def visitElement_declaration(self, ctx:vhdlParser.Element_declarationContext):
        '''
        element_declaration
            : identifier_list COLON element_subtype_definition SEMI
            ;
        '''

        identifier_list : List[str] = self.visit(ctx.identifier_list())
        subtype : str = None
        subtype_js : str = None

        subtype, subtype_js = self.visit(ctx.element_subtype_definition())

        return ElementDeclaration(None, None, identifier_list, subtype, subtype_js)

    def visitRange_decl(self, ctx:vhdlParser.Range_declContext) -> Tuple[str, str]:
        '''
        range_decl
            : explicit_range
            | name
            ;
        '''

        if ctx.explicit_range():
            return self.visit(ctx.explicit_range())

        if ctx.name():
            name : str = ctx.name().getText()
            return name, f"{self.find_agent(name)}.{name}" if self.find_agent(name) is not None else name

    def visitRecord_type_definition(self, ctx:vhdlParser.Record_type_definitionContext) -> RecordType:
        '''
        record_type_definition
            : RECORD (element_declaration)+ END RECORD (identifier)?
            ;
        '''

        element_declarations : List[ElementDeclaration] = []

        for index in range(len(ctx.element_declaration())):
            element_declarations.append(self.visit(ctx.element_declaration(index)))

        return RecordType(element_declarations)

    def visitAccess_type_definition(self, ctx:vhdlParser.Access_type_definitionContext) -> AccessType:
        '''
        access_type_definition
            : ACCESS subtype_indication
            ;
        '''

        subtype : str = None
        subtype_js : str = None

        subtype, subtype_js = self.visit(ctx.subtype_indication())

        return AccessType(subtype, subtype_js)

    def visitFile_type_definition(self, ctx:vhdlParser.File_type_definitionContext) -> FileType:
        '''
        file_type_definition
            : FILE OF subtype_indication
            ;
        '''

        subtype : str = None
        subtype_js : str = None

        subtype, subtype_js = self.visit(ctx.subtype_indication())

        return FileType(subtype, subtype_js)

    
    def visitComposite_type_definition(self, ctx:vhdlParser.Composite_type_definitionContext):
        '''
        composite_type_definition
            : array_type_definition
            | record_type_definition
            ;
        '''

        if ctx.array_type_definition():
            return self.visit(ctx.array_type_definition())

        if ctx.record_type_definition():
            return self.visit(ctx.record_type_definition())

    def visitArray_type_definition(self, ctx:vhdlParser.Array_type_definitionContext):
        '''
        array_type_definition
            : unconstrained_array_definition
            | constrained_array_definition
            ;
        '''

        if ctx.unconstrained_array_definition():
            return self.visit(ctx.unconstrained_array_definition())

        if ctx.constrained_array_definition():
            return self.visit(ctx.constrained_array_definition())

    def visitUnconstrained_array_definition(self, ctx:vhdlParser.Unconstrained_array_definitionContext) -> UnconstrainedArray:
        '''
        unconstrained_array_definition
            : ARRAY LPAREN index_subtype_definition (COMMA index_subtype_definition)* RPAREN OF subtype_indication
            ;
        '''

        index_subtype_definition : List[str] = []
        subtype     : str = None
        subtype_js  : str = None

        for index in range(len(ctx.index_subtype_definition())):
            index_subtype_definition.append(self.visit(ctx.index_subtype_definition(index)))

        subtype, subtype_js = self.visit(ctx.subtype_indication())

        return UnconstrainedArray(index_subtype_definition, subtype, subtype_js)

    def visitIndex_subtype_definition(self, ctx:vhdlParser.Index_subtype_definitionContext) -> str:
        '''
        index_subtype_definition
            : name RANGE BOX
            ;
        '''
        return ctx.name().getText()

    def visitConstrained_array_definition(self, ctx:vhdlParser.Constrained_array_definitionContext) -> ConstrainedArray:
        '''
        constrained_array_definition
            : ARRAY index_constraint OF subtype_indication
            ;
        '''

        index_constraint : IndexConstraint = self.visit(ctx.index_constraint())

        subtype     : str = None
        subtype_js  : str = None

        subtype, subtype_js = self.visit(ctx.subtype_indication())

        return ConstrainedArray(index_constraint, subtype, subtype_js)
    
    

    def visitScalar_type_definition(self, ctx:vhdlParser.Scalar_type_definitionContext, name: str = None, agent_name: str = None):
        '''
            scalar_type_definition
                : physical_type_definition
                | enumeration_type_definition
                | range_constraint
                ;
            '''
        
        if ctx.physical_type_definition():
            return self.visitPhysical_type_definition(ctx.physical_type_definition(), name, agent_name)

        if ctx.enumeration_type_definition():
            return self.visitEnumeration_type_definition(ctx.enumeration_type_definition(), name, agent_name)

        if ctx.range_constraint():
            return self.visitRange_constraint(ctx.range_constraint(), name, agent_name)

    def visitPhysical_type_definition(self, ctx:vhdlParser.Physical_type_definitionContext, name: str = None, agent_name: str = None):
        '''
        physical_type_definition
            : range_constraint UNITS base_unit_declaration (secondary_unit_declaration)* END UNITS (
                identifier
            )?
            ;
        '''
        return self.visitChildren(ctx)

    def visitSubprogram_declaration(self, ctx:vhdlParser.Subprogram_declarationContext, agent_name:str = None):
        '''
        subprogram_declaration
            : subprogram_specification SEMI
            ;
        '''

        return self.visitChildren(ctx)

    def visitSubprogram_body(self, ctx:vhdlParser.Subprogram_bodyContext, agent_name:str = None) -> SubprogramBody:
        '''
        subprogram_body
            : subprogram_specification IS subprogram_declarative_part BEGIN subprogram_statement_part END (
                subprogram_kind
            )? (designator)? SEMI
            ;
        '''

        return self.visitChildren(ctx)

    #endregion

    #endregion

    #Statements
    #region Statements

    # Block
    #region Block statement

    def visitBlock_statement(self, ctx:vhdlParser.Block_statementContext, parent: VHDLStatement = None):
        '''
        block_statement
            : label_colon BLOCK (LPAREN expression RPAREN)? (IS)? block_header block_declarative_part BEGIN block_statement_part END BLOCK (
                identifier
            )? SEMI
            ;
        '''

        Debug.write_visit_to_log(self.output_log, "Block_statement")

        statement_info : VHDLStatement = VHDLStatement.from_tuple(BlockStatement, parent, self.statement_manager.get_statement_general_info(BlockStatement, ctx))

        expression              : str = None
        expression_with_agents  : str = None
        block_header            : None = self.visit(ctx.block_header())
        declarations            : List[VHDLDeclaration] = self.visitBlock_declarative_part(ctx.block_declarative_part(), parent)
        statements              : List[VHDLStatement] = self.visitBlock_statement_part(ctx.block_statement_part(), parent)

        if ctx.expression():
            expression, expression_with_agents = self.visit(ctx.expression())

        self.output_log.debug(f"block - statement_name:{statement_info.statement_name}, behaviour_name:{statement_info.behaviour_name}, full_behaviour_name:{statement_info.full_behaviour_name}, agent_name:{statement_info.agent_name}")
        
        return BlockStatement(statement_info, expression, expression_with_agents, block_header, declarations, statements)

    def visitBlock_declarative_part(self, ctx:vhdlParser.Block_declarative_partContext, parent: VHDLStatement = None):
        '''
        block_declarative_part
            : (block_declarative_item)*
            ;
        '''

        Debug.write_visit_to_log(self.output_log, "Block_declarative_part")

        declaration_list : List[VHDLDeclaration] = []

        for declaration in ctx.block_declarative_item():
            declaration_list.append(self.visitBlock_declarative_item(declaration, parent))

        self.output_log.debug(f"{len(ctx.block_declarative_item())} declarations found")

        return declaration_list
    
    def visitBlock_declarative_item(self, ctx:vhdlParser.Block_declarative_itemContext, parent: VHDLStatement) -> VHDLDeclaration:
        '''
        parent_declarative_item
            : subprogram_declaration
            | subprogram_body
            | type_declaration
            | subtype_declaration
            | constant_declaration
            | signal_declaration
            | variable_declaration
            | file_declaration
            | alias_declaration
            | component_declaration
            | attribute_declaration
            | attribute_specification
            | configuration_specification
            | disconnection_specification
            | step_limit_specification
            | use_clause
            | group_template_declaration
            | group_declaration
            | nature_declaration
            | subnature_declaration
            | quantity_declaration
            | terminal_declaration
            ;
        '''

        if ctx.subprogram_declaration():
            declaration = self.visitSubprogram_declaration(ctx.subprogram_declaration(), parent)

        if ctx.subprogram_body():
            declaration = self.visitSubprogram_body(ctx.subprogram_body(), parent)

        if ctx.type_declaration():
            declaration = self.visitType_declaration(ctx.type_declaration(), parent)

        if ctx.subtype_declaration():
            declaration = self.visitSubtype_declaration(ctx.subtype_declaration(), parent)

        if ctx.constant_declaration():
            declaration = self.visitConstant_declaration(ctx.constant_declaration(), parent)

        if ctx.signal_declaration():
            declaration = self.visitSignal_declaration(ctx.signal_declaration(), parent)

        if ctx.variable_declaration():
            declaration = self.visitVariable_declaration(ctx.variable_declaration(), parent)

        if ctx.file_declaration():
            declaration = self.visitFile_declaration(ctx.file_declaration(), parent)

        if ctx.alias_declaration():
            declaration = self.visitAlias_declaration(ctx.alias_declaration(), parent)

        if ctx.component_declaration():
            declaration = self.visitComponent_declaration(ctx.component_declaration(), parent)

        if ctx.attribute_declaration():
            declaration = self.visitAttribute_declaration(ctx.attribute_declaration(), parent)

        if ctx.attribute_specification():
            declaration = self.visitAttribute_specification(ctx.attribute_specification(), parent)

        if ctx.configuration_specification():
            declaration = self.visitConfiguration_specification(ctx.configuration_specification(), parent)

        if ctx.disconnection_specification():
            declaration = self.visitDisconnection_specification(ctx.disconnection_specification(), parent)

        if ctx.step_limit_specification():
            declaration = self.visitStep_limit_specification(ctx.step_limit_specification(), parent)

        if ctx.use_clause():
            declaration = self.visitUse_clause(ctx.use_clause(), parent)

        if ctx.group_template_declaration():
            declaration = self.visitGroup_template_declaration(ctx.group_template_declaration(), parent)

        if ctx.group_declaration():
            declaration = self.visitGroup_declaration(ctx.group_declaration(), parent)

        if ctx.nature_declaration():
            declaration = self.visitNature_declaration(ctx.nature_declaration(), parent)

        if ctx.subnature_declaration():
            declaration = self.visitSubnature_declaration(ctx.subnature_declaration(), parent)

        if ctx.quantity_declaration():
            declaration = self.visitQuantity_declaration(ctx.quantity_declaration(), parent)

        if ctx.terminal_declaration():
            declaration = self.visitTerminal_declaration(ctx.terminal_declaration(), parent)

        if isinstance(declaration, list):
            self.append_declarations(declaration, parent)
        else:
            self.append_declarations([declaration], parent)

        return declaration

    def visitBlock_statement_part(self, ctx:vhdlParser.Block_statement_partContext, parent: VHDLStatement = None):

        '''
        block_statement_part
            : (architecture_statement)*
            ;
        '''
        Debug.write_visit_to_log(self.output_log, "Block_statement_part")

        self.output_log.debug(f"{len(ctx.architecture_statement())} statements found")

        return self.visitChildren(ctx)

    #endregion

    # Process
    #region Process statement

    def visitProcess_statement(self, ctx:vhdlParser.Process_statementContext, parent: VHDLStatement = None):
        '''
        process_statement
            : (label_colon)? (POSTPONED)? PROCESS (LPAREN sensitivity_list RPAREN)? (IS)? process_declarative_part BEGIN process_statement_part END (
                POSTPONED
            )? PROCESS (identifier)? SEMI
            ;
        '''
        
        Debug.write_visit_to_log(self.output_log, "Process_statement")

        statement_info : VHDLStatement = VHDLStatement.from_tuple(ProcessStatement, parent, self.statement_manager.get_statement_general_info(ProcessStatement, ctx, parent))
        self.output_log.debug(f"process - parent: {parent.statement_class}, statement_name:{statement_info.statement_name}, behaviour_name:{statement_info.behaviour_name}, full_behaviour_name:{statement_info.full_behaviour_name}, agent_name:{statement_info.agent_name}")

        sensitivity_list                : List[str] = None
        sensitivity_list_with_agents    : List[str] = None

        declarations    : List[VHDLDeclaration] = self.visitProcess_declarative_part(ctx.process_declarative_part(), statement_info)
        statements      : List[VHDLStatement] = self.visitProcess_statement_part(ctx.process_statement_part(), statement_info)
        
        if ctx.sensitivity_list():
            sensitivity_list, sensitivity_list_with_agents = self.visit(ctx.sensitivity_list())
        
        process : ProcessStatement = ProcessStatement(statement_info, sensitivity_list, sensitivity_list_with_agents, declarations, statements)

        self.append_agent(statement_info)

        return process

    def visitSensitivity_list(self, ctx:vhdlParser.Sensitivity_listContext):
        '''
        sensitivity_list
            : name (COMMA name)*
            ;
        '''

        Debug.write_visit_to_log(self.output_log, "Sensitivity_list")

        sensitive_list              : List[str] = []
        sensitive_list_with_agents  : List[str] = []

        temp                        : str = None
        agent                       : str = None

        for index in range(len(ctx.name())):
            temp = ctx.name(index).getText()
            agent = self.find_agent(temp)

            sensitive_list.append(temp)
            sensitive_list_with_agents.append(f"{agent}.{temp}" if agent is not None else f"{temp}")

        self.output_log.debug(f"{len(ctx.name())} sensitivities found")

        return sensitive_list, sensitive_list_with_agents


    def visitProcess_declarative_part(self, ctx:vhdlParser.Process_declarative_partContext, parent: VHDLStatement = None):
        '''
        process_declarative_part
            : (process_declarative_item)*
            ;
        '''

        self.output_log.info("Process_declarative_part")

        declarations : List[VHDLDeclaration] = []

        for index in range(len(ctx.process_declarative_item())):
            declarative_item = self.visitProcess_declarative_item(ctx.process_declarative_item(index), parent)

            declarations.extend(declarative_item)
            #if isinstance(declarative_item, List):
            #    for item in declarative_item:
            #        declarations.append(item)
            #else:
            #    declarations.append(declarative_item)
        
        self.output_log.debug(f"{len(ctx.process_declarative_item())} declarations found")

        self.append_declarations(declarations, parent)

        return declarations
    
    def visitProcess_declarative_item(self, ctx:vhdlParser.Process_declarative_itemContext, process: VHDLStatement = None):
        '''
        process_declarative_item
            : subprogram_declaration
            | subprogram_body
            | type_declaration
            | subtype_declaration
            | constant_declaration
            | variable_declaration
            | file_declaration
            | alias_declaration
            | attribute_declaration
            | attribute_specification
            | use_clause
            | group_template_declaration
            | group_declaration
            ;
        '''
        
        if ctx.subprogram_declaration():
            declaration = self.visitSubprogram_declaration(ctx.subprogram_declaration(), process.agent_name)

        if ctx.subprogram_body():
            declaration = self.visitSubprogram_body(ctx.subprogram_body(), process.agent_name)

        if ctx.type_declaration():
            declaration = self.visitType_declaration(ctx.type_declaration(), process.agent_name)

        if ctx.subtype_declaration():
            declaration = self.visitSubtype_declaration(ctx.subtype_declaration(), process.agent_name)

        if ctx.constant_declaration():
            declaration = self.visitConstant_declaration(ctx.constant_declaration(), process.agent_name)

        if ctx.variable_declaration():
            declaration = self.visitVariable_declaration(ctx.variable_declaration(), process.agent_name)

        if ctx.file_declaration():
            declaration = self.visitFile_declaration(ctx.file_declaration(), process.agent_name)

        if ctx.alias_declaration():
            declaration = self.visitAlias_declaration(ctx.alias_declaration(), process.agent_name)

        if ctx.attribute_declaration():
            declaration = self.visitAttribute_declaration(ctx.attribute_declaration(), process.agent_name)

        if ctx.attribute_specification():
            declaration = self.visitAttribute_specification(ctx.attribute_specification(), process.agent_name)

        if ctx.use_clause():
            declaration = self.visitUse_clause(ctx.use_clause(), process.agent_name)

        if ctx.group_template_declaration():
            declaration = self.visitGroup_template_declaration(ctx.group_template_declaration(), process.agent_name)

        if ctx.group_declaration():
            declaration = self.visitGroup_declaration(ctx.group_declaration(), process.agent_name)

        return declaration

    def visitProcess_statement_part(self, ctx:vhdlParser.Process_statement_partContext, process: VHDLStatement = None):
        '''
        process_statement_part
            : (sequential_statement)*
            ;
        '''

        Debug.write_visit_to_log(self.output_log, "Process_statement_part")
        
        sequential_statements : List[VHDLStatement] = []

        for statement in ctx.sequential_statement():
            sequential_statements.append(self.visitSequential_statement(statement, process))

        self.output_log.debug(f"{len(ctx.sequential_statement())} statements found")

        return sequential_statements
    
    def visitSequential_statement(self, ctx:vhdlParser.Sequential_statementContext, process: VHDLStatement = None):
        '''
        sequential_statement
            : wait_statement
            | assertion_statement
            | report_statement
            | signal_assignment_statement
            | variable_assignment_statement
            | if_statement
            | case_statement
            | loop_statement
            | next_statement
            | exit_statement
            | return_statement
            | ( label_colon)? NULL_ SEMI
            | break_statement
            | procedure_call_statement
            ;
        '''
        
        if ctx.wait_statement():
            return self.visitWait_statement(ctx.wait_statement(), process)

        if ctx.assertion_statement():
            return self.visitAssertion_statement(ctx.assertion_statement(), process)

        if ctx.report_statement():
            return self.visitReport_statement(ctx.report_statement(), process)

        if ctx.signal_assignment_statement():
            return self.visitSignal_assignment_statement(ctx.signal_assignment_statement(), process)

        if ctx.variable_assignment_statement():
            return self.visitVariable_assignment_statement(ctx.variable_assignment_statement(), process)

        if ctx.if_statement():
            return self.visitIf_statement(ctx.if_statement(), process)

        if ctx.case_statement():
            return self.visitCase_statement(ctx.case_statement(), process)

        if ctx.loop_statement():
            return self.visitLoop_statement(ctx.loop_statement(), process)

        if ctx.next_statement():
            return self.visitNext_statement(ctx.next_statement(), process)

        if ctx.exit_statement():
            return self.visitExit_statement(ctx.exit_statement(), process)

        if ctx.return_statement():
            return self.visitReturn_statement(ctx.return_statement(), process)

        if ctx.break_statement():
            return self.visitBreak_statement(ctx.break_statement(), process)

        if ctx.procedure_call_statement():
            return self.visitProcedure_call_statement(ctx.procedure_call_statement(), process)    
    #endregion

    # Assignment
    #region Assignment statements
    def visitSignal_assignment_statement(self, ctx:vhdlParser.Signal_assignment_statementContext, parent: VHDLStatement = None):
        '''
        signal_assignment_statement
            : (label_colon)? target LE (delay_mechanism)? waveform SEMI
            ;
        '''

        Debug.write_visit_to_log(self.output_log, "Signal_assignment_statement")

        statement_info : VHDLStatement = VHDLStatement.from_tuple(SignalAssignment, parent, self.statement_manager.get_statement_general_info(SignalAssignment, ctx, parent))
        self.output_log.debug(f"signal_assignment - parent: {parent.statement_class}, statement_name:{statement_info.statement_name}, behaviour_name:{statement_info.behaviour_name}, full_behaviour_name:{statement_info.full_behaviour_name}, agent_name:{statement_info.agent_name}")

        target : str = ctx.target().getText()
        target_with_agent : str = f"{self.find_agent(target)}.{target}" if self.find_agent(target) is not None else target

        delay_mechanism : str = None

        waveform : str = None
        waveform_with_agents : str = None

        waveform, waveform_with_agents = self.visit(ctx.waveform())

        if ctx.delay_mechanism():
            delay_mechanism = ctx.target().getText()
        
        
        return SignalAssignment(statement_info, target, target_with_agent, delay_mechanism, waveform, waveform_with_agents)

    def visitVariable_assignment_statement(self, ctx:vhdlParser.Variable_assignment_statementContext, parent: VHDLStatement = None):
        '''
        variable_assignment_statement
            : (label_colon)? target VARASGN expression SEMI
            ;
        '''

        self.output_log.info("Variable_assignment_statement")

        statement_info : VHDLStatement = VHDLStatement.from_tuple(VariableAssignment, parent, self.statement_manager.get_statement_general_info(VariableAssignment, ctx, parent))
        self.output_log.debug(f"variable_assignment - parent: {parent.statement_class}, statement_name:{statement_info.statement_name}, behaviour_name:{statement_info.behaviour_name}, full_behaviour_name:{statement_info.full_behaviour_name}, agent_name:{statement_info.agent_name}")
        
        target                  : str = None
        target_with_agents      : str = None

        target, target_with_agents = self.visit(ctx.target())

        expression              : str = None
        expression_with_agents  : str = None

        expression, expression_with_agents = self.visit(ctx.expression())

        return VariableAssignment(statement_info, target, target_with_agents, expression, expression_with_agents)
    

    def visitConcurrent_signal_assignment_statement(self, ctx:vhdlParser.Concurrent_signal_assignment_statementContext, parent: VHDLStatement = None):
        '''
        concurrent_signal_assignment_statement
            : (label_colon)? (POSTPONED)? (conditional_signal_assignment | selected_signal_assignment)
            ;
        '''
        
        if ctx.conditional_signal_assignment():
            return self.visitConditional_signal_assignment(ctx.conditional_signal_assignment(), parent)

        if ctx.selected_signal_assignment():
            return self.visitSelected_signal_assignment(ctx.selected_signal_assignment(), parent)
    
    def visitConditional_signal_assignment(self, ctx:vhdlParser.Conditional_signal_assignmentContext, parent: VHDLStatement = None) -> ConditionalSignalAssignment:
        '''
        conditional_signal_assignment
            : target LE opts conditional_waveforms SEMI
            ;
        '''

        Debug.write_visit_to_log(self.output_log, "Conditional_signal_assignment")

        statement_info : VHDLStatement = VHDLStatement.from_tuple(ConditionalWaveform, parent, self.statement_manager.get_statement_general_info(ConditionalSignalAssignment, ctx, parent))
        self.output_log.debug(f"conditional_assignment - statement_name:{statement_info.statement_name}, behaviour_name:{statement_info.behaviour_name}, full_behaviour_name:{statement_info.full_behaviour_name}, agent_name:{statement_info.agent_name}")
        
        target : str = None
        target_with_agent : str = None

        target, target_with_agent = self.visit(ctx.target())

        opts : str = ctx.opts().getText()
        conditional_waveforms : ConditionalWaveform = self.visit(ctx.conditional_waveforms())

        
        return ConditionalSignalAssignment(statement_info, target, target_with_agent, opts, conditional_waveforms)

    
    def visitConditional_waveforms(self, ctx:vhdlParser.Conditional_waveformsContext) -> ConditionalWaveform:
        '''
        conditional_waveforms
            : waveform (WHEN condition (ELSE conditional_waveforms)?)?
            ;
        '''
        
        waveform                : str = None
        waveform_with_agents    : str = None

        waveform, waveform_with_agents = self.visit(ctx.waveform())

        condition               : str = None
        condition_with_agents   : str = None

        conditional_waveforms   : ConditionalWaveform = None

        if ctx.WHEN():
            condition, condition_with_agents = self.visit(ctx.condition())
            
        if ctx.ELSE():
            conditional_waveforms = self.visit(ctx.conditional_waveforms())
        
        return ConditionalWaveform(waveform, waveform_with_agents, condition, condition_with_agents, conditional_waveforms)
    

    def visitSelected_signal_assignment(self, ctx:vhdlParser.Selected_signal_assignmentContext, parent: VHDLStatement = None):
        '''
        selected_signal_assignment
            : WITH expression SELECT target LE opts selected_waveforms SEMI
            ;
        '''
        
        Debug.write_visit_to_log(self.output_log, "Selected_signal_assignment")

        statement_info : VHDLStatement = VHDLStatement.from_tuple(SelectedSignalAssignment, parent, self.statement_manager.get_statement_general_info(SelectedSignalAssignment, ctx, parent))

        expression              : str = None
        expression_with_agents  : str = None

        target : str = None
        target_with_agent : str = None

        opts : str = None

        selected_waveforms : SelectedWaveform = None
        
        expression, expression_with_agents = self.visit(ctx.expression())
        
        target, target_with_agent = self.visit(ctx.target())
        opts = ctx.opts().getText()
        
        selected_waveforms = self.visit(ctx.selected_waveforms())
    
        self.output_log.debug(f"selected_assignment - statement_name:{statement_info.statement_name}, behaviour_name:{statement_info.behaviour_name}, full_behaviour_name:{statement_info.full_behaviour_name}, agent_name:{statement_info.agent_name}")
        
        return SelectedSignalAssignment(statement_info, target, target_with_agent, opts, expression, expression_with_agents, selected_waveforms)

    def visitSelected_waveforms(self, ctx:vhdlParser.Selected_waveformsContext):
        '''
        selected_waveforms
            : waveform WHEN choices (COMMA waveform WHEN choices)*
            ;
        '''
        
        waveform                : str = None
        waveform_with_agents    : str = None

        choice                  : str = None
        choice_with_agent       : str = None

        selected_waveforms : List[SelectedWaveform] = []

        for index in range(len(ctx.waveform())):
            waveform, waveform_with_agents = self.visit(ctx.waveform(index))
            choice, choice_with_agent = self.visit(ctx.choices(index))

            selected_waveforms.append(SelectedWaveform(waveform, waveform_with_agents, choice, choice_with_agent))

        return selected_waveforms

    #endregion

    def visitIf_statement(self, ctx:vhdlParser.If_statementContext, parent: VHDLStatement = None):
        '''
        if_statement
            : (label_colon)? IF condition THEN sequence_of_statements (
                ELSIF condition THEN sequence_of_statements
            )* (ELSE sequence_of_statements)? END IF (identifier)? SEMI
            ;
        '''

        self.output_log.info("visit 'If_statement'")
        
        statement_info : VHDLStatement = VHDLStatement.from_tuple(IfStatement, parent, self.statement_manager.get_statement_general_info(IfStatement, ctx, parent))
        self.output_log.debug(f"if - parent: {parent.statement_class}, statement_name:{statement_info.statement_name}, behaviour_name:{statement_info.behaviour_name}, full_behaviour_name:{statement_info.full_behaviour_name}, agent_name:{statement_info.agent_name}")
        
        condition                   : str = None
        condition_with_agents       : str = None

        temp                        : str = None
        temp_with_agents            : str = None

        statements                  : List[VHDLStatement] = []

        elsif_condition             : str = None
        elsif_condition_with_agents : str = None

        elsif_statements            : List[VHDLStatement] = []
        else_statements             : List[VHDLStatement] = []
        
        temp, temp_with_agents = self.visit(ctx.condition(0))

        condition = temp
        condition_with_agents = temp_with_agents

        statements = self.visitSequence_of_statements(ctx.sequence_of_statements(0), statement_info)
        
        i : int = 1
        for _ in range(len(ctx.ELSIF())):
            temp, temp_with_agents = self.visit(ctx.condition(i))

            elsif_condition = temp
            elsif_condition_with_agents = temp_with_agents

            elsif_statements = self.visitSequence_of_statements(ctx.sequence_of_statements(i), statement_info)
            i+=1
            
        if ctx.ELSE():
            else_statements = self.visitSequence_of_statements(ctx.sequence_of_statements(i), statement_info)

        return IfStatement(statement_info, condition, condition_with_agents, statements, elsif_condition, elsif_condition_with_agents, elsif_statements, else_statements)

    # Case
    #region Case statement
    def visitCase_statement(self, ctx:vhdlParser.Case_statementContext, parent: VHDLStatement = None):
        '''
        case_statement
            : (label_colon)? CASE expression IS (case_statement_alternative)+ END CASE (identifier)? SEMI
            ;
        '''

        Debug.write_visit_to_log(self.output_log, "Case_statement")

        statement_info : VHDLStatement = VHDLStatement.from_tuple(CaseStatement, parent, self.statement_manager.get_statement_general_info(CaseStatement, ctx, parent))
        self.output_log.debug(f"case - statement_name:{statement_info.statement_name}, behaviour_name:{statement_info.behaviour_name}, full_behaviour_name:{statement_info.full_behaviour_name}, agent_name:{statement_info.agent_name}")

        expression : str = None
        expression_with_agents : str = None

        expression, expression_with_agents = self.visit(ctx.expression())

        case_alternatives : List[CaseAlternative] = []

        for case in ctx.case_statement_alternative():
            case_alternatives.append(self.visitCase_statement_alternative(case, statement_info, expression_with_agents))

        return CaseStatement(statement_info, expression, expression_with_agents, case_alternatives)
    
    def visitCase_statement_alternative(self, ctx:vhdlParser.Case_statement_alternativeContext, parent: VHDLStatement = None, case_expression: str = None) -> CaseAlternative:
        '''
        case_statement_alternative
            : WHEN choices ARROW sequence_of_statements
            ;
        '''

        Debug.write_visit_to_log(self.output_log, "Case_statement_alternative")
        statement_info : VHDLStatement = VHDLStatement.from_tuple(CaseAlternative, parent, self.statement_manager.get_statement_general_info(CaseAlternative, ctx, parent))

        choices : str = None
        choices_with_agents : str = None

        choices, choices_with_agents = self.visit(ctx.choices())

        choices_with_agents = f"{case_expression} == {choices_with_agents}"

        statements : List[VHDLStatement] = self.visitSequence_of_statements(ctx.sequence_of_statements(), statement_info)

        self.output_log.debug(f"case_alternative - choices:{len(choices)}, sequence_of_statements:{len(statements)}")
        
        return CaseAlternative(statement_info, choices, choices_with_agents, statements)
    #endregion

    
    #endregion    

    # NOT IMPLEMENTED, WORK IN PROGRESS....
    #region NOT_IMPLEMENTED

    def visitNext_statement(self, ctx:vhdlParser.Next_statementContext, parent: VHDLStatement = None):
        '''
        next_statement
            : (label_colon)? NEXT (identifier)? (WHEN condition)? SEMI
            ;
        '''
        
        return self.visitChildren(ctx)
    
    def visitExit_statement(self, ctx:vhdlParser.Exit_statementContext):
        '''
        exit_statement
            : (label_colon)? EXIT (identifier)? (WHEN condition)? SEMI
            ;
        '''

        return self.visitChildren(ctx)
    
    def visitReturn_statement(self, ctx:vhdlParser.Return_statementContext, parent: VHDLStatement = None):
        '''
        return_statement
            : (label_colon)? RETURN (expression)? SEMI
            ;
        '''
        
        return self.visitChildren(ctx)
    
    def visitBreak_statement(self, ctx:vhdlParser.Break_statementContext, parent: VHDLStatement = None):
        '''
        break_statement
            : (label_colon)? BREAK (break_list)? (WHEN condition)? SEMI
            ;
        '''
        
        return self.visitChildren(ctx)


    
    def visitWait_statement(self, ctx:vhdlParser.Wait_statementContext, parent: VHDLStatement = None):
        return self.visitChildren(ctx) # SKIP VISIT

        '''
        wait_statement
            : (label_colon)? WAIT (sensitivity_clause)? (condition_clause)? (timeout_clause)? SEMI
            ;
        '''
        self.output_log.info("visit 'Wait_statement'")
        
        statement_info : VHDLStatement = VHDLStatement.from_tuple(parent, self.statement_manager.get_statement_general_info(WaitStatement, ctx, parent))

        sensitivity_clause              : List[str] = []
        sensitivity_clause_with_agents  : List[str] = []
        condition_clause                : None = None
        timeout_clause                  : None = None

        if ctx.sensitivity_clause():
            sensitivity_clause, sensitivity_clause_with_agents = self.visit(ctx.sensitivity_clause())

        if ctx.timeout_clause():
            timeout_clause = self.visit(ctx.timeout_clause())

        self.output_log.info(f"wait - statement_name:{statement_info.statement_name}, behaviour_name:{statement_info.behaviour_name}, full_behaviour_name:{statement_info.full_behaviour_name}, agent_name:{statement_info.agent_name}")
        return WaitStatement(statement_info, sensitivity_clause, condition_clause, timeout_clause)
        
        
    def visitReport_statement(self, ctx:vhdlParser.Report_statementContext, parent: VHDLStatement = None):
        return self.visitChildren(ctx) # SKIP VISIT

        '''
        report_statement
            : (label_colon)? REPORT expression (SEVERITY expression)? SEMI
            ;
        '''
        self.output_log.info("visit 'Report_statement'")
        
        statement_info : VHDLStatement = VHDLStatement.from_tuple(parent, self.statement_manager.get_statement_general_info(ReportStatement, ctx, parent))

        report_expression               : str = None
        report_expression_with_agents   : str = None
        severity_expression             : str = None
        severity_expression_with_agents : str = None

        report_expression, report_expression_with_agents = self.visit(ctx.expression(0))

        if ctx.expression(1):
            severity_expression, severity_expression_with_agents = self.visit(ctx.expression(1))

        self.output_log.info(f"report - statement_name:{statement_info.statement_name}, behaviour_name:{statement_info.behaviour_name}, full_behaviour_name:{statement_info.full_behaviour_name}, agent_name:{statement_info.agent_name}")
        return ReportStatement(statement_info, report_expression, report_expression_with_agents, severity_expression, severity_expression_with_agents)

    def visitComponent_instantiation_statement(self, ctx:vhdlParser.Component_instantiation_statementContext):
        '''
        component_instantiation_statement
            : label_colon instantiated_unit (generic_map_aspect)? (port_map_aspect)? SEMI
            ;
        '''
        
        return self.visitChildren(ctx)
    
    def visitGenerate_statement(self, ctx:vhdlParser.Generate_statementContext):
        '''
        generate_statement
            : label_colon generation_scheme GENERATE (( block_declarative_item)* BEGIN)? (
                architecture_statement
            )* END GENERATE (identifier)? SEMI
            ;
        '''
        
        return self.visitChildren(ctx)
    
    def visitConcurrent_break_statement(self, ctx:vhdlParser.Concurrent_break_statementContext):
        '''
        concurrent_break_statement
            : (label_colon)? BREAK (break_list)? (sensitivity_clause)? (WHEN condition)? SEMI
            ;
        '''
        
        return self.visitChildren(ctx)

    
    def visitLoop_statement(self, ctx:vhdlParser.Loop_statementContext, parent: VHDLStatement = None):
        '''
        loop_statement
            : (label_colon)? (iteration_scheme)? LOOP sequence_of_statements END LOOP (identifier)? SEMI
            ;
        '''

        statement_info : VHDLStatement = VHDLStatement.from_tuple(parent, self.statement_manager.get_statement_general_info(LoopStatement, ctx, parent))

        iteration_scheme    : None = None
        statements          : List[VHDLStatement] = []

        statements = self.visit(ctx.sequence_of_statements())
        
        #return LoopStatement(statement_info, iteration_scheme, statements)
        return self.visitChildren(ctx)

    def visitIteration_scheme(self, ctx:vhdlParser.Iteration_schemeContext) -> IterationScheme:
        '''
        iteration_scheme
            : WHILE condition
            | FOR parameter_specification
            ;
        '''

        if ctx.WHILE():
            condition : str = None
            condition_with_agents : str = None

            condition, condition_with_agents = self.visit(ctx.condition())

            return WhileScheme(condition, condition_with_agents)

        if ctx.FOR():
            return ForScheme()
        

    # Simultaneous
    #region Simultaneous

    def visitSimultaneous_statement(self, ctx:vhdlParser.Simultaneous_statementContext, parent: VHDLStatement = None) -> None:
        '''
        simultaneous_statement
            : simple_simultaneous_statement
            | simultaneous_if_statement
            | simultaneous_case_statement
            | simultaneous_procedural_statement
            | ( label_colon)? NULL_ SEMI
            ;
        '''
        
        if ctx.simple_simultaneous_statement():
            ...

        if ctx.simultaneous_if_statement():
            ...

        if ctx.simultaneous_case_statement():
            ...

        if ctx.simultaneous_procedural_statement():
            ...

        if ctx.NULL_():
            ...

        return self.visitChildren(ctx)

    def visitSimultaneous_statement_part(self, ctx:vhdlParser.Simultaneous_statement_partContext):
        '''
        simultaneous_statement_part
            : (simultaneous_statement)*
            ;
        '''

        return self.visitChildren(ctx)

    def visitSimple_simultaneous_statement(self, ctx:vhdlParser.Simple_simultaneous_statementContext, parent: VHDLStatement = None) -> None:
        '''
        simple_simultaneous_statement
            : (label_colon)? simple_expression ASSIGN simple_expression (tolerance_aspect)? SEMI
            ;
        '''

        return self.visitChildren(ctx)

    def visitSimultaneous_if_statement(self, ctx:vhdlParser.Simultaneous_if_statementContext, parent: VHDLStatement = None) -> None:
        '''
        simultaneous_if_statement
            : (label_colon)? IF condition USE simultaneous_statement_part (
                ELSIF condition USE simultaneous_statement_part
            )* (ELSE simultaneous_statement_part)? END USE (identifier)? SEMI
            ;
        '''

        return self.visitChildren(ctx)

    def visitSimultaneous_case_statement(self, ctx:vhdlParser.Simultaneous_case_statementContext, parent: VHDLStatement = None) -> None:
        '''
        simultaneous_case_statement
            : (label_colon)? CASE expression USE (simultaneous_alternative)+ END CASE (identifier)? SEMI
            ;
        '''

        return self.visitChildren(ctx)

    def visitSimultaneous_alternative(self, ctx:vhdlParser.Simultaneous_alternativeContext):
        return self.visitChildren(ctx)

    def visitSimultaneous_procedural_statement(self, ctx:vhdlParser.Simultaneous_procedural_statementContext, parent: VHDLStatement = None) -> None:
        '''
        simultaneous_procedural_statement
            : (label_colon)? PROCEDURAL (IS)? procedural_declarative_part BEGIN procedural_statement_part END PROCEDURAL (
                identifier
            )? SEMI
            ;
        '''

        return self.visitChildren(ctx)

    #endregion

    # Assertion
    #region Assertion statement
    def visitAssertion_statement(self, ctx:vhdlParser.Assertion_statementContext, parent: VHDLStatement = None):
        return self.visitChildren(ctx) # SKIP VISIT

        '''
        assertion_statement
            : (label_colon)? assertion SEMI
            ;
        '''

        self.output_log.info("Assertion_statement")
        
        statement_info : VHDLStatement = VHDLStatement.from_tuple(parent, self.statement_manager.get_statement_general_info(AssertionStatement, ctx, parent))

        assertion : None = self.visit(ctx.assertion())

        self.output_log.info(f"assertion - statement_name:{statement_info.statement_name}, behaviour_name:{statement_info.behaviour_name}, full_behaviour_name:{statement_info.full_behaviour_name}, agent_name:{statement_info.agent_name}")
        
        return AssertionStatement(statement_info, assertion)
    
    def visitConcurrent_assertion_statement(self, ctx:vhdlParser.Concurrent_assertion_statementContext, parent: VHDLStatement = None):
        return self.visitChildren(ctx) # SKIP VISIT

        '''
        concurrent_assertion_statement
            : (label_colon)? (POSTPONED)? assertion SEMI
            ;
        '''
        
        self.output_log.info("visit 'Concurrent_assertion_statement'")

        statement_info : VHDLStatement = VHDLStatement.from_tuple(parent, self.statement_manager.get_statement_general_info(ConcurrentAssertionStatement, ctx, parent))

        self.output_log.info(f"concurrent_assertion - statement_name:{statement_info.statement_name}, behaviour_name:{statement_info.behaviour_name}, full_behaviour_name:{statement_info.full_behaviour_name}, agent_name:{statement_info.agent_name}")
        return self.visitChildren(ctx)
    #endregion

    # Procedure
    #region Procedure statement
    def visitProcedure_call_statement(self, ctx:vhdlParser.Procedure_call_statementContext, parent: VHDLStatement = None):
        return self.visitChildren(ctx) # SKIP VISIT

        '''
        procedure_call_statement
            : (label_colon)? procedure_call SEMI
            ;
        '''
        
        Debug.write_visit_to_log(self.output_log, "Procedure_call_statement")

        statement_name, behaviour_name, full_behaviour_name, agent_name = self.statement_manager.get_statement_general_info(ProcedureCallStatement, ctx)

        self.output_log.debug(f"procedure_call_statement - statement_name:{statement_info.statement_name}, behaviour_name:{statement_info.behaviour_name}, full_behaviour_name:{statement_info.full_behaviour_name}, agent_name:{statement_info.agent_name}")
    
    def visitConcurrent_procedure_call_statement(self, ctx:vhdlParser.Concurrent_procedure_call_statementContext, parent: VHDLStatement = None):
        return self.visitChildren(ctx) # SKIP VISIT

        '''
        concurrent_procedure_call_statement
            : (label_colon)? (POSTPONED)? procedure_call SEMI
            ;
        '''

        Debug.write_visit_to_log(self.output_log, "Concurrent_procedure_call")

        statement_name, behaviour_name, full_behaviour_name, agent_name = self.statement_manager.get_statement_general_info(ConcurrentProcedureCallStatement, ctx)

        self.output_log.debug(f"concurrent_procedure_call - statement_name:{statement_info.statement_name}, behaviour_name:{statement_info.behaviour_name}, full_behaviour_name:{statement_info.full_behaviour_name}, agent_name:{statement_info.agent_name}")
    
    def visitProcedure_call(self, ctx:vhdlParser.Procedure_callContext, parent: VHDLStatement = None):
        return self.visitChildren(ctx) # SKIP VISIT

        '''
        procedure_call
            : selected_name (LPAREN actual_parameter_part RPAREN)?
            ;
        '''

        Debug.write_visit_to_log(self.output_log, "Procedure_call")

    #endregion

    #endregion
    
    # Other
    #region Other

    def visitSequence_of_statements(self, ctx:vhdlParser.Sequence_of_statementsContext, parent: VHDLStatement = None) -> List[VHDLStatement]:
        '''
        sequence_of_statements
            : (sequential_statement)*
            ;
        '''

        statement_list : List[VHDLStatement] = []

        for statement in ctx.sequential_statement():
            statement_list.append(self.visitSequential_statement(statement, parent))

        return statement_list


    def visitSubtype_indication(self, ctx:vhdlParser.Subtype_indicationContext) -> Tuple[str, str]:
        '''
        subtype_indication
            : selected_name (selected_name)? (constraint)? (tolerance_aspect)?
            ;
        '''

        selected_name : str = ctx.selected_name(0).getText()
        selected_name_js : str = self.convert_subtype_to_js(selected_name)

        selected_name_2 : str = ""
        constraint : str = ""
        tolerance_aspect : str = ""

        if ctx.selected_name(1):
            selected_name_2 = ctx.selected_name(1).getText()
            print(f"selected_name_2: {selected_name_2}")

        if ctx.constraint():
            constraint = ctx.constraint().getText()
            print(f"constraint: {constraint}")

        if ctx.tolerance_aspect():
            tolerance_aspect = ctx.tolerance_aspect().getText()
            print(f"tolerance_aspect: {tolerance_aspect}")


        return selected_name, selected_name_js

    def visitWaveform(self, ctx:vhdlParser.WaveformContext) -> Tuple[str, str]:
        '''
        waveform
            : waveform_element (COMMA waveform_element)*
            | UNAFFECTED
            ;
        '''
        
        waveform                : str = None
        waveform_with_agents    : str = None

        temp                    : str = None
        temp_with_agents        : str = None

        if ctx.waveform_element():

            temp, temp_with_agents = self.visit(ctx.waveform_element(0))

            waveform = temp
            waveform_with_agents = temp_with_agents

            for index in range(len(ctx.COMMA())):
                temp = self.visit(ctx.waveform_element(index+1))

                waveform += f"{ctx.COMMA(index).getText()} {temp}"
                waveform_with_agents = f"{ctx.COMMA(index).getText()} {self.find_agent(temp)}.{temp}"
                
            return waveform, waveform_with_agents
        
        if ctx.UNAFFECTED():
            return ctx.UNAFFECTED().getText(), ctx.UNAFFECTED().getText()

    def visitWaveform_element(self, ctx:vhdlParser.Waveform_elementContext) -> Tuple[str, str]:
        '''
        waveform_element
            : expression (AFTER expression)?
            ;
        '''

        waveform_element : str = ""
        waveform_element_with_agents : str = ""

        temp : str = ""
        temp_with_agents : str = ""
        temp, temp_with_agents = self.visit(ctx.expression(0))

        waveform_element += temp
        waveform_element_with_agents += temp_with_agents
        
        if ctx.AFTER():
            temp, temp_with_agents = self.visit(ctx.exception(1))
            waveform_element += f" {ctx.AFTER().getText()} {temp}"
            waveform_element_with_agents += f" {ctx.AFTER().getText()} {temp_with_agents}"
            
        return waveform_element, waveform_element_with_agents

    def visitCondition(self, ctx:vhdlParser.ConditionContext) -> Tuple[str, str]:
        '''
        condition
            : expression
            ;
        '''
        
        return self.visit(ctx.expression())
    
    def visitExpression(self, ctx:vhdlParser.ExpressionContext) -> Tuple[str, str]:
        '''
        // NOTE that NAND/NOR are in (...)* now (used to be in (...)?).
        // (21.1.2004, e.f.)
        expression
            : relation (: logical_operator relation)*
            ;
        '''

        expression              : str = ""
        expression_with_agents  : str = ""

        logical_operator    : str = ""
        logical_operator_js : str = ""

        temp                : str = ""
        temp_with_agents    : str = ""

        temp, temp_with_agents = self.visit(ctx.relation(0))

        expression += temp
        expression_with_agents += temp_with_agents
        
        for index in range(len(ctx.logical_operator())):
            temp, temp_with_agents = self.visit(ctx.relation(index+1))
            logical_operator, logical_operator_js = self.visit(ctx.logical_operator(index))

            expression += f" {logical_operator} {temp}"
            expression_with_agents += f" {logical_operator_js} {temp_with_agents}"
            
        return expression, expression_with_agents

    def visitRelation(self, ctx:vhdlParser.RelationContext) -> Tuple[str, str]:
        '''
        relation
            : shift_expression (: relational_operator shift_expression)?
            ;
        '''
        
        relation                : str = ""
        relation_with_agents    : str = ""

        relational_operator     : str = ""
        relational_operator_js  : str = ""

        temp                : str = ""
        temp_with_agents    : str = ""

        temp, temp_with_agents = self.visit(ctx.shift_expression(0))
        
        relation = temp
        relation_with_agents = temp_with_agents

        if ctx.relational_operator():
            temp, temp_with_agents = self.visit(ctx.shift_expression(1))
            relational_operator, relational_operator_js = self.visit(ctx.relational_operator())

            relation += f" {relational_operator} {temp}"
            relation_with_agents += f" {relational_operator_js} {temp_with_agents}"
        
        return relation, relation_with_agents
    
    def visitShift_expression(self, ctx:vhdlParser.Shift_expressionContext) -> Tuple[str, str]:
        '''
        shift_expression
            : simple_expression (: shift_operator simple_expression)?
            ;
        '''

        shift_expression : str = ""
        shift_expression_with_agents : str = ""
        
        temp : str = ""
        temp_with_agents : str = ""

        temp, temp_with_agents = self.visit(ctx.simple_expression(0))

        shift_expression += temp
        shift_expression_with_agents += temp_with_agents

        if ctx.shift_operator():
            temp, temp_with_agents = self.visit(ctx.simple_expression(1))

            shift_expression += f" {ctx.shift_operator().getText()} {temp}"
            shift_expression_with_agents += f" {ctx.shift_operator().getText()} {temp_with_agents}"
        
        return shift_expression, shift_expression_with_agents
        
    def visitSimple_expression(self, ctx:vhdlParser.Simple_expressionContext) -> Tuple[str, str]:
        '''
        simple_expression
            : (PLUS | MINUS)? term (: adding_operator term)*
            ;
        '''
        
        simple_expression               : str = ""
        simple_expression_with_agents   : str = ""

        adding_operator : str = ""
        adding_operator_js : str = ""

        temp                : str = ""
        temp_with_agents    : str = ""

        temp, temp_with_agents = self.visit(ctx.term(0))
        
        simple_expression += " + " if ctx.PLUS() else ""
        simple_expression_with_agents += " + " if ctx.PLUS() else ""

        simple_expression += " - " if ctx.MINUS() else ""
        simple_expression_with_agents += " - " if ctx.MINUS() else ""
        
        simple_expression += temp
        simple_expression_with_agents += temp_with_agents
        
        for index in range(len(ctx.adding_operator())):
            temp, temp_with_agents = self.visit(ctx.term(index+1))
            adding_operator, adding_operator_js = self.visit(ctx.adding_operator(index))

            simple_expression += f" {adding_operator} {temp}"
            simple_expression_with_agents += f" {adding_operator_js} {temp_with_agents}"
        
        return simple_expression, simple_expression_with_agents

    def visitTerm(self, ctx:vhdlParser.TermContext):
        '''
        term
            : factor (: multiplying_operator factor)*
            ;
        '''
        
        term : str = ""
        term_with_agents : str = ""

        temp        : str = ""
        temp_with_agents : str = ""

        temp, temp_with_agents = self.visit(ctx.factor(0))
        
        term += temp
        term_with_agents += temp_with_agents
        
        for index in range(len(ctx.multiplying_operator())):
            temp, temp_with_agents = self.visit(ctx.factor(index+1))

            term += f" {ctx.multiplying_operator(index).getText()} {temp}"
            term_with_agents += f" * {temp_with_agents}"
        
        return term, term_with_agents

    def visitFactor(self, ctx:vhdlParser.FactorContext) -> Tuple[str, str]:
        '''
        factor
            : primary (: DOUBLESTAR primary)?
            | ABS primary
            | NOT primary
            ;
        '''
        
        factor : str = ""
        factor_with_agents : str = ""

        temp : str = ""
        temp_with_agents : str = ""

        if ctx.primary(0):
            temp, temp_with_agents = self.visit(ctx.primary(0))

            factor += temp
            factor_with_agents += temp_with_agents

            if ctx.DOUBLESTAR():
                temp, temp_with_agents = self.visit(ctx.primary(1))

                factor += f" {ctx.DOUBLESTAR().getText()} {temp}"
                factor_with_agents += f" ^= {temp_with_agents}"
        
        if ctx.ABS():
            temp, temp_with_agents = self.visit(ctx.primary(0))

            factor += f" {ctx.ABS().getText()} {temp}"
            factor_with_agents += f" {ctx.ABS().getText()} {temp_with_agents}"
        
        if ctx.NOT():
            temp, temp_with_agents = self.visit(ctx.primary(0))

            factor += f" {ctx.NOT().getText()} {temp}"
            factor_with_agents += f" {ctx.NOT().getText()} {temp_with_agents}"

        return factor, factor_with_agents
    
    def visitPrimary(self, ctx:vhdlParser.PrimaryContext):
        '''
        primary
            : literal
            | qualified_expression
            | LPAREN expression RPAREN
            | allocator
            | aggregate
            | name
            ;
        '''
        
        if ctx.literal():
            literal : str = ctx.literal().getText().replace("'", "")

            agent : str = self.find_agent(literal)

            literal_with_agent : str = f"{agent}.{literal}" if agent is not None else literal
            literal_with_agent = literal_with_agent.replace("'", "")

            return literal, literal_with_agent

        #???????
        if ctx.qualified_expression():
            print("Primary qualified expression")
            return ctx.qualified_expression().getText()
        
        if ctx.expression():
            expression : str = ""
            expression_with_agents : str = ""
            expression, expression_with_agents = self.visit(ctx.expression())

            return f"({expression})", f"({expression_with_agents})" 
        
        #???????
        if ctx.allocator():
            print("Primary allocator")
            return ctx.allocator().getText()
        
        #???????
        if ctx.aggregate():
            print("Primary aggregate")
            return self.visit(ctx.aggregate())
        
        if ctx.name():
            name    : str = ctx.name().getText()
            agent   : str = self.find_agent(name)
            return name, f"{agent}.{name}" if agent is not None else name
        
    def visitTarget(self, ctx:vhdlParser.TargetContext) -> Tuple[str, str]:
        '''
        target
            : name
            | aggregate
            ;
        '''
        
        if ctx.name():
            name    : str = ctx.name().getText()
            agent   : str = self.find_agent(name)
            return name, f"{agent}.{name}" if agent is not None else name
        
        if ctx.aggregate().getText():
            return ctx.aggregate().getText()

    def visitLiteral(self, ctx:vhdlParser.LiteralContext):
        '''
        literal
            : NULL_
            | BIT_STRING_LITERAL
            | STRING_LITERAL
            | enumeration_literal
            | numeric_literal
            ;
        '''
        if ctx.NULL_():
            return ctx.NULL_().getText()

        if ctx.BIT_STRING_LITERAL():
            return ctx.BIT_STRING_LITERAL().getText()

        if ctx.STRING_LITERAL():
            return ctx.STRING_LITERAL().getText()

        if ctx.enumeration_literal():
            return ctx.enumeration_literal().getText()

        if ctx.numeric_literal():
            return ctx.numeric_literal().getText() 
        
    def visitQualified_expression(self, ctx:vhdlParser.Qualified_expressionContext):
        '''
        qualified_expression
            : subtype_indication APOSTROPHE (aggregate | LPAREN expression RPAREN)
            ;
        '''

        return self.visitChildren(ctx)

    def visitAllocator(self, ctx:vhdlParser.AllocatorContext):
        '''
        allocator
            : NEW (qualified_expression | subtype_indication)
            ;
        '''

        return self.visitChildren(ctx)

    def visitAggregate(self, ctx:vhdlParser.AggregateContext) -> Tuple[str, str]:
        '''
        aggregate
            : LPAREN element_association (COMMA element_association)* RPAREN
            ;
        '''

        aggregate               : str = ""
        aggregate_with_agents   : str = ""

        temp                    : str = ""
        temp_with_agents        : str = ""
        
        for index in range(len(ctx.element_association())):
            temp, temp_with_agents = self.visit(ctx.element_association(index))
            if index < len(ctx.element_association())-1:
                temp += ", "
                temp_with_agents += ", "

            aggregate += temp
            aggregate_with_agents += temp_with_agents
            
        return aggregate, aggregate_with_agents

    def visitElement_association(self, ctx:vhdlParser.Element_associationContext) -> Tuple[str, str]:
        '''
        element_association
            : (choices ARROW)? expression
            ;
        '''

        element_association             : str = ""
        element_association_with_agents : str = ""

        choices                         : str = None
        choices_with_agents             : str = None

        expression                      : str = None
        expression_with_agents          : str = None

        if ctx.choices():
            choices, choices_with_agents = self.visit(ctx.choices())

        expression, expression_with_agents = self.visit(ctx.expression())

        if choices is not None:
            element_association             = f"{choices} => "
            element_association_with_agents = f"{choices_with_agents} == "

        element_association             += expression
        element_association_with_agents += expression_with_agents

        return element_association, element_association_with_agents

    def visitChoices(self, ctx:vhdlParser.ChoicesContext) -> Tuple[str, str]:
        '''
        choices
            : choice (BAR choice)*
            ;
        '''

        choices             : str = None
        choices_with_agents : str = None

        temp                : str = None
        temp_with_agents    : str = None

        for index in range(len(ctx.choice())):
            if index == 0:
                choices, choices_with_agents = self.visit(ctx.choice(0))
                continue

            temp, temp_with_agents = self.visit(ctx.choice(index))

            choices += f" | {temp}"
            choices_with_agents += f" | {temp_with_agents}"

        return choices, choices_with_agents
    
    def visitChoice(self, ctx:vhdlParser.ChoiceContext) -> Tuple[str, str]:
        '''
        choice
            : identifier
            | discrete_range
            | simple_expression
            | OTHERS
            ;
        '''

        if ctx.identifier():
            temp : str = ctx.identifier().getText()
            return temp, f"{self.find_agent(temp)}.{temp}" if self.find_agent(temp) is not None else temp 

        if ctx.discrete_range():
            return self.visit(ctx.discrete_range())

        if ctx.simple_expression():
            return self.visit(ctx.simple_expression())

        if ctx.OTHERS():
            return ctx.OTHERS().getText(), ctx.OTHERS().getText()

    def visitExplicit_range(self, ctx:vhdlParser.Explicit_rangeContext):
        '''
        explicit_range
            : simple_expression (direction simple_expression)?
            ;
        '''
            
        #simple_expression               : str = None
        #simple_expression_with_agents   : str = None
        
        #explicit_range      : str = None
        #explicit_range_js   : str = None
        
        #simple_expression, simple_expression_with_agents = self.visit(ctx.simple_expression(0))
        
        #try:
        #    exp_to_int : int = int(simple_expression)
        #except:
        #    pass

        return self.visitChildren(ctx)


    def visitIdentifier_list(self, ctx:vhdlParser.Identifier_listContext) -> List[str]:
        '''
        identifier_list
            : identifier (COMMA identifier)*
            ;
        '''
        
        identifier_list : List[str] = []
        
        for identifier in range(0, len(ctx.identifier())):
            identifier_list.append(ctx.identifier(identifier).getText())
            
        return identifier_list


    def visitAdding_operator(self, ctx:vhdlParser.Adding_operatorContext) -> Tuple[str, str]:
        '''
        adding_operator
            : PLUS
            | MINUS
            | AMPERSAND
            ;
        '''

        if ctx.PLUS():
            return "+", "+"

        if ctx.MINUS():
            return "-", "-"

        if ctx.AMPERSAND():
            return "&", "&&"

    def visitRelational_operator(self, ctx:vhdlParser.Relational_operatorContext) -> Tuple[str, str]:
        '''
        relational_operator
            : EQ
            | NEQ
            | LOWERTHAN
            | LE
            | GREATERTHAN
            | GE
            ;
        '''
        if ctx.EQ():
            return "=", "=="

        if ctx.NEQ():
            return "/=", "!="

        if ctx.LOWERTHAN():
            return "<", "<"

        if ctx.LE():
            return "<=", "<="

        if ctx.GREATERTHAN():
            return ">", ">"

        if ctx.GE():
            return ">=", ">="


        return self.visitChildren(ctx)

    def visitLogical_operator(self, ctx:vhdlParser.Logical_operatorContext) -> Tuple[str, str]:
        '''
        logical_operator
            : AND
            | OR
            | NAND
            | NOR
            | XOR
            | XNOR
            ;
        '''

        if ctx.AND():
            return "AND", "&&"

        if ctx.OR():
            return "OR", "||"

        if ctx.NAND():
            return "NAND", "NAND"

        if ctx.NOR():
            return "NOR", "NOR"

        if ctx.XOR():
            return "XOR", "^"

        if ctx.XNOR():
            return "XNOR", "XNOR"

    def visitLabel_colon(self, ctx:vhdlParser.Label_colonContext):
        return ctx.identifier().getText()

    def visitParameter_specification(self, ctx:vhdlParser.Parameter_specificationContext) -> ParameterSpecification:
        '''
        parameter_specification
            : identifier IN discrete_range
            ;
        '''

        #identifier : str = self.visit(ctx.identifier())
        #discrete_range : DiscreteRange = self.visit(ctx.discrete_range())
        #
        #return ParameterSpecification(identifier, discrete_range)
        return self.visitChildren(ctx)

    def visitRange_constraint(self, ctx:vhdlParser.Range_constraintContext):
        '''
        range_constraint
            : RANGE range_decl
            ;
        '''

        return self.visitChildren(ctx)

    def visitEnumeration_literal(self, ctx:vhdlParser.Enumeration_literalContext) -> str:
        '''
        enumeration_literal
            : identifier
            | CHARACTER_LITERAL
            ;
        '''

        if ctx.identifier():
            return ctx.identifier().getText()

        if ctx.CHARACTER_LITERAL():
            return ctx.CHARACTER_LITERAL().getText()


    def visitDiscrete_range(self, ctx:vhdlParser.Discrete_rangeContext):
        '''
        discrete_range
            : range_decl
            | subtype_indication
            ;
        '''

        #if ctx.range_decl():
        #    ...
        #
        #if ctx.subtype_indication():
        #    subtype, subtype_js = self.visit(ctx.subtype_indication())
        #    return

        return self.visitChildren(ctx)
    #endregion

    def get_vhdl_data(self) -> VHDLData :
        return self.vhdlData


    def append_declarations(self, declaration_list: List[VHDLDeclaration], parent: VHDLStatement) -> None:
        #if not declaration_list:
        #    return

        if parent.agent_name in self.vhdlData.agent_types:
            self.vhdlData.agent_types[parent.agent_name].extend(declaration_list)
        else:
            self.vhdlData.agent_types[parent.agent_name] = declaration_list

        self.vhdlData.declarations.extend(declaration_list)

    def append_agent(self, statement: VHDLStatement):
        self.vhdlData.agents.append(statement)

    def find_agent(self, target: str) -> str:
        if not self.vhdlData.agent_types:
            print("Can't find agent name. Declaration list is empty...")
            return None

        for agent in self.vhdlData.agent_types:
            if not self.vhdlData.agent_types[agent]:
                continue

            declarations_names: List[str] = [declaration.name for declaration in self.vhdlData.agent_types[agent]]
            
            if target in declarations_names:
                return agent

        return None

    def convert_subtype_to_js(self, subtype: str) -> str:
        key : str = subtype.lower()

        if key in const.vhdl_types:
            return const.vhdl_types[key]
        else:
            return subtype

    def _initialize_vhdl_data(self) -> VHDLData:
        return VHDLData([], {}, [], [])