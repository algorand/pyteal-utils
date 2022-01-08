from pytest import *
from tests.helpers import *
from .match import *


def test_match():
    expr = Seq(Pop(Match(AssetIdAndAmount(10, 100))))
    print(compile_sig(expr))
