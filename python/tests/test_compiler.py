from unittest import TestCase

from src.monkey import ast, code, compiler, lexer, obj, parser


def parse(src_code: str) -> ast.Program:
    lex = lexer.Lexer(src_code)
    par = parser.Parser(lex)
    return par.parse_program()


class TestCompiler(TestCase):
    def verify_compiler(self, test_code, expected_const, insts):
        expected_insts = b""
        for inst in insts:
            expected_insts += inst
        program = parse(test_code)
        comp = compiler.Compiler()
        comp.compile(program)
        bytecode = comp.bytecode
        err_msg = (
            f"\nwant:\n{code.instructions_to_string(expected_insts)}"
            f"\ngot:\n{code.instructions_to_string(bytecode.instructions)}"
        )
        self.assertEqual(len(bytecode.instructions), len(expected_insts), err_msg)
        self.assertEqual(bytecode.instructions, expected_insts, err_msg)
        if len(expected_const):
            self.assertEqual(len(bytecode.constants), len(expected_const))
            for i, expected in enumerate(expected_const):
                match expected:
                    case bool():
                        self.assertIsInstance(bytecode.constants[i], obj.Boolean)
                        self.assertEqual(bytecode.constants[i].value, expected)
                    case int():
                        self.assertIsInstance(bytecode.constants[i], obj.Integer)
                        self.assertEqual(bytecode.constants[i].value, expected)
                    case str():
                        self.assertIsInstance(bytecode.constants[i], obj.String)
                        self.assertEqual(bytecode.constants[i].value, expected)
                    case bytearray():
                        self.assertIsInstance(
                            bytecode.constants[i], obj.CompiledFunction
                        )
                        err_msg = (
                            f"\nwant:\n{code.instructions_to_string(expected)}"
                            f"\ngot:\n{code.instructions_to_string(bytecode.constants[i].instructions)}"
                        )
                        self.assertEqual(
                            bytecode.constants[i].instructions, expected, err_msg
                        )
                    case _:
                        self.fail("Unknown object type. Please create new assert...")

    def test_compiler_integer_arithmetic(self):
        test_code_list = [
            "1 + 2",
            "3 - 4",
            "4 * 5",
            "2 / 1",
            "-1",
        ]
        expected_const_list = [[1, 2], [3, 4], [4, 5], [2, 1], [1]]
        insts_list = [
            (
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.Add),
                code.make(code.OpCode.Pop),
            ),
            (
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.Sub),
                code.make(code.OpCode.Pop),
            ),
            (
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.Mul),
                code.make(code.OpCode.Pop),
            ),
            (
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.Div),
                code.make(code.OpCode.Pop),
            ),
            (
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.Minus),
                code.make(code.OpCode.Pop),
            ),
        ]

        for test_code, expected_const, insts in zip(
            test_code_list, expected_const_list, insts_list
        ):
            self.verify_compiler(test_code, expected_const, insts)

    def test_compiler_pop_constant(self):
        test_code = "1; 2;"
        expected_const = (1, 2)
        insts = [
            code.make(code.OpCode.PConstant, 0),
            code.make(code.OpCode.Pop),
            code.make(code.OpCode.PConstant, 1),
            code.make(code.OpCode.Pop),
        ]
        self.verify_compiler(test_code, expected_const, insts)

    def test_compiler_boolean_expressions(self):
        test_code_list = [
            "true;",
            "false;",
            "1 > 2",
            "1 < 2",
            "1 != 2",
            "1 == 2",
            "true == false",
            "!true",
        ]
        expected_const_list = [(), (), (1, 2), (2, 1), (1, 2), (1, 2), (), ()]
        insts_list = [
            (
                code.make(code.OpCode.PTrue),
                code.make(code.OpCode.Pop),
            ),
            (
                code.make(code.OpCode.PFalse),
                code.make(code.OpCode.Pop),
            ),
            (
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.GreaterThan, 1),
                code.make(code.OpCode.Pop),
            ),
            (
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.GreaterThan, 1),
                code.make(code.OpCode.Pop),
            ),
            (
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.NotEqual, 1),
                code.make(code.OpCode.Pop),
            ),
            (
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.Equal, 1),
                code.make(code.OpCode.Pop),
            ),
            (
                code.make(code.OpCode.PTrue),
                code.make(code.OpCode.PFalse),
                code.make(code.OpCode.Equal, 1),
                code.make(code.OpCode.Pop),
            ),
            (
                code.make(code.OpCode.PTrue),
                code.make(code.OpCode.Bang),
                code.make(code.OpCode.Pop),
            ),
        ]

        for test_code, expected_const, insts in zip(
            test_code_list, expected_const_list, insts_list
        ):
            self.verify_compiler(test_code, expected_const, insts)

    def test_compiler_conditionals(self):
        test_code_list = [
            "if (true) { 10 }; 3333;",
            "if (false) { 10 }; 3333;",
            "if (true) { 10 } else { 20 }; 3333;",
        ]
        expected_const_list = [
            [10, 3333],
            [10, 3333],
            [10, 20, 3333],
        ]
        insts_list = [
            (
                code.make(code.OpCode.PTrue),
                code.make(code.OpCode.JumpNT, 10),
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.Jump, 11),
                code.make(code.OpCode.PNull),
                code.make(code.OpCode.Pop),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.Pop),
            ),
            (
                code.make(code.OpCode.PFalse),
                code.make(code.OpCode.JumpNT, 10),
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.Jump, 11),
                code.make(code.OpCode.PNull),
                code.make(code.OpCode.Pop),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.Pop),
            ),
            (
                code.make(code.OpCode.PTrue),
                code.make(code.OpCode.JumpNT, 10),
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.Jump, 13),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.Pop),
                code.make(code.OpCode.PConstant, 2),
                code.make(code.OpCode.Pop),
            ),
        ]

        for test_code, expected_const, insts in zip(
            test_code_list, expected_const_list, insts_list
        ):
            self.verify_compiler(test_code, expected_const, insts)

    def test_compiler_global_let_statements(self):
        test_code_list = [
            "let one = 1; let two = 2;",
            "let one = 1; one;",
            "let one = 1; let two = one; two;",
        ]
        expected_const_list = [
            (1, 2),
            (1,),
            (1,),
        ]
        insts_list = [
            (
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.SetGlobal, 0),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.SetGlobal, 1),
            ),
            (
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.SetGlobal, 0),
                code.make(code.OpCode.GetGlobal, 0),
                code.make(code.OpCode.Pop),
            ),
            (
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.SetGlobal, 0),
                code.make(code.OpCode.GetGlobal, 0),
                code.make(code.OpCode.SetGlobal, 1),
                code.make(code.OpCode.GetGlobal, 1),
                code.make(code.OpCode.Pop),
            ),
        ]
        for test_code, expected_const, insts in zip(
            test_code_list, expected_const_list, insts_list
        ):
            self.verify_compiler(test_code, expected_const, insts)

    def test_compiler_string_expresssions(self):
        test_code_list = ['"monkey"', '"mon" + "key"']
        expected_const_list = [
            ["monkey"],
            ["mon", "key"],
        ]
        insts_list = [
            (
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.Pop),
            ),
            (
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.Add),
                code.make(code.OpCode.Pop),
            ),
        ]
        for test_code, expected_const, insts in zip(
            test_code_list, expected_const_list, insts_list
        ):
            self.verify_compiler(test_code, expected_const, insts)

    def test_compiler_array_literals(self):
        test_code_list = [
            "[]",
            "[1, 2, 3]",
            "[1 + 2, 3 - 4, 5 * 6]",
        ]
        expected_const_list = [[], [1, 2, 3], [1, 2, 3, 4, 5, 6]]
        insts_list = [
            [
                code.make(code.OpCode.PArray, 0),
                code.make(code.OpCode.Pop),
            ],
            [
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.PConstant, 2),
                code.make(code.OpCode.PArray, 3),
                code.make(code.OpCode.Pop),
            ],
            [
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.Add),
                code.make(code.OpCode.PConstant, 2),
                code.make(code.OpCode.PConstant, 3),
                code.make(code.OpCode.Sub),
                code.make(code.OpCode.PConstant, 4),
                code.make(code.OpCode.PConstant, 5),
                code.make(code.OpCode.Mul),
                code.make(code.OpCode.PArray, 3),
                code.make(code.OpCode.Pop),
            ],
        ]
        for test_code, expected_const, insts in zip(
            test_code_list, expected_const_list, insts_list
        ):
            self.verify_compiler(test_code, expected_const, insts)

    def test_compiler_hash_literals(self):
        test_code_list = [
            "{}",
            "{1: 2, 3: 4, 5: 6}",
            "{1: 2 + 3, 4: 5 * 6}",
        ]
        expected_const_list = [
            [],
            [1, 2, 3, 4, 5, 6],
            [1, 2, 3, 4, 5, 6],
        ]
        insts_list = [
            [
                code.make(code.OpCode.PHash, 0),
                code.make(code.OpCode.Pop),
            ],
            [
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.PConstant, 2),
                code.make(code.OpCode.PConstant, 3),
                code.make(code.OpCode.PConstant, 4),
                code.make(code.OpCode.PConstant, 5),
                code.make(code.OpCode.PHash, 6),
                code.make(code.OpCode.Pop),
            ],
            [
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.PConstant, 2),
                code.make(code.OpCode.Add),
                code.make(code.OpCode.PConstant, 3),
                code.make(code.OpCode.PConstant, 4),
                code.make(code.OpCode.PConstant, 5),
                code.make(code.OpCode.Mul),
                code.make(code.OpCode.PHash, 4),
                code.make(code.OpCode.Pop),
            ],
        ]
        for test_code, expected_const, insts in zip(
            test_code_list, expected_const_list, insts_list
        ):
            self.verify_compiler(test_code, expected_const, insts)

    def test_compiler_index_expressions(self):
        test_code_list = [
            "[1, 2, 3][1 + 1]",
            "{1: 2}[2 - 1]",
        ]
        expected_const_list = [
            [1, 2, 3, 1, 1],
            [1, 2, 2, 1],
        ]
        insts_list = [
            [
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.PConstant, 2),
                code.make(code.OpCode.PArray, 3),
                code.make(code.OpCode.PConstant, 3),
                code.make(code.OpCode.PConstant, 4),
                code.make(code.OpCode.Add),
                code.make(code.OpCode.Index),
                code.make(code.OpCode.Pop),
            ],
            [
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.PHash, 2),
                code.make(code.OpCode.PConstant, 2),
                code.make(code.OpCode.PConstant, 3),
                code.make(code.OpCode.Sub),
                code.make(code.OpCode.Index),
                code.make(code.OpCode.Pop),
            ],
        ]
        for test_code, expected_const, insts in zip(
            test_code_list, expected_const_list, insts_list
        ):
            self.verify_compiler(test_code, expected_const, insts)

    def test_compiler_functions(self):
        test_code_list = [
            "fn() { return 5 + 10 }",
            "fn() { 5 + 10 }",
            "fn() { 1; 2; }",
            "fn() { }",
        ]
        expected_const_list = [
            [
                5,
                10,
                code.make(code.OpCode.PConstant, 0)
                + code.make(code.OpCode.PConstant, 1)
                + code.make(code.OpCode.Add)
                + code.make(code.OpCode.ReturnValue),
            ],
            [
                5,
                10,
                code.make(code.OpCode.PConstant, 0)
                + code.make(code.OpCode.PConstant, 1)
                + code.make(code.OpCode.Add)
                + code.make(code.OpCode.ReturnValue),
            ],
            [
                1,
                2,
                code.make(code.OpCode.PConstant, 0)
                + code.make(code.OpCode.Pop)
                + code.make(code.OpCode.PConstant, 1)
                + code.make(code.OpCode.ReturnValue),
            ],
            [
                code.make(code.OpCode.Return),
            ],
        ]
        insts_list = [
            [
                code.make(code.OpCode.Closure, 2, 0),
                code.make(code.OpCode.Pop),
            ],
            [
                code.make(code.OpCode.Closure, 2, 0),
                code.make(code.OpCode.Pop),
            ],
            [
                code.make(code.OpCode.Closure, 2, 0),
                code.make(code.OpCode.Pop),
            ],
            [
                code.make(code.OpCode.Closure, 0, 0),
                code.make(code.OpCode.Pop),
            ],
        ]
        for test_code, expected_const, insts in zip(
            test_code_list, expected_const_list, insts_list
        ):
            self.verify_compiler(test_code, expected_const, insts)

    def test_compiler_function_calls(self):
        test_code_list = [
            "fn() { 24 }();",
            "let noArg = fn() { 24 }; noArg();",
            "let oneArg = fn(a) { a; }; oneArg(24);",
            "let manyArg = fn(a, b, c) { a; b; c; }; manyArg(24, 25, 26) ",
        ]
        expected_const_list = [
            [
                24,
                code.make(code.OpCode.PConstant, 0)
                + code.make(code.OpCode.ReturnValue),
            ],
            [
                24,
                code.make(code.OpCode.PConstant, 0)
                + code.make(code.OpCode.ReturnValue),
            ],
            [
                code.make(code.OpCode.GetLocal, 0) + code.make(code.OpCode.ReturnValue),
                24,
            ],
            [
                code.make(code.OpCode.GetLocal, 0)
                + code.make(code.OpCode.Pop)
                + code.make(code.OpCode.GetLocal, 1)
                + code.make(code.OpCode.Pop)
                + code.make(code.OpCode.GetLocal, 2)
                + code.make(code.OpCode.ReturnValue),
                24,
                25,
                26,
            ],
        ]
        insts_list = [
            [
                code.make(code.OpCode.Closure, 1, 0),
                code.make(code.OpCode.Call, 0),
                code.make(code.OpCode.Pop),
            ],
            [
                code.make(code.OpCode.Closure, 1, 0),
                code.make(code.OpCode.SetGlobal, 0),
                code.make(code.OpCode.GetGlobal, 0),
                code.make(code.OpCode.Call, 0),
                code.make(code.OpCode.Pop),
            ],
            [
                code.make(code.OpCode.Closure, 0, 0),
                code.make(code.OpCode.SetGlobal, 0),
                code.make(code.OpCode.GetGlobal, 0),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.Call, 1),
                code.make(code.OpCode.Pop),
            ],
            [
                code.make(code.OpCode.Closure, 0, 0),
                code.make(code.OpCode.SetGlobal, 0),
                code.make(code.OpCode.GetGlobal, 0),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.PConstant, 2),
                code.make(code.OpCode.PConstant, 3),
                code.make(code.OpCode.Call, 3),
                code.make(code.OpCode.Pop),
            ],
        ]
        for test_code, expected_const, insts in zip(
            test_code_list, expected_const_list, insts_list
        ):
            self.verify_compiler(test_code, expected_const, insts)

    def test_compiler_function_scopes(self):
        c = compiler.Compiler()

        self.assertEqual(c.scope_ptr, 0)
        gtable = c.sym_table

        c.emit(code.OpCode.Mul)
        c.enter_scope()
        self.assertEqual(c.scope_ptr, 1)

        c.emit(code.OpCode.Sub)
        self.assertEqual(len(c.scopes[c.scope_ptr].instructions), 1)
        last = c.scopes[c.scope_ptr].last_inst
        self.assertEqual(last.opcode, code.OpCode.Sub)

        self.assertEqual(c.sym_table.outer, gtable, "failed to scope symbol table.")
        c.leave_scope()
        self.assertEqual(c.scope_ptr, 0)
        self.assertEqual(c.sym_table, gtable, "failed to restore global symbol table.")
        self.assertEqual(
            c.sym_table.outer, None, "corrupted global by introducing outer scope."
        )

        c.emit(code.OpCode.Add)
        self.assertEqual(len(c.scopes[c.scope_ptr].instructions), 2)
        last = c.scopes[c.scope_ptr].last_inst
        self.assertEqual(last.opcode, code.OpCode.Add)
        prev = c.scopes[c.scope_ptr].prev_inst
        self.assertEqual(prev.opcode, code.OpCode.Mul)

    def test_compiler_local_let_statements(self):
        test_code_list = [
            "let num = 55; fn() { num }",
            "fn() { let num = 55; num }",
        ]
        expected_const_list = [
            [
                55,
                code.make(code.OpCode.GetGlobal, 0)
                + code.make(code.OpCode.ReturnValue),
            ],
            [
                55,
                code.make(code.OpCode.PConstant, 0)
                + code.make(code.OpCode.SetLocal, 0)
                + code.make(code.OpCode.GetLocal, 0)
                + code.make(code.OpCode.ReturnValue),
            ],
        ]
        insts_list = [
            [
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.SetGlobal, 0),
                code.make(code.OpCode.Closure, 1, 0),
                code.make(code.OpCode.Pop),
            ],
            [
                code.make(code.OpCode.Closure, 1, 0),
                code.make(code.OpCode.Pop),
            ],
        ]
        for test_code, expected_const, insts in zip(
            test_code_list, expected_const_list, insts_list
        ):
            self.verify_compiler(test_code, expected_const, insts)

    def test_compiler_builtins(self):
        test_code_list = [
            "len([]); push([], 1);",
            "fn() { len([]) }",
        ]
        expected_const_list = [
            [1],
            [
                code.make(code.OpCode.GetBuiltIn, 0)
                + code.make(code.OpCode.PArray, 0)
                + code.make(code.OpCode.Call, 1)
                + code.make(code.OpCode.ReturnValue),
            ],
        ]
        insts_list = [
            [
                code.make(code.OpCode.GetBuiltIn, 0),
                code.make(code.OpCode.PArray, 0),
                code.make(code.OpCode.Call, 1),
                code.make(code.OpCode.Pop),
                code.make(code.OpCode.GetBuiltIn, 5),
                code.make(code.OpCode.PArray, 0),
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.Call, 2),
                code.make(code.OpCode.Pop),
            ],
            [
                code.make(code.OpCode.Closure, 0, 0),
                code.make(code.OpCode.Pop),
            ],
        ]
        for test_code, expected_const, insts in zip(
            test_code_list, expected_const_list, insts_list
        ):
            self.verify_compiler(test_code, expected_const, insts)

    def test_compiler_closures(self):
        test_code_list = [
            """
            fn(a) {
                fn(b) {
                    a + b
                }
            }
            """,
            """
            fn(a) {
                fn(b) {
                    fn(c) {
                        a + b + c
                    }
                }
            }
            """,
            """
            let global = 55;
            fn() {
                let a = 66;
                fn() {
                    let b = 77;

                    fn() {
                        let c = 88;

                        global + a + b + c;
                    }
                }
            }
            """,
        ]
        expected_const_list = [
            [
                code.make(code.OpCode.GetFree, 0)
                + code.make(code.OpCode.GetLocal, 0)
                + code.make(code.OpCode.Add)
                + code.make(code.OpCode.ReturnValue),
                code.make(code.OpCode.GetLocal, 0)
                + code.make(code.OpCode.Closure, 0, 1)
                + code.make(code.OpCode.ReturnValue),
            ],
            [
                code.make(code.OpCode.GetFree, 0)
                + code.make(code.OpCode.GetFree, 1)
                + code.make(code.OpCode.Add)
                + code.make(code.OpCode.GetLocal, 0)
                + code.make(code.OpCode.Add)
                + code.make(code.OpCode.ReturnValue),
                code.make(code.OpCode.GetFree, 0)
                + code.make(code.OpCode.GetLocal, 0)
                + code.make(code.OpCode.Closure, 0, 2)
                + code.make(code.OpCode.ReturnValue),
                code.make(code.OpCode.GetLocal, 0)
                + code.make(code.OpCode.Closure, 1, 1)
                + code.make(code.OpCode.ReturnValue),
            ],
            [
                55,
                66,
                77,
                88,
                code.make(code.OpCode.PConstant, 3)
                + code.make(code.OpCode.SetLocal, 0)
                + code.make(code.OpCode.GetGlobal, 0)
                + code.make(code.OpCode.GetFree, 0)
                + code.make(code.OpCode.Add)
                + code.make(code.OpCode.GetFree, 1)
                + code.make(code.OpCode.Add)
                + code.make(code.OpCode.GetLocal, 0)
                + code.make(code.OpCode.Add)
                + code.make(code.OpCode.ReturnValue),
                code.make(code.OpCode.PConstant, 2)
                + code.make(code.OpCode.SetLocal, 0)
                + code.make(code.OpCode.GetFree, 0)
                + code.make(code.OpCode.GetLocal, 0)
                + code.make(code.OpCode.Closure, 4, 2)
                + code.make(code.OpCode.ReturnValue),
                code.make(code.OpCode.PConstant, 1)
                + code.make(code.OpCode.SetLocal, 0)
                + code.make(code.OpCode.GetLocal, 0)
                + code.make(code.OpCode.Closure, 5, 1)
                + code.make(code.OpCode.ReturnValue),
            ],
        ]
        insts_list = [
            [
                code.make(code.OpCode.Closure, 1, 0),
                code.make(code.OpCode.Pop),
            ],
            [
                code.make(code.OpCode.Closure, 2, 0),
                code.make(code.OpCode.Pop),
            ],
            [
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.SetGlobal, 0),
                code.make(code.OpCode.Closure, 6, 0),
                code.make(code.OpCode.Pop),
            ],
        ]
        for test_code, expected_const, insts in zip(
            test_code_list, expected_const_list, insts_list
        ):
            self.verify_compiler(test_code, expected_const, insts)

    # def test_compiler_template(self):
    #     test_code_list = []
    #     expected_const_list = []
    #     insts_list = []
    #     for test_code, expected_const, insts in zip(
    #         test_code_list, expected_const_list, insts_list
    #     ):
    #         self.verify_compiler(test_code, expected_const, insts)
