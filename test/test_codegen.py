#!/usr/bin/env python

__copyright__ = "Copyright (C) 2020 Andreas Kloeckner"

__license__ = """
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import sys

import loopy as lp
import numpy as np
import pyopencl as cl
import pyopencl.array as cl_array  # noqa
import pyopencl.cltypes as cltypes  # noqa
import pyopencl.tools as cl_tools  # noqa
from pyopencl.tools import (  # noqa
        pytest_generate_tests_for_pyopencl as pytest_generate_tests)
import pytest  # noqa

import pytato as pt


def test_basic_codegen(ctx_factory):
    ctx = ctx_factory()
    queue = cl.CommandQueue(ctx)

    namespace = pt.Namespace()
    x = pt.Placeholder(namespace, "x", (5,), np.int)
    prog = pt.generate_loopy(x * x, target=pt.PyOpenCLTarget(queue))
    x_in = np.array([1, 2, 3, 4, 5])
    _, (out,) = prog(x=x_in)
    assert (out == x_in * x_in).all()


def test_codegen_with_DictOfNamedArrays(ctx_factory):  # noqa
    ctx = ctx_factory()
    queue = cl.CommandQueue(ctx)

    namespace = pt.Namespace()
    x = pt.Placeholder(namespace, "x", (5,), np.int)
    y = pt.Placeholder(namespace, "y", (5,), np.int)
    x_in = np.array([1, 2, 3, 4, 5])
    y_in = np.array([6, 7, 8, 9, 10])

    result = pt.DictOfNamedArrays(dict(x_out=x, y_out=y))

    # Without return_dict.
    prog = pt.generate_loopy(result, target=pt.PyOpenCLTarget(queue))
    _, (x_out, y_out) = prog(x=x_in, y=y_in)
    assert (x_out == x_in).all()
    assert (y_out == y_in).all()

    # With return_dict.
    prog = pt.generate_loopy(result,
            target=pt.PyOpenCLTarget(queue),
            options=lp.Options(return_dict=True))

    _, outputs = prog(x=x_in, y=y_in)
    assert (outputs["x_out"] == x_in).all()
    assert (outputs["y_out"] == y_in).all()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        exec(sys.argv[1])
    else:
        from pytest import main
        main([__file__])

# vim: filetype=pyopencl:fdm=marker