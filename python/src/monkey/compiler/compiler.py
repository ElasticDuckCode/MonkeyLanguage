from dataclasses import dataclass, field
from pprint import pformat
from typing import Optional

from ..ast import ast
from ..code import code
from ..obj import obj
from . import symbols


@dataclass
class Bytecode:
    instructions: bytearray
    constants: list[obj.Object]


@dataclass
class EmittedInstruction:
    opcode: code.OpCode
    position: int


@dataclass
class CompilationScope:
    instructions: bytearray = field(default_factory=bytearray)
    last_inst: EmittedInstruction | None = None
    prev_inst: EmittedInstruction | None = None


class Compiler:
    def __init__(
        self,
        constants: Optional[list[obj.Object]] = None,
        table: Optional[symbols.Table] = None,
    ) -> None:
        if constants is not None:
            self.constants: list[obj.Object] = constants
        else:
            self.constants = []
        self.op_dict: dict[str, code.OpCode] = {
            "+": code.OpCode.Add,
            "-": code.OpCode.Sub,
            "*": code.OpCode.Mul,
            "/": code.OpCode.Div,
            "==": code.OpCode.Equal,
            "!=": code.OpCode.NotEqual,
            ">": code.OpCode.GreaterThan,
            "<": code.OpCode.GreaterThan,
        }
        if table is not None:
            self.sym_table: symbols.Table = table
        else:
            self.sym_table = symbols.Table()

        # self.instructions: bytearray = bytearray(0)
        # self.last_inst: EmittedInstruction | None = None
        # self.prev_inst: EmittedInstruction | None = None
        self.main_scope = CompilationScope(bytearray(0))
        self.scopes: list[CompilationScope] = [self.main_scope]
        self.scope_ptr: int = 0

    @property
    def instructions(self) -> bytearray:
        return self.scopes[self.scope_ptr].instructions

    @instructions.setter
    def instructions(self, insts: bytearray) -> None:
        self.scopes[self.scope_ptr].instructions = insts

    @property
    def last_inst(self) -> EmittedInstruction | None:
        return self.scopes[self.scope_ptr].last_inst

    @last_inst.setter
    def last_inst(self, inst: EmittedInstruction | None) -> None:
        self.scopes[self.scope_ptr].last_inst = inst

    @property
    def prev_inst(self) -> EmittedInstruction | None:
        return self.scopes[self.scope_ptr].prev_inst

    @prev_inst.setter
    def prev_inst(self, inst: EmittedInstruction | None) -> None:
        self.scopes[self.scope_ptr].prev_inst = inst

    def enter_scope(self) -> None:
        cs = CompilationScope(bytearray(0))
        self.scopes.append(cs)
        self.scope_ptr += 1

    def leave_scope(self) -> bytearray:
        scope = self.scopes.pop()
        self.scope_ptr -= 1
        return scope.instructions

    def compile(self, node: ast.Node) -> None:
        match node:
            case ast.Program():
                for stmt in node.statements:
                    self.compile(stmt)
            case ast.LetStatement():
                self.compile(node.value)
                sym = self.sym_table.define(node.name.value)
                self.emit(code.OpCode.SetGlobal, sym.index)
            case ast.ExpressionStatement():
                self.compile(node.expression)
                self.emit(code.OpCode.Pop)
            case ast.PrefixExpression(operator="-"):
                self.compile(node.right)
                self.emit(code.OpCode.Minus)
            case ast.PrefixExpression(operator="!"):
                self.compile(node.right)
                self.emit(code.OpCode.Bang)
            case ast.InfixExpression(operator=op):
                match op:
                    case "<":
                        self.compile(node.right)
                        self.compile(node.left)
                    case _:
                        self.compile(node.left)
                        self.compile(node.right)
                self.emit(self.op_dict[op])
            case ast.IntegerLiteral():
                integer = obj.Integer(node.value)
                ident = self.add_constant(integer)
                self.emit(code.OpCode.PConstant, ident)
            case ast.StringLiteral():
                string = obj.String(node.value)
                ident = self.add_constant(string)
                self.emit(code.OpCode.PConstant, ident)
            case ast.ArrayLiteral():
                elems = node.elements
                if elems:
                    n_elems = len(elems)
                    for elem in elems:
                        self.compile(elem)
                else:
                    n_elems = 0
                self.emit(code.OpCode.PArray, n_elems)
            case ast.HashLiteral():
                pairs = node.pairs
                n_pairs = len(pairs.keys())
                for key, val in pairs.items():
                    if key and val:
                        self.compile(key)
                        self.compile(val)
                self.emit(code.OpCode.PHash, 2 * n_pairs)
            case ast.IndexExpression():
                if node.left and node.index:
                    self.compile(node.left)
                    self.compile(node.index)
                self.emit(code.OpCode.Index)
            case ast.Boolean(value=True):
                self.emit(code.OpCode.PTrue)
            case ast.Boolean(value=False):
                self.emit(code.OpCode.PFalse)
            case ast.Identifier(value="null"):
                self.emit(code.OpCode.PNull)
            case ast.Identifier():
                if node.value in self.sym_table.store.keys():
                    sym = self.sym_table.resolve(node.value)
                    self.emit(code.OpCode.GetGlobal, sym.index)
                else:
                    raise RuntimeError(f"Unable to resolve identifier: {node.value}")
            case ast.BlockStatement():
                for s in node.statements:
                    self.compile(s)
            case ast.IfExpression():
                if node.condition and node.consequence:
                    self.compile(node.condition)
                    jump_end_if = self.emit(code.OpCode.JumpNT, 9999)
                    self.compile(node.consequence)
                    if self.last_inst and self.last_inst.opcode == code.OpCode.Pop:
                        self.remove_last_instruction()
                    jump_end_else = self.emit(code.OpCode.Jump, 9999)
                    end_if = len(self.instructions)
                    if node.alternative is not None:
                        self.compile(node.alternative)
                    else:
                        self.emit(code.OpCode.PNull)
                    if self.last_inst and self.last_inst.opcode == code.OpCode.Pop:
                        self.remove_last_instruction()
                    end_else = len(self.instructions)
                    self.change_instruction_operand(jump_end_else, end_else)
                    self.change_instruction_operand(jump_end_if, end_if)
                else:
                    raise RuntimeError(
                        (
                            f"failed to compile node:\n{pformat(node)}."
                            " Conditional missing condition or consequence."
                        )
                    )
            case ast.FunctionLiteral():
                self.enter_scope()
                if node.body and len(node.body.statements) > 0:
                    self.compile(node.body)
                else:
                    self.emit(code.OpCode.Return)  # empty body same as return
                if self.last_inst and self.last_inst.opcode == code.OpCode.Pop:
                    self.remove_last_instruction()  # implict returns
                    self.emit(code.OpCode.ReturnValue)
                insts = self.leave_scope()
                fn = obj.CompiledFunction(insts)
                self.emit(code.OpCode.PConstant, self.add_constant(fn))
            case ast.ReturnStatement():
                self.compile(node.value)
                self.emit(code.OpCode.ReturnValue)
            case ast.CallExpression():
                if node.function:
                    self.compile(node.function)
                else:
                    self.emit(code.OpCode.PNull)
                self.emit(code.OpCode.Call)
            case _:
                raise RuntimeError(f"failed to compile node:\n{pformat(node)}")
        return None

    def add_constant(self, c: obj.Object) -> int:
        self.constants.append(c)
        return len(self.constants) - 1

    def add_instruction(self, ins: bytes) -> int:
        pos = len(self.instructions)
        self.instructions += ins
        return pos

    def replace_instruction(self, pos: int, ins: bytes) -> None:
        # WARNING: does not confirm instruction length matches
        #          one being replaced.
        self.instructions[pos : pos + len(ins)] = ins

    def change_instruction_operand(self, pos: int, operand: int) -> None:
        # TODO: only replaces 1 operand
        op = code.OpCode(self.instructions[pos].to_bytes(1, "big"))
        new_inst = code.make(op, operand)
        self.replace_instruction(pos, new_inst)

    def remove_last_instruction(self) -> None:
        if self.last_inst:
            # TODO: only removes one byte
            pos = self.last_inst.position
            self.instructions = self.instructions[:pos]
            self.last_inst = self.prev_inst

    def emit(self, op: code.OpCode, *operands: int) -> int:
        ins = code.make(op, *operands)
        pos = self.add_instruction(ins)
        self.set_last_instruction(op, pos)
        return pos

    def set_last_instruction(self, op: code.OpCode, pos: int) -> None:
        self.prev_inst = self.last_inst
        self.last_inst = EmittedInstruction(op, pos)

    @property
    def bytecode(self) -> Bytecode:
        return Bytecode(self.instructions, self.constants)
