from lsprotocol.types import (
    CompletionContext,
    CompletionParams,
    CompletionTriggerKind,
    Position,
    TextDocumentIdentifier,
)
from pygls.workspace import Document

from vyper_lsp.handlers.completion import CompletionHandler


def test_completion_internal_fn(ast):
    src = """
@internal
def foo():
    return

@external
def bar():
    self.foo()
"""
    ast.build_ast(src)

    src += """
@external
def baz():
    self.
"""

    doc = Document(uri="<inline source code>", source=src)
    pos = Position(line=11, character=7)
    context = CompletionContext(trigger_character=".", trigger_kind=2)
    params = CompletionParams(
        text_document=TextDocumentIdentifier(doc.uri), position=pos, context=context
    )

    analyzer = CompletionHandler(ast)
    completions = analyzer._get_completions_in_doc(doc, params)
    assert len(completions.items) == 1
    assert "foo" in [c.label for c in completions.items]


def test_completions_struct_members(ast):
    src = """
struct Foo:
    bar: uint256
    baz: uint256

@internal
def foo():
    return

@external
def bar():
    self.foo()

@external
def baz():
    g: Foo = Foo(bar=12, baz=13)
"""
    ast.build_ast(src)

    src += """
    g.
"""
    doc = Document(uri="<inline source code>", source=src)
    pos = Position(line=17, character=6)
    context = CompletionContext(trigger_character=".", trigger_kind=2)
    params = CompletionParams(
        text_document=TextDocumentIdentifier(uri=doc.uri), position=pos, context=context
    )

    analyzer = CompletionHandler(ast)
    completions = analyzer._get_completions_in_doc(doc, params)
    assert len(completions.items) == 2


def test_completions_enum_variant(ast):
    src = """
flag Foo:
    BAR
    BAZ

@internal
def foo():
    return

@external
def bar():
    self.foo()
"""
    ast.build_ast(src)

    src += """
@external
def baz():
    x: Foo = Foo.
"""

    doc = Document(uri="<inline source code>", source=src)
    pos = Position(line=15, character=18)
    context = CompletionContext(trigger_character=".", trigger_kind=2)
    params = CompletionParams(
        text_document=TextDocumentIdentifier(uri=doc.uri), position=pos, context=context
    )

    analyzer = CompletionHandler(ast)
    completions = analyzer._get_completions_in_doc(doc, params)
    assert len(completions.items) == 2
    assert "BAR" in [c.label for c in completions.items]
    assert "BAZ" in [c.label for c in completions.items]


def test_completion_fn_decorator(ast):
    src = """
@internal
def foo():
    return

@external
def bar():
    self.foo()
"""
    ast.build_ast(src)

    src += """
@
"""

    doc = Document(uri="<inline source code>", source=src)
    pos = Position(line=8, character=1)
    context = CompletionContext(
        trigger_character="@", trigger_kind=CompletionTriggerKind.TriggerCharacter
    )
    params = CompletionParams(
        text_document=TextDocumentIdentifier(uri=doc.uri), position=pos, context=context
    )

    analyzer = CompletionHandler(ast)
    completions = analyzer._get_completions_in_doc(doc, params)
    assert len(completions.items) == 7
    labels = [c.label for c in completions.items]
    assert "internal" in labels
    assert "external" in labels
    assert "payable" in labels
    assert "nonpayable" in labels
    assert "view" in labels
    assert "pure" in labels
    assert "deploy" in labels


def test_self_completions_exclude_constants_and_immutables(ast):
    """Constants and immutables should not appear in self. completions."""
    src = """#pragma version ^0.4.0

counter: uint256
MY_CONST: constant(uint256) = 100
my_immut: immutable(uint256)

@deploy
def __init__():
    my_immut = 42

@internal
def _foo():
    pass
"""
    ast.build_ast(src)
    handler = CompletionHandler(ast)

    completions = handler._dot_completions_for_element("self")
    labels = [item.label for item in completions]

    # State variable should be included
    assert "counter" in labels

    # Internal function should be included
    assert "_foo" in labels

    # Constants and immutables should NOT be included
    assert "MY_CONST" not in labels
    assert "my_immut" not in labels
