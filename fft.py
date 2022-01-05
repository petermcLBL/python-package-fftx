
import numpy as np

try:
    import cupy as cp
except ModuleNotFoundError:
    cp = None

import snowwhite as sw
from snowwhite.dftsolver import *
from snowwhite.mddftsolver import *

_solver_cache = {}

def _solver_key(tf, src):
    szstr = 'x'.join([str(n) for n in list(src.shape)])
    retkey = tf + '_' + szstr
    if sw.get_array_module(src) == cp:
        retkey = retkey + '_CU'
    return retkey
    
def _solver_opts(src):
    return {SW_OPT_CUDA : True} if (sw.get_array_module(src) == cp) else {SW_OPT_CUDA : False}

def make_complex128(src):
    if sw.get_array_module(src) == cp:
        xp = cp
    else:
        xp = np
    if xp.iscomplexobj(src):
        src_complex = src
    else:
        src_complex = src + 0*1j
    if src_complex.dtype == xp.complex128:
        return src_complex
    else:
        return src_complex.astype(xp.complex128)
    
def fft(src):
    global _solver_cache
    ckey = _solver_key('fft', src)
    solver = _solver_cache.get(ckey, 0)
    if solver == 0:
        problem = DftProblem(src.size, SW_FORWARD)
        solver = DftSolver(problem)
        _solver_cache[ckey] = solver
    result = solver.solve(make_complex128(src))
    return result

def ifft(src):
    global _solver_cache
    ckey = _solver_key('1fft', src)
    solver = _solver_cache.get(ckey, 0)
    if solver == 0:
        problem = DftProblem(src.size, SW_INVERSE)
        solver = DftSolver(problem)
        _solver_cache[ckey] = solver
    result = solver.solve(make_complex128(src))
    return result

def fftn(src):
    global _solver_cache
    ckey = _solver_key('fftn', src)
    solver = _solver_cache.get(ckey, 0)
    if solver == 0:
        problem = MddftProblem(list(src.shape), SW_FORWARD)
        solver = MddftSolver(problem, _solver_opts(src))
        _solver_cache[ckey] = solver
    result = solver.solve(make_complex128(src))
    return result

def ifftn(src):
    global _solver_cache
    ckey = _solver_key('ifftn', src)
    solver = _solver_cache.get(ckey, 0)
    if solver == 0:
        problem = MddftProblem(list(src.shape), SW_INVERSE)
        solver = MddftSolver(problem, _solver_opts(src))
        _solver_cache[ckey] = solver
    result = solver.solve(make_complex128(src))
    return result

