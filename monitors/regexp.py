from antlr4 import *

from RegExpLexer import RegExpLexer
from RegExpParser import RegExpParser
from RegExpVisitor import RegExpVisitor

import intervals

def monitor(pattern, **kwargs):
    "Compile a regular expression"

    lexer = RegExpLexer(InputStream(pattern))
    stream = CommonTokenStream(lexer)
    parser = RegExpParser(stream)
    tree = parser.namedExpr()

    # lisp_tree_str = tree.toStringTree(recog=parser)
    # print(lisp_tree_str)

    # Annotate the syntax tree with positions, nullable values, and output positions
    annotator = RegExpAnnotator()
    annotator.visit(tree)

    builder = RegExpBuilder()
    builder.build(tree)

    if 'classname' in kwargs:
        classname = kwargs['classname']
    else:
        classname = builder.name

    statements = []
    statements += ["class {classname}: ".format(classname=classname)]
    statements += [""]
    statements += ["\tstates = [{}]".format(", ".join([str(init) for init in builder.initialization]))]
    statements += ["\tprev_states = [{}]".format(", ".join([str(init) for init in builder.initialization]))]
    statements += [""]
    statements += ["\tdef update(self, **kwargs):"]
    statements += [""]
    statements += ["\t\tself.prev_states = self.states.copy()"]
    statements += [""]
    statements += ["\t\t{}".format(statement) for statement in builder.statements]
    statements += [""]
    statements += ["\t\treturn {}".format(builder.output)]
    statements += [""]
    statements += ["\tdef output(self):"]
    statements += ["\t\treturn {}".format(builder.output)]

    source = '\n'.join(statements)

    if ('print_source_code' in kwargs) and kwargs['print_source_code']:
        print(source)

    code = compile(source, "<string>", "exec")

    exec(code, kwargs)

    return kwargs[classname]()


class RegExpBuilder(RegExpVisitor):

    def __init__(self):
        super(RegExpVisitor, self).__init__()
        self.name = "Monitor"
        self.statements = list()
        self.variables = set([])

    def build(self, tree, trigger_init=set([0])):

        # Start anywhere
        self.statements.append("self.states[0] = False")

        self.walk(tree, trigger_init)

        self.output = ' or '.join(['self.states[{}]'.format(i) for i in tree.output])

        # Zeroth state should be True initially
        self.initialization = [True]
        self.initialization.extend([False] * (len(self.statements) -1 ))

        return self.initialization, self.statements, self.output

    def walk(self, tree, trigger=set([0])):
        tree.trigger = trigger
        self.visit(tree)

    #def visitNamedExpr(self, ctx:RegExpParser.NamedExprContext):
    def visitNamedExpr(self, ctx):
        try:
            self.name = ctx.name.text
        except AttributeError as e:
            self.name = "Monitor"

        self.walk(ctx.child, ctx.trigger)

    #def visitTrue(self, ctx:RegExpParser.TrueContext):
    def visitTrue(self, ctx):
        trig_cond = " or ".join(['self.prev_states[{}]'.format(i) for i in ctx.trigger])
        self.statements.append("self.states[{}] = {};".format(ctx.position, trig_cond))

    #def visitAtomic(self, ctx:RegExpParser.AtomicContext):
    def visitAtomic(self, ctx):
        trig_cond = " or ".join(['self.prev_states[{}]'.format(i) for i in ctx.trigger])
        self.statements.append("self.states[{}] = {} and ({});".format(ctx.position, ctx.child.callname, trig_cond))

    #def visitNegAtomic(self, ctx:RegExpParser.NegAtomicContext):
    def visitNegAtomic(self, ctx):
        trig_cond = " or ".join(['self.prev_states[{}]'.format(i) for i in ctx.trigger])
        self.statements.append("self.states[{}] = not {} and ({});".format(ctx.position, ctx.child.callname, trig_cond))

    #def visitUnion(self, ctx:RegExpParser.UnionContext):
    def visitUnion(self, ctx):
        self.walk(ctx.left, ctx.trigger)
        self.walk(ctx.right, ctx.trigger)

    # Visit a parse tree produced by RegExpParser#Concat.
    #def visitConcat(self, ctx:RegExpParser.ConcatContext):
    def visitConcat(self, ctx):

        self.walk(ctx.left, ctx.trigger)

        if ctx.left.nullable:
            self.walk(ctx.right, ctx.left.output | ctx.trigger)
        else:
            self.walk(ctx.right, ctx.left.output)

    # Visit a parse tree produced by RegExpParser#Star.
    #def visitStar(self, ctx:RegExpParser.StarContext):
    def visitStar(self, ctx):
        self.walk(ctx.child, ctx.child.output | ctx.trigger)

    # Visit a parse tree produced by RegExpParser#Grouping.
    #def visitGrouping(self, ctx:RegExpParser.GroupingContext):
    def visitGrouping(self, ctx):
        self.walk(ctx.child, ctx.trigger)

    # Visit a parse tree produced by RegExpParser#Question.
    #def visitQuestion(self, ctx:RegExpParser.QuestionContext):
    def visitQuestion(self, ctx):
        self.walk(ctx.child, ctx.child.output | ctx.trigger)

    # Visit a parse tree produced by RegExpParser#Plus.
    #def visitPlus(self, ctx:RegExpParser.PlusContext):
    def visitPlus(self, ctx):
        self.walk(ctx.child, ctx.child.output | ctx.trigger)


class RegExpAnnotator(RegExpVisitor):

    def __init__(self):
        super(RegExpVisitor, self).__init__()
        self.num = 1
        self.variables = set()

        self.name = None
        self.statements = list()

    #def visitNamedExpr(self, ctx:RegExpParser.NamedExprContext):
    def visitNamedExpr(self, ctx):

        self.visit(ctx.child)

        try:
            ctx.name = ctx.name.text
        except AttributeError as e:
            ctx.name = None
        finally:
            ctx.nullable = ctx.child.nullable
            ctx.output = ctx.child.output

        return self.num, ctx.nullable, ctx.output

    #def visitTrue(self, ctx:RegExpParser.TrueContext):
    def visitTrue(self, ctx):

        ctx.nullable = False
        ctx.output = set([self.num])
        ctx.position = self.num
        ctx.callname = "True"
        self.num = self.num + 1

        return self.num, ctx.nullable, ctx.output

    #def visitProp(self, ctx:RegExpParser.PropContext):
    def visitProp(self, ctx):

        ctx.nullable = False
        ctx.output = set([self.num])
        ctx.position = self.num
        ctx.callname = "kwargs['{}']".format(ctx.name.text)
        self.num = self.num + 1

        return self.num, ctx.nullable, ctx.output

    #def visitPred(self, ctx:RegExpParser.PredContext):
    def visitPred(self, ctx):
        name = ctx.name.text
        nargs = ["kwargs['{}']".format(arg) for arg in ctx.args.getText().split(',')]

        ctx.callname = "{name}({params})".format(name=name, params=','.join(nargs))

        ctx.nullable = False
        ctx.output = set([self.num])
        ctx.position = self.num

        self.num = self.num + 1

        return self.num, ctx.nullable, ctx.output

    #def visitAtomic(self, ctx:RegExpParser.AtomicContext):
    def visitAtomic(self, ctx):

        self.visit(ctx.child)

        ctx.nullable = ctx.child.nullable
        ctx.output = ctx.child.output
        ctx.position = ctx.child.position

        return self.num, ctx.nullable, ctx.output

    #def visitNegAtomic(self, ctx:RegExpParser.NegAtomicContext):
    def visitNegAtomic(self, ctx):
        self.visit(ctx.child)

        ctx.nullable = ctx.child.nullable
        ctx.output = ctx.child.output
        ctx.position = ctx.child.position

        return self.num, ctx.nullable, ctx.output

    #def visitVarBind(self, ctx:RegExpParser.VarBindContext):
    def visitVarBind(self, ctx):

        self.visit(ctx.child)

        ctx.nullable = ctx.child.nullable
        ctx.output = ctx.child.output
        ctx.position = ctx.child.position

        return self.num, ctx.nullable, ctx.output

    #def visitExists(self, ctx:RegExpParser.ExistsContext):
    def visitExists(self, ctx):

        self.visit(ctx.child)

        ctx.nullable = ctx.child.nullable
        ctx.output = ctx.child.output

        ctx.varnames = set(ctx.args.getText().split(','))

        return self.num, ctx.nullable, ctx.output

    #def visitUnion(self, ctx:RegExpParser.UnionContext):
    def visitUnion(self, ctx):
        self.visit(ctx.left)
        self.visit(ctx.right)

        ctx.nullable = ctx.left.nullable or ctx.right.nullable
        ctx.output = ctx.left.output | ctx.right.output

        return self.num, ctx.nullable, ctx.output

    # Visit a parse tree produced by RegExpParser#Concat.
    #def visitConcat(self, ctx:RegExpParser.ConcatContext):
    def visitConcat(self, ctx):

        self.visit(ctx.left)
        self.visit(ctx.right)

        ctx.nullable = ctx.left.nullable and ctx.right.nullable
        ctx.output = ctx.left.output | ctx.right.output if ctx.right.nullable else ctx.right.output

        return self.num, ctx.nullable, ctx.output

    # Visit a parse tree produced by RegExpParser#Star.
    #def visitStar(self, ctx:RegExpParser.StarContext):
    def visitStar(self, ctx):

        self.visit(ctx.child)

        ctx.nullable = True
        ctx.output = ctx.child.output

        return self.num, ctx.nullable, ctx.output

    # Visit a parse tree produced by RegExpParser#Grouping.
    #def visitGrouping(self, ctx:RegExpParser.GroupingContext):
    def visitGrouping(self, ctx):

        self.visit(ctx.child)

        ctx.nullable = ctx.child.nullable
        ctx.output = ctx.child.output

        return self.num, ctx.nullable, ctx.output

    # Visit a parse tree produced by RegExpParser#Question.
    #def visitQuestion(self, ctx:RegExpParser.QuestionContext):
    def visitQuestion(self, ctx):

        self.visit(ctx.child)

        ctx.nullable = True
        ctx.output = ctx.child.output

        return self.num, ctx.nullable, ctx.output

    # Visit a parse tree produced by RegExpParser#Plus.
    #def visitPlus(self, ctx:RegExpParser.PlusContext):
    def visitPlus(self, ctx):

        self.visit(ctx.child)

        ctx.nullable = ctx.child.nullable
        ctx.output = ctx.child.output

        return self.num, ctx.nullable, ctx.output
