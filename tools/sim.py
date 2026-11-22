"""Tiny TI-BASIC subset simulator used to test IMGGEO.txt on a PC.

It only understands the statements IMGGEO uses. It cannot catch calculator-only
limits (e.g. Menu( shows at most 7 items, matrix / scalar is not allowed).
"""
import re, math, sys
import numpy as np

class Mat:
    def __init__(s, a): s.a = np.array(a, dtype=float)
    def __call__(s, r, c): return s.a[int(r)-1, int(c)-1]
    def __mul__(s, o):
        if isinstance(o, Mat):
            assert s.a.shape[1] == o.a.shape[0], f"DIM MISMATCH {s.a.shape}*{o.a.shape}"
            return Mat(s.a @ o.a)
        return Mat(s.a * o)
    __rmul__ = lambda s, o: Mat(s.a * o)
    def __add__(s, o): assert s.a.shape == o.a.shape; return Mat(s.a + o.a)
    def __sub__(s, o): assert s.a.shape == o.a.shape, "DIM MISMATCH -"; return Mat(s.a - o.a)
    def __truediv__(s, o): return Mat(s.a / o)
    def __neg__(s): return Mat(-s.a)
    @property
    def T(s): return Mat(s.a.T)
    @property
    def inv(s): return Mat(np.linalg.inv(s.a))
    def __repr__(s): return str(np.round(s.a, 5))

class LST(np.ndarray):
    def __new__(cls, x): return np.asarray(x, dtype=float).view(cls)
    def __call__(s, i): return float(s[int(i)-1])

def tround(x, n):
    if isinstance(x, Mat): return Mat(np.round(x.a, int(n)))
    if isinstance(x, np.ndarray): return np.round(x, int(n))
    return round(x, int(n))

def conv(e):
    e = e.replace('θ', 'TH')
    e = re.sub(r'\[\[(.*?)\]\]', lambda m: 'Mat([[' + m.group(1).replace('][', '],[') + ']])', e)
    e = re.sub(r'\[([A-J])\]', r'M_\1', e)
    e = e.replace('^T', '.T').replace('^-1', '.inv').replace('^2', '**2').replace('^', '**')
    e = e.replace('~', '-').replace('!=', '<>')
    e = re.sub(r'(?<![<>!])=', '==', e).replace('<>', '!=')
    e = re.sub(r'\{([^{}]*)\}', r'LST([\1])', e)
    e = re.sub(r'(?<![A-Za-z_\d.])(\d+)([A-Za-z(])', r'\1*\2', e)
    e = e.replace('sqrt(', 'math.sqrt(')
    return e

s_env_holder=[None]
class Sim:
    def __init__(s, src, inputs, menus):
        s.lines = [l for l in src.split('\n')]
        s.inputs = list(inputs); s.menus = list(menus); s.out = []
        s.env = dict(Mat=Mat, LST=LST, math=math, np=np,
                     sin=lambda d: math.sin(math.radians(d)), cos=lambda d: math.cos(math.radians(d)),
                     round=tround, identity=lambda n: Mat(np.eye(int(n))),
                     augment=lambda a, b: Mat(np.hstack([a.a, b.a])), dim=lambda x: len(x), abs=lambda x: np.abs(x) if isinstance(x,np.ndarray) else abs(x), det=lambda m: np.linalg.det(m.a), log=math.log10, int=math.floor, sum=lambda x: float(np.sum(x)), mean=lambda x: float(np.mean(x)), expr=lambda st: eval(conv(st), s_env_holder[0]))
        s_env_holder[0]=s.env
        s.labels = {l[4:].strip(): i for i, l in enumerate(s.lines) if l.startswith('Lbl ')}
    def ev(s, e): return eval(conv(e), s.env)
    def store(s, val, tgt):
        tgt = tgt.replace('θ', 'TH')
        m = re.fullmatch(r'\[([A-J])\]\((.+),(.+)\)', tgt)
        if m:
            M = s.env['M_' + m.group(1)]; r, c = int(s.ev(m.group(2))), int(s.ev(m.group(3)))
            assert 1 <= r <= M.a.shape[0] and 1 <= c <= M.a.shape[1], f"ERR:INVALID DIM {tgt}"
            M.a[r-1, c-1] = val; return
        m = re.fullmatch(r'dim\(\[([A-J])\]\)', tgt)
        if m:
            k = 'M_' + m.group(1); r, c = int(val[0]), int(val[1])
            old = s.env.get(k, Mat(np.zeros((0, 0)))).a
            new = np.zeros((r, c)); rr, cc = min(r, old.shape[0]), min(c, old.shape[1])
            new[:rr, :cc] = old[:rr, :cc]; s.env[k] = Mat(new); return
        m = re.fullmatch(r'\[([A-J])\]', tgt)
        if m: s.env['M_' + m.group(1)] = Mat(val.a.copy()); return
        s.env[tgt] = val
    def skip_block(s, i):
        # i points after Then/Else; skip to matching End or Else (depth-aware)
        d = 0
        while True:
            l = s.lines[i]
            if l == 'Then' or l.startswith('For('): d += 1
            if l == 'End':
                if d == 0: return i, 'End'
                d -= 1
            if l == 'Else' and d == 0: return i, 'Else'
            i += 1
    def run(s, maxsteps=200000):
        i = 0; stack = []; steps = 0
        while i < len(s.lines):
            steps += 1; assert steps < maxsteps
            l = s.lines[i]
            if l in ('', 'Degree', 'ClrHome') or l.startswith('Lbl '): i += 1; continue
            if l == 'Stop': return
            if l.startswith('Goto '): i = s.labels[l[5:]]; continue
            if l.startswith('Menu('):
                parts = [p.strip() for p in re.findall(r'"[^"]*"|[^,()]+', l[5:-1])]
                opts = {parts[k].strip('"'): parts[k+1] for k in range(1, len(parts), 2)}
                ch = s.menus.pop(0); s.out.append(f'[MENU {parts[0]} -> {ch}]')
                i = s.labels[opts[ch]]; continue
            if l.startswith('Input '):
                m = re.fullmatch(r'Input "(.*)",(.+)', l)
                v = s.inputs.pop(0); s.out.append(f'{m.group(1)}{v}')
                s.store(v if m.group(2)=='Str1' else s.ev(v), m.group(2)); i += 1; continue
            if l.startswith('Disp ') or l.startswith('Pause'):
                arg = l[5:].strip() if l.startswith('Disp') else l[6:].strip()
                if arg:
                    for p in split_args(arg):
                        if p.startswith('"'): s.out.append(p.strip('"'))
                        elif p.endswith('>Frac'): s.out.append(frac(s.ev(p[:-5])))
                        else: s.out.append(repr(s.ev(p)))
                i += 1; continue
            if l.startswith('Fill('):
                v, t = l[5:-1].split(','); s.env['M_' + t[1]].a[:] = s.ev(v); i += 1; continue
            if l.startswith('For('):
                var, a, b = l[4:-1].split(',')
                s.env[var] = s.ev(a); stack.append(('for', i, var, b)); i += 1; continue
            if l == 'End':
                top = stack[-1]
                if top[0] == 'for':
                    _, j, var, b = top; s.env[var] += 1
                    if s.env[var] <= s.ev(b): i = j + 1; continue
                    stack.pop(); i += 1; continue
                stack.pop(); i += 1; continue
            if l == 'Else':  # reached end of true branch
                j, _ = s.skip_block(i + 1); stack.pop(); i = j + 1; continue
            if l.startswith('If '):
                c = s.ev(l[3:])
                if s.lines[i+1] == 'Then':
                    if c: stack.append(('if',)); i += 2
                    else:
                        j, kind = s.skip_block(i + 2)
                        if kind == 'Else': stack.append(('if',))
                        i = j + 1
                    continue
                i += 1 if c else 2; continue
            if '->' in l:
                e, t = l.rsplit('->', 1); s.store(s.ev(e), t); i += 1; continue
            raise Exception('unknown ' + l)

from fractions import Fraction
def f1(x):
    f=Fraction(float(x)).limit_denominator(9999)
    return str(f) if abs(float(f)-x)<1e-9 else f'{x:.10g}'
def frac(v):
    if isinstance(v, Mat): return '\n'.join('['+'  '.join(f1(x) for x in r)+']' for r in v.a)
    if isinstance(v, list): return '{'+' '.join(f1(x) for x in v)+'}'
    return f1(v)
def split_args(a):
    out, d, q, cur = [], 0, False, ''
    for ch in a:
        if ch == '"': q = not q
        if not q and ch in '([{': d += 1
        if not q and ch in ')]}': d -= 1
        if ch == ',' and d == 0 and not q: out.append(cur); cur = ''
        else: cur += ch
    out.append(cur); return out
