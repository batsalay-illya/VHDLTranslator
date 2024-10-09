from typing import Tuple, Union

from ANTLR.vhdlVisitor import vhdlVisitor
from ANTLR.vhdlParser import vhdlParser
from VHDL.VHDLData import *
from VHDL.VHDLStatements import *
from VHDL.VHDLDeclaration import *

import Constants

class CustomVhdlVisitor(vhdlVisitor):
    def __init__(self):
        self.vhdlData : VHDLData = VHDLData(None, None, None)

    def visitLibrary_unit(self, ctx:vhdlParser.Library_unitContext) -> None: 
        '''
        library_unit
            : secondary_unit
            | primary_unit
            ;
        '''

        if not self.vhdlData.declaration_list:
            self.vhdlData.declaration_list = []
        
        if ctx.primary_unit():
            entity : Entity = self.visit(ctx.primary_unit())
            self.vhdlData.entity = entity

        if ctx.secondary_unit():
            architecture : Architecture = self.visit(ctx.secondary_unit())
            self.vhdlData.architecture = architecture

    def visitPrimary_unit(self, ctx:vhdlParser.Primary_unitContext) -> Entity:
        '''
        primary_unit
            : entity_declaration
            | configuration_declaration
            | package_declaration
            ;
        '''
        entity                    : Entity = None
        configuration_declaration : None = None
        package_declaration       : None = None
        
        if ctx.entity_declaration():
            entity = self.visit(ctx.entity_declaration())

        if ctx.configuration_declaration():
            configuration_declaration = self.visit(configuration_declaration())

        if ctx.package_declaration():
            package_declaration = self.visit(ctx.package_declaration())
            
        return entity

    def visitSecondary_unit(self, ctx:vhdlParser.Secondary_unitContext) -> Architecture:
        '''
        secondary_unit
            : architecture_body
            | package_body
            ;
        '''
        
        architecture : Architecture = None
        package_body : None = None
        
        if ctx.architecture_body():
            architecture = self.visit(ctx.architecture_body())
            
        if ctx.package_body():
            package_body = self.visit(ctx.package_body())

        return architecture

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
        
        identifier : str = ctx.identifier(0).getText() if ctx.identifier() else None
        
        generic : List[Generic] = []
        port    : List[Port] = []
        
        generic, port = self.visit(ctx.entity_header())

        self.visit(ctx.entity_declarative_part())
        if ctx.entity_statement_part():
            self.visit(ctx.entity_statement_part())

        entity : Entity = Entity(identifier, generic, port)

        return entity

    def visitEntity_header(self, ctx:vhdlParser.Entity_headerContext) -> Tuple[List[Generic], List[Port]]:
        '''
        entity_header
            : (generic_clause)? (port_clause)?
            ;
        '''

        generic : List[Generic] = []
        port    : List[Port] = []
        
        if ctx.generic_clause():
            generic = self.visit(ctx.generic_clause())
            
        port = self.visit(ctx.port_clause())

        return generic, port

    def visitGeneric_clause(self, ctx:vhdlParser.Generic_clauseContext) -> None:
        '''
        generic_clause
            : GENERIC LPAREN generic_list RPAREN SEMI
            ;
        '''
        
        return self.visitChildren(ctx)
    
    def visitGeneric_list(self, ctx:vhdlParser.Generic_listContext) -> List[Generic]:
        '''
        generic_list
            : interface_constant_declaration (SEMI interface_constant_declaration)*
            ;
        '''
        generic_list : List[Generic] = []
        
        for generic_declaration in range(0, len(ctx.interface_port_declaration())):
            generic_list_by_subtype : List[Generic] = self.visit(ctx.interface_port_declaration(generic_declaration))
            generic_list.extend(generic_list_by_subtype)
        
        return generic_list

    def visitPort_clause(self, ctx:vhdlParser.Port_clauseContext) -> None:
        '''
        port_clause
            : PORT LPAREN port_list RPAREN SEMI
            ;
        '''
        return self.visit(ctx.port_list())

    def visitInterface_port_list(self, ctx:vhdlParser.Interface_port_listContext) -> List[Port]:
        '''
        interface_port_list
            : interface_port_declaration (SEMI interface_port_declaration)*
            ;
        '''
        port_list : List[Port] = []
        
        for port_declaration in range(0, len(ctx.interface_port_declaration())):
            port_list_by_subtype : List[Port] = self.visit(ctx.interface_port_declaration(port_declaration))
            port_list.extend(port_list_by_subtype)
        
        return port_list

    def visitInterface_constant_declaration(self, ctx:vhdlParser.Interface_constant_declarationContext) -> List[Generic]:
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

        if ctx.expression():
            expression, expression_with_agents = self.visit(ctx.expression())

        for identifier in identifier_list :
            generic : Generic = Generic(identifier, "module", subtype_indication, expression)

            generic_list.append(generic)
            self.vhdlData.declaration_list.append(generic)


        return generic_list

    def visitInterface_port_declaration(self, ctx:vhdlParser.Interface_port_declarationContext) -> List[Port]:
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
            self.vhdlData.declaration_list.append(port)

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

        identifier : str = None
        architecture_declarative_part : List[VHDLDeclaration] = []
        architecture_statement_part   : List[VHDLStatement] = []

        identifier = ctx.identifier(0).getText()

        architecture_declarative_part = self.visitArchitecture_declarative_part(ctx.architecture_declarative_part(), identifier)
        architecture_statement_part = self.visitArchitecture_statement_part(ctx.architecture_statement_part(), identifier)

        return Architecture(identifier, architecture_declarative_part, architecture_statement_part)

    def visitArchitecture_declarative_part(self, ctx:vhdlParser.Architecture_declarative_partContext, agent_name: str = None) -> List[VHDLDeclaration]:
        '''
        architecture_declarative_part
            : (block_declarative_item)*
            ;
        '''
        
        declarations : List[VHDLDeclaration] = []

        for index in range(len(ctx.block_declarative_item())):
            declarative_item = self.visitBlock_declarative_item(ctx.block_declarative_item(index), agent_name)

            if isinstance(declarative_item, List):
                for item in declarative_item:
                    declarations.append(item)
            else:
                declarations.append(declarative_item)

        return declarations

    def visitArchitecture_statement_part(self, ctx:vhdlParser.Architecture_statement_partContext, agent_name: str = None) -> List[VHDLDeclaration]:
        '''
        architecture_statement_part
            : (architecture_statement)*
            ;
        '''
        
        statement_list : List[VHDLStatement] = []
        
        for index in range(len(ctx.architecture_statement())):
            statement_list.append(self.visitArchitecture_statement(ctx.architecture_statement(index), agent_name))

        return statement_list
    
    def visitArchitecture_statement(self, ctx:vhdlParser.Architecture_statementContext, agent_name: str = None) -> VHDLStatement:
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
            return self.visitBlock_statement(ctx.block_statement(), agent_name)

        if ctx.process_statement():
            return self.visitProcess_statement(ctx.process_statement(), agent_name)

        if ctx.concurrent_procedure_call_statement():
            return self.visitConcurrent_procedure_call_statement(ctx.concurrent_procedure_call_statement(), agent_name)

        if ctx.concurrent_assertion_statement():
            return self.visitConcurrent_assertion_statement(ctx.concurrent_assertion_statement(), agent_name)

        if ctx.concurrent_signal_assignment_statement():
            return self.visitConcurrent_signal_assignment_statement(ctx.concurrent_signal_assignment_statement(), agent_name)

        if ctx.component_instantiation_statement():
            return self.visitComponent_instantiation_statement(ctx.component_instantiation_statement(), agent_name)

        if ctx.generate_statement():
            return self.visitGenerate_statement(ctx.generate_statement(), agent_name)

        if ctx.concurrent_break_statement():
            return self.visitConcurrent_break_statement(ctx.concurrent_break_statement(), agent_name)

        if ctx.simultaneous_statement():
            return self.visitSimultaneous_statement(ctx.simultaneous_statement(), agent_name)

    #endregion

    # Text
    #region Text

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
            literal : str = ctx.literal().getText()

            agent : str = self.find_agent(literal)

            literal_with_agent : str = f"{agent}.{literal}" if agent is not None else literal
            literal_with_agent = literal_with_agent.replace("'", "")

            return literal, literal_with_agent

        #???????
        if ctx.qualified_expression():
            return ctx.qualified_expression().getText()
        
        if ctx.expression():
            expression : str = ""
            expression_with_agents : str = ""
            expression, expression_with_agents = self.visit(ctx.expression())

            return f"({expression})", f"({expression_with_agents})" 
        
        #???????
        if ctx.allocator():
            return ctx.allocator().getText()
        
        #???????
        if ctx.aggregate():
            return ctx.aggregate().getText()
        
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

    def visitAggregate(self, ctx:vhdlParser.AggregateContext):
        '''
        aggregate
            : LPAREN element_association (COMMA element_association)* RPAREN
            ;
        '''

        return self.visitChildren(ctx)

    def visitElement_association(self, ctx:vhdlParser.Element_associationContext):
        '''
        element_association
            : (choices ARROW)? expression
            ;
        '''

        return self.visitChildren(ctx)

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

    #endregion
    
    # Other
    #region Other
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

    def visitType_declaration(self, ctx:vhdlParser.Type_declarationContext, agent_name:str = None) -> TypeDeclaration:
        '''
        type_declaration
            : TYPE identifier (IS type_definition)? SEMI
            ;
        '''
        identifier : str = ctx.identifier().getText()


        return self.visitChildren(ctx)

    def visitType_definition(self, ctx:vhdlParser.Type_definitionContext):
        '''
        type_definition
            : scalar_type_definition
            | composite_type_definition
            | access_type_definition
            | file_type_definition
            ;
        '''

        if ctx.scalar_type_definition():
            '''
            scalar_type_definition
                : physical_type_definition
                | enumeration_type_definition
                | range_constraint
                ;
            '''
            return self.visit(ctx.scalar_type_definition())

        if ctx.composite_type_definition():
            
            return self.visit(ctx.composite_type_definition())

        if ctx.access_type_definition():
            return self.visit(ctx.access_type_definition())

        if ctx.file_type_definition():
            return self.visit(ctx.file_type_definition())


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

    def visitUnconstrained_array_definition(self, ctx:vhdlParser.Unconstrained_array_definitionContext) -> UnconstrainedArrayDefinition:
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

        return UnconstrainedArrayDefinition(index_subtype_definition, subtype, subtype_js)

    def visitIndex_subtype_definition(self, ctx:vhdlParser.Index_subtype_definitionContext) -> str:
        '''
        index_subtype_definition
            : name RANGE BOX
            ;
        '''
        return ctx.name().getText()

    def visitConstrained_array_definition(self, ctx:vhdlParser.Constrained_array_definitionContext) -> ConstrainedArrayDefinition:
        '''
        constrained_array_definition
            : ARRAY index_constraint OF subtype_indication
            ;
        '''

        index_constraint : IndexConstraint = self.visit(ctx.index_constraint())

        subtype     : str = None
        subtype_js  : str = None

        subtype, subtype_js = self.visit(ctx.subtype_indication())

        return ConstrainedArrayDefinition(index_constraint, subtype, subtype_js)


    def visitRecord_type_definition(self, ctx:vhdlParser.Record_type_definitionContext):
        '''
        record_type_definition
            : RECORD (element_declaration)+ END RECORD (identifier)?
            ;
        '''

        for index in range(len(ctx.element_declaration())):
            element_declarations.append(self.visit(ctx.element_declaration(index)))

        return RecordTypeDefinition(element_declarations)

    def visitAccess_type_definition(self, ctx:vhdlParser.Access_type_definitionContext):
        '''
        access_type_definition
            : ACCESS subtype_indication
            ;
        '''

        subtype : str = None
        subtype_js : str = None

        subtype, subtype_js = self.visit(ctx.subtype_indication())

        return AccessTypeDefinition(subtype, subtype_js)

    def visitFile_type_definition(self, ctx:vhdlParser.File_type_definitionContext):
        '''
        file_type_definition
            : FILE OF subtype_indication
            ;
        '''

        subtype : str = None
        subtype_js : str = None

        subtype, subtype_js = self.visit(ctx.subtype_indication())

        return FileTypeDefinition(subtype, subtype_js)


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
            self.vhdlData.declaration_list.append(variable)

        return variable_list

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

    #endregion

    #Statements
    #region Statements

    # Block
    #region Block statement
    def visitBlock_statement_part(self, ctx:vhdlParser.Block_statement_partContext, agent_name: str = None):
        '''
        block_statement_part
            : (architecture_statement)*
            ;
        '''
        return self.visitChildren(ctx)

    def visitBlock_statement(self, ctx:vhdlParser.Block_statementContext, agent_name: str = None):
        '''
        block_statement
            : label_colon BLOCK (LPAREN expression RPAREN)? (IS)? block_header block_declarative_part BEGIN block_statement_part END BLOCK (
                identifier
            )? SEMI
            ;
        '''

        statement_name : str = self.visit(ctx.label_colon())

        expression              : str = None
        expression_with_agents  : str = None
        block_header            : None = self.visit(ctx.block_header())
        declarations            : List[VHDLDeclaration] = self.visitBlock_declarative_part(ctx.block_declarative_part(), agent_name)
        statements              : List[VHDLStatement] = self.visitBlock_statement_part(ctx.block_statement_part(), agent_name)

        if ctx.expression():
            expression, expression_with_agents = self.visit(ctx.expression())

        return BlockStatement(statement_name, agent_name, expression, expression_with_agents, block_header, declarations, statements)

    def visitBlock_declarative_part(self, ctx:vhdlParser.Block_declarative_partContext, agent_name: str = None):
        '''
        block_declarative_part
            : (block_declarative_item)*
            ;
        '''

        declaration_list : List[VHDLDeclaration] = []

        for declaration in ctx.block_declarative_item():
            declaration_list.append(self.visitBlock_declarative_item(declaration, agent_name))

        return declaration_list
    
    def visitBlock_declarative_item(self, ctx:vhdlParser.Block_declarative_itemContext, agent_name: str) -> VHDLDeclaration:
        '''
        block_declarative_item
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
            declaration = self.visitSubprogram_declaration(ctx.subprogram_declaration(), agent_name)

        if ctx.subprogram_body():
            declaration = self.visitSubprogram_body(ctx.subprogram_body(), agent_name)

        if ctx.type_declaration():
            declaration = self.visitType_declaration(ctx.type_declaration(), agent_name)

        if ctx.subtype_declaration():
            declaration = self.visitSubtype_declaration(ctx.subtype_declaration(), agent_name)

        if ctx.constant_declaration():
            declaration = self.visitConstant_declaration(ctx.constant_declaration(), agent_name)

        if ctx.signal_declaration():
            declaration = self.visitSignal_declaration(ctx.signal_declaration(), agent_name)

        if ctx.variable_declaration():
            declaration = self.visitVariable_declaration(ctx.variable_declaration(), agent_name)

        if ctx.file_declaration():
            declaration = self.visitFile_declaration(ctx.file_declaration(), agent_name)

        if ctx.alias_declaration():
            declaration = self.visitAlias_declaration(ctx.alias_declaration(), agent_name)

        if ctx.component_declaration():
            declaration = self.visitComponent_declaration(ctx.component_declaration(), agent_name)

        if ctx.attribute_declaration():
            declaration = self.visitAttribute_declaration(ctx.attribute_declaration(), agent_name)

        if ctx.attribute_specification():
            declaration = self.visitAttribute_specification(ctx.attribute_specification(), agent_name)

        if ctx.configuration_specification():
            declaration = self.visitConfiguration_specification(ctx.configuration_specification(), agent_name)

        if ctx.disconnection_specification():
            declaration = self.visitDisconnection_specification(ctx.disconnection_specification(), agent_name)

        if ctx.step_limit_specification():
            declaration = self.visitStep_limit_specification(ctx.step_limit_specification(), agent_name)

        if ctx.use_clause():
            declaration = self.visitUse_clause(ctx.use_clause(), agent_name)

        if ctx.group_template_declaration():
            declaration = self.visitGroup_template_declaration(ctx.group_template_declaration(), agent_name)

        if ctx.group_declaration():
            declaration = self.visitGroup_declaration(ctx.group_declaration(), agent_name)

        if ctx.nature_declaration():
            declaration = self.visitNature_declaration(ctx.nature_declaration(), agent_name)

        if ctx.subnature_declaration():
            declaration = self.visitSubnature_declaration(ctx.subnature_declaration(), agent_name)

        if ctx.quantity_declaration():
            declaration = self.visitQuantity_declaration(ctx.quantity_declaration(), agent_name)

        if ctx.terminal_declaration():
            declaration = self.visitTerminal_declaration(ctx.terminal_declaration(), agent_name)

        if isinstance(declaration, List):
            self.vhdlData.declaration_list.extend(declaration)
        else:
            self.vhdlData.declaration_list.append(declaration)

        return declaration

    #endregion

    # Procedure
    #region Procedure statement
    def visitProcedure_call_statement(self, ctx:vhdlParser.Procedure_call_statementContext, agent_name: str = None):
        '''
        procedure_call_statement
            : (label_colon)? procedure_call SEMI
            ;
        '''
        
        statement_name : str = None

        if ctx.label_colon():
            statement_name = self.visit(ctx.label_colon())

        return self.visitChildren(ctx)
    
    def visitConcurrent_procedure_call_statement(self, ctx:vhdlParser.Concurrent_procedure_call_statementContext, agent_name: str = None):
        '''
        concurrent_procedure_call_statement
            : (label_colon)? (POSTPONED)? procedure_call SEMI
            ;
        '''
        statement_name : str = None

        if ctx.label_colon():
            statement_name = self.visit(ctx.label_colon())

        return self.visitChildren(ctx)
    
    def visitProcedure_call(self, ctx:vhdlParser.Procedure_callContext, agent_name: str = None):
        '''
        procedure_call
            : selected_name (LPAREN actual_parameter_part RPAREN)?
            ;
        '''
        return self.visitChildren(ctx)
    #endregion

    # Process
    #region Process statement

    def visitProcess_statement(self, ctx:vhdlParser.Process_statementContext, agent_name: str = None):
        '''
        process_statement
            : (label_colon)? (POSTPONED)? PROCESS (LPAREN sensitivity_list RPAREN)? (IS)? process_declarative_part BEGIN process_statement_part END (
                POSTPONED
            )? PROCESS (identifier)? SEMI
            ;
        '''
        
        statement_name : str = None

        if ctx.label_colon():
            statement_name = self.visit(ctx.label_colon())
        else:
            statement_name = "NONAME_PROCESS"

        sensitivity_list                : List[str] = None
        sensitivity_list_with_agents    : List[str] = None

        declarations    : List[VHDLDeclaration] = self.visitProcess_declarative_part(ctx.process_declarative_part(), statement_name)
        statements      : List[VHDLStatement] = self.visitProcess_statement_part(ctx.process_statement_part(), statement_name)
        
        if ctx.sensitivity_list():
            sensitivity_list, sensitivity_list_with_agents = self.visit(ctx.sensitivity_list())

        return ProcessStatement(statement_name, agent_name, sensitivity_list, sensitivity_list_with_agents, declarations, statements)

    def visitSensitivity_list(self, ctx:vhdlParser.Sensitivity_listContext):
        '''
        sensitivity_list
            : name (COMMA name)*
            ;
        '''

        sensitive_list              : List[str] = []
        sensitive_list_with_agents  : List[str] = []

        temp                        : str = None
        agent                       : str = None

        for index in range(len(ctx.name())):
            temp = ctx.name(index).getText()
            agent = self.find_agent(temp)

            sensitive_list.append(temp)
            sensitive_list_with_agents.append(f"{agent}.{temp}" if agent is not None else f"{temp}")

        return sensitive_list, sensitive_list_with_agents

    def visitProcess_declarative_part(self, ctx:vhdlParser.Process_declarative_partContext, agent_name: str = None):
        '''
        process_declarative_part
            : (process_declarative_item)*
            ;
        '''

        declarations : List[VHDLDeclaration] = []

        for index in range(len(ctx.process_declarative_item())):
            declarative_item = self.visitProcess_declarative_item(ctx.process_declarative_item(index), agent_name)

            if isinstance(declarative_item, List):
                for item in declarative_item:
                    declarations.append(item)
            else:
                declarations.append(declarative_item)
        
        return declarations
    
    def visitProcess_declarative_item(self, ctx:vhdlParser.Process_declarative_itemContext, agent_name: str = None):
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
            return self.visitSubprogram_declaration(ctx.subprogram_declaration(), agent_name)

        if ctx.subprogram_body():
            return self.visitSubprogram_body(ctx.subprogram_body(), agent_name)

        if ctx.type_declaration():
            return self.visitType_declaration(ctx.type_declaration(), agent_name)

        if ctx.subtype_declaration():
            return self.visitSubtype_declaration(ctx.subtype_declaration(), agent_name)

        if ctx.constant_declaration():
            return self.visitConstant_declaration(ctx.constant_declaration(), agent_name)

        if ctx.variable_declaration():
            return self.visitVariable_declaration(ctx.variable_declaration(), agent_name)

        if ctx.file_declaration():
            return self.visitFile_declaration(ctx.file_declaration(), agent_name)

        if ctx.alias_declaration():
            return self.visitAlias_declaration(ctx.alias_declaration(), agent_name)

        if ctx.attribute_declaration():
            return self.visitAttribute_declaration(ctx.attribute_declaration(), agent_name)

        if ctx.attribute_specification():
            return self.visitAttribute_specification(ctx.attribute_specification(), agent_name)

        if ctx.use_clause():
            return self.visitUse_clause(ctx.use_clause(), agent_name)

        if ctx.group_template_declaration():
            return self.visitGroup_template_declaration(ctx.group_template_declaration(), agent_name)

        if ctx.group_declaration():
            return self.visitGroup_declaration(ctx.group_declaration(), agent_name)

    def visitProcess_statement_part(self, ctx:vhdlParser.Process_statement_partContext, agent_name: str = None):
        '''
        process_statement_part
            : (sequential_statement)*
            ;
        '''
        
        sequential_statements : List[VHDLStatement] = []

        for statement in ctx.sequential_statement():
            sequential_statements.append(self.visitSequential_statement(statement, agent_name))

        return sequential_statements
    
    def visitSequential_statement(self, ctx:vhdlParser.Sequential_statementContext, agent_name: str = None):
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
            return self.visitWait_statement(ctx.wait_statement(), agent_name)

        if ctx.assertion_statement():
            return self.visitAssertion_statement(ctx.assertion_statement(), agent_name)

        if ctx.report_statement():
            return self.visitReport_statement(ctx.report_statement(), agent_name)

        if ctx.signal_assignment_statement():
            return self.visitSignal_assignment_statement(ctx.signal_assignment_statement(), agent_name)

        if ctx.variable_assignment_statement():
            return self.visitVariable_assignment_statement(ctx.variable_assignment_statement(), agent_name)

        if ctx.if_statement():
            return self.visitIf_statement(ctx.if_statement(), agent_name)

        if ctx.case_statement():
            return self.visitCase_statement(ctx.case_statement(), agent_name)

        if ctx.loop_statement():
            return self.visitLoop_statement(ctx.loop_statement(), agent_name)

        if ctx.next_statement():
            return self.visitNext_statement(ctx.next_statement(), agent_name)

        if ctx.exit_statement():
            return self.visitExit_statement(ctx.exit_statement(), agent_name)

        if ctx.return_statement():
            return self.visitReturn_statement(ctx.return_statement(), agent_name)

        if ctx.break_statement():
            return self.visitBreak_statement(ctx.break_statement(), agent_name)

        if ctx.procedure_call_statement():
            return self.visitProcedure_call_statement(ctx.procedure_call_statement(), agent_name)    
    #endregion

    # Assignment
    #region Assignment statements
    def visitSignal_assignment_statement(self, ctx:vhdlParser.Signal_assignment_statementContext, agent_name: str = None):
        '''
        signal_assignment_statement
            : (label_colon)? target LE (delay_mechanism)? waveform SEMI
            ;
        '''

        statement_name : str = None

        target : str = ctx.target().getText()
        target_with_agent : str = f"{self.find_agent(target)}.{target}"

        delay_mechanism : str = None

        waveform : str = None
        waveform_with_agents : str = None

        waveform, waveform_with_agents = self.visit(ctx.waveform())

        if ctx.label_colon():
            statement_name = self.visit(ctx.label_colon())

        if ctx.delay_mechanism():
            delay_mechanism = ctx.target().getText()
        
        return SignalAssignment(statement_name, agent_name, target, target_with_agent, delay_mechanism, waveform, waveform_with_agents)

    def visitVariable_assignment_statement(self, ctx:vhdlParser.Variable_assignment_statementContext, agent_name: str = None):
        '''
        variable_assignment_statement
            : (label_colon)? target VARASGN expression SEMI
            ;
        '''

        statement_name          : str = None
        
        target                  : str = None
        target_with_agents      : str = None

        target, target_with_agents = self.visit(ctx.target())

        expression              : str = None
        expression_with_agents  : str = None

        expression, expression_with_agents = self.visit(ctx.expression())

        if ctx.label_colon():
            statement_name = self.visit(ctx.label_colon())

        return VariableAssignment(statement_name, agent_name, target, target_with_agents, expression, expression_with_agents)
    
    def visitConcurrent_signal_assignment_statement(self, ctx:vhdlParser.Concurrent_signal_assignment_statementContext, agent_name: str = None):
        '''
        concurrent_signal_assignment_statement
            : (label_colon)? (POSTPONED)? (conditional_signal_assignment | selected_signal_assignment)
            ;
        '''
        
        if ctx.conditional_signal_assignment():
            return self.visitConditional_signal_assignment(ctx.conditional_signal_assignment(), agent_name)

        if ctx.selected_signal_assignment():
            return self.visitSelected_signal_assignment(ctx.selected_signal_assignment(), agent_name)
    
    def visitConditional_signal_assignment(self, ctx:vhdlParser.Conditional_signal_assignmentContext, agent_name: str = None) -> ConditionalSignalAssignment:
        '''
        conditional_signal_assignment
            : target LE opts conditional_waveforms SEMI
            ;
        '''
        
        target : str = None
        target_with_agent : str = None

        target, target_with_agent = self.visit(ctx.target())

        opts : str = ctx.opts().getText()
        conditional_waveforms : ConditionalWaveform = self.visit(ctx.conditional_waveforms())

        return ConditionalSignalAssignment(None, agent_name, target, target_with_agent, opts, conditional_waveforms)

    
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
    

    def visitSelected_signal_assignment(self, ctx:vhdlParser.Selected_signal_assignmentContext, agent_name: str = None):
        '''
        selected_signal_assignment
            : WITH expression SELECT target LE opts selected_waveforms SEMI
            ;
        '''
        
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
    
        return SelectedSignalAssignment(None, agent_name, target, target_with_agent, opts, expression, expression_with_agents, selected_waveforms)

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

    # Case
    #region Case statement
    def visitCase_statement(self, ctx:vhdlParser.Case_statementContext, agent_name: str = None):
        '''
        case_statement
            : (label_colon)? CASE expression IS (case_statement_alternative)+ END CASE (identifier)? SEMI
            ;
        '''

        statement_name : str = None

        expression : str = None
        expression_with_agents : str = None

        expression, expression_with_agents = self.visit(ctx.expression())

        case_alternatives : List[CaseAlternative] = []

        if ctx.label_colon():
            statement_name = self.visit(ctx.label_colon())

        for case in ctx.case_statement_alternative():
            case_alternatives.append(self.visitCase_statement_alternative(case, agent_name))

        return CaseStatement(statement_name, agent_name, expression, expression_with_agents, case_alternatives)
    
    def visitCase_statement_alternative(self, ctx:vhdlParser.Case_statement_alternativeContext, agent_name: str = None):
        '''
        case_statement_alternative
            : WHEN choices ARROW sequence_of_statements
            ;
        '''

        choice : str = None
        statements : List[VHDLStatement] = self.visitSequence_of_statements(ctx.sequence_of_statements(), agent_name)

        return CaseAlternative(choice, statements)
    #endregion

    # Assertion
    #region Assertion statement
    def visitAssertion_statement(self, ctx:vhdlParser.Assertion_statementContext, agent_name: str = None):
        '''
        assertion_statement
            : (label_colon)? assertion SEMI
            ;
        '''
        
        statement_name : str = None
        assertion : None = self.visit(ctx.assertion())

        if ctx.label_colon():
            statement_name = self.visit(ctx.label_colon())

        return AssertionStatement(statement_name, agent_name, assertion)
    
    def visitConcurrent_assertion_statement(self, ctx:vhdlParser.Concurrent_assertion_statementContext, agent_name: str = None):
        '''
        concurrent_assertion_statement
            : (label_colon)? (POSTPONED)? assertion SEMI
            ;
        '''
        statement_name : str = None

        if ctx.label_colon():
            statement_name = self.visit(ctx.label_colon())

        return self.visitChildren(ctx)
    #endregion
    
    def visitWait_statement(self, ctx:vhdlParser.Wait_statementContext, agent_name: str = None):
        '''
        wait_statement
            : (label_colon)? WAIT (sensitivity_clause)? (condition_clause)? (timeout_clause)? SEMI
            ;
        '''
        
        statement_name : str = None

        sensitivity_clause              : List[str] = []
        sensitivity_clause_with_agents  : List[str] = []
        condition_clause                : None = None
        timeout_clause                  : None = None

        if ctx.label_colon():
            statement_name = self.visit(ctx.label_colon())
        else:
            statement_name = f"Wait{self.wait_statement_index}"
            self.wait_statement_index += 1

        if ctx.sensitivity_clause():
            sensitivity_clause, sensitivity_clause_with_agents = self.visit(ctx.sensitivity_clause())

        if ctx.timeout_clause():
            timeout_clause = self.visit(ctx.timeout_clause())

        return WaitStatement(statement_name, agent_name, sensitivity_clause, condition_clause, timeout_clause)
        
    def visitReport_statement(self, ctx:vhdlParser.Report_statementContext, agent_name: str = None):
        '''
        report_statement
            : (label_colon)? REPORT expression (SEVERITY expression)? SEMI
            ;
        '''
        
        statement_name                  : str = None
        report_expression               : str = None
        report_expression_with_agents   : str = None
        severity_expression             : str = None
        severity_expression_with_agents : str = None

        report_expression, report_expression_with_agents = self.visit(ctx.expression(0))

        if ctx.label_colon():
            statement_name = self.visit(ctx.label_colon())

        if ctx.expression(1):
            severity_expression, severity_expression_with_agents = self.visit(ctx.expression(1))

        return ReportStatement(statement_name, agent_name, report_expression, report_expression_with_agents, severity_expression, severity_expression_with_agents)

    def visitIf_statement(self, ctx:vhdlParser.If_statementContext, agent_name: str = None):
        '''
        if_statement
            : (label_colon)? IF condition THEN sequence_of_statements (
                ELSIF condition THEN sequence_of_statements
            )* (ELSE sequence_of_statements)? END IF (identifier)? SEMI
            ;
        '''
        
        statement_name              : str = None

        condition                   : str = None
        condition_with_agents       : str = None

        temp                        : str = None
        temp_with_agents            : str = None

        statements                  : List[VHDLStatement] = []

        elsif_condition             : str = None
        elsif_condition_with_agents : str = None

        elsif_statements            : List[VHDLStatement] = []
        else_statements             : List[VHDLStatement] = []
        
        if ctx.label_colon():
            statement_name = self.visit(ctx.label_colon());
        
        temp, temp_with_agents = self.visit(ctx.condition(0))

        condition = temp
        condition_with_agents = temp_with_agents

        statements = self.visitSequence_of_statements(ctx.sequence_of_statements(0), agent_name)
        
        i : int = 1
        for _ in range(len(ctx.ELSIF())):
            temp, temp_with_agents = self.visit(ctx.condition(i))

            elsif_condition = temp
            elsif_condition_with_agents = temp_with_agents

            elsif_statements = self.visitSequence_of_statements(ctx.sequence_of_statements(i), agent_name)
            i+=1
            
        if ctx.ELSE():
            else_statements = self.visitSequence_of_statements(ctx.sequence_of_statements(i), agent_name)

        return IfStatement(statement_name, agent_name, condition, condition_with_agents, statements, elsif_condition, elsif_condition_with_agents, elsif_statements, else_statements)

    # Loop
    #region Loop

    def visitLoop_statement(self, ctx:vhdlParser.Loop_statementContext, agent_name: str = None):
        '''
        loop_statement
            : (label_colon)? (iteration_scheme)? LOOP sequence_of_statements END LOOP (identifier)? SEMI
            ;
        '''

        statement_name      : str = None
        iteration_scheme    : None = None
        statements          : List[VHDLStatement] = []

        if ctx.label_colon():
            statement_name = self.visit(ctx.label_colon())

        statements = self.visit(ctx.sequence_of_statements())
        
        return LoopStatement(statement_name, agent_name, iteration_scheme, statements)

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

    #endregion
    
    def visitNext_statement(self, ctx:vhdlParser.Next_statementContext, agent_name: str = None):
        '''
        next_statement
            : (label_colon)? NEXT (identifier)? (WHEN condition)? SEMI
            ;
        '''
        
        statement_name : str = None

        if ctx.label_colon():
            statement_name = self.visit(ctx.label_colon())

        return self.visitChildren(ctx)
    
    def visitExit_statement(self, ctx:vhdlParser.Exit_statementContext):
        '''
        exit_statement
            : (label_colon)? EXIT (identifier)? (WHEN condition)? SEMI
            ;
        '''
        
        statement_name : str = None

        if ctx.label_colon():
            statement_name = self.visit(ctx.label_colon())

        return self.visitChildren(ctx)
    
    def visitReturn_statement(self, ctx:vhdlParser.Return_statementContext, agent_name: str = None):
        '''
        return_statement
            : (label_colon)? RETURN (expression)? SEMI
            ;
        '''
        
        statement_name : str = None

        if ctx.label_colon():
            statement_name = self.visit(ctx.label_colon())

        return self.visitChildren(ctx)
    
    def visitBreak_statement(self, ctx:vhdlParser.Break_statementContext, agent_name: str = None):
        '''
        break_statement
            : (label_colon)? BREAK (break_list)? (WHEN condition)? SEMI
            ;
        '''
        
        statement_name : str = None

        if ctx.label_colon():
            statement_name = self.visit(ctx.label_colon())

        return self.visitChildren(ctx)

    

    def visitComponent_instantiation_statement(self, ctx:vhdlParser.Component_instantiation_statementContext):
        '''
        component_instantiation_statement
            : label_colon instantiated_unit (generic_map_aspect)? (port_map_aspect)? SEMI
            ;
        '''
        
        statement_name : str = None

        if ctx.label_colon():
            statement_name = self.visit(ctx.label_colon())

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

        statement_name : str = None

        if ctx.label_colon():
            statement_name = self.visit(ctx.label_colon())

        return self.visitChildren(ctx)

    # Simultaneous
    #region Simultaneous

    def visitSimultaneous_statement(self, ctx:vhdlParser.Simultaneous_statementContext, agent_name: str = None) -> None:
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
            print("simple_simultaneous_statement")

        if ctx.simultaneous_if_statement():
            print("simultaneous_if_statement")

        if ctx.simultaneous_case_statement():
            print("simultaneous_case_statement")

        if ctx.simultaneous_procedural_statement():
            print("simultaneous_procedural_statement")

        if ctx.NULL_():
            print("simultaneous NULL_")

        return self.visitChildren(ctx)

    def visitSimultaneous_statement_part(self, ctx:vhdlParser.Simultaneous_statement_partContext):
        '''
        simultaneous_statement_part
            : (simultaneous_statement)*
            ;
        '''

        return self.visitChildren(ctx)

    def visitSimple_simultaneous_statement(self, ctx:vhdlParser.Simple_simultaneous_statementContext, agent_name: str = None) -> None:
        '''
        simple_simultaneous_statement
            : (label_colon)? simple_expression ASSIGN simple_expression (tolerance_aspect)? SEMI
            ;
        '''

        return self.visitChildren(ctx)

    def visitSimultaneous_if_statement(self, ctx:vhdlParser.Simultaneous_if_statementContext, agent_name: str = None) -> None:
        '''
        simultaneous_if_statement
            : (label_colon)? IF condition USE simultaneous_statement_part (
                ELSIF condition USE simultaneous_statement_part
            )* (ELSE simultaneous_statement_part)? END USE (identifier)? SEMI
            ;
        '''

        return self.visitChildren(ctx)

    def visitSimultaneous_case_statement(self, ctx:vhdlParser.Simultaneous_case_statementContext, agent_name: str = None) -> None:
        '''
        simultaneous_case_statement
            : (label_colon)? CASE expression USE (simultaneous_alternative)+ END CASE (identifier)? SEMI
            ;
        '''

        return self.visitChildren(ctx)

    def visitSimultaneous_alternative(self, ctx:vhdlParser.Simultaneous_alternativeContext):
        return self.visitChildren(ctx)

    def visitSimultaneous_procedural_statement(self, ctx:vhdlParser.Simultaneous_procedural_statementContext, agent_name: str = None) -> None:
        '''
        simultaneous_procedural_statement
            : (label_colon)? PROCEDURAL (IS)? procedural_declarative_part BEGIN procedural_statement_part END PROCEDURAL (
                identifier
            )? SEMI
            ;
        '''

        return self.visitChildren(ctx)

    #endregion

    def visitSequence_of_statements(self, ctx:vhdlParser.Sequence_of_statementsContext, agent_name: str = None) -> List[VHDLStatement]:
        '''
        sequence_of_statements
            : (sequential_statement)*
            ;
        '''

        statement_list : List[VHDLStatement] = []

        for statement in ctx.sequential_statement():
            statement_list.append(self.visitSequential_statement(statement, agent_name))

        return statement_list

    #endregion    

    def get_vhdl_data(self) -> VHDLData :
        return self.vhdlData

    def find_agent(self, target: str) -> str:
        if not self.vhdlData.declaration_list:
            print("Can't find agent name. Declaration list is empty...")
            return None

        for declaration in self.vhdlData.declaration_list:
            if target == declaration.name:
                return declaration.agent_name
        return None

    def convert_subtype_to_js(self, subtype: str) -> str:
        key : str = subtype.lower()

        if key in Constants.vhdl_types:
            return Constants.vhdl_types[key]