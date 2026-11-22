"""Run IMGGEO.txt through the PC simulator with worked examples.

usage:  python tools/test_examples.py
Each case feeds menu choices and inputs, then checks the key numbers.
"""
import os
import sys

import warnings

import numpy as np

warnings.filterwarnings('ignore')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sim import Sim  # noqa: E402

SRC = open(os.path.join(HERE, '..', 'IMGGEO.txt'), encoding='utf-8').read()
K = ['4,0,0', '0,4,0', '0,0,1']


def run(inputs, menus):
    s = Sim(SRC, inputs, menus)
    s.run()
    assert not s.inputs and not s.menus, 'unused inputs/menus left over'
    return s.out


def nums(out):
    vals = []
    for o in out:
        try:
            vals.append(float(eval(o, {'np': np})))
        except Exception:
            pass
    return vals


def close(a, b):
    return abs(a - b) < 1e-4


CASES = []


def case(fn):
    CASES.append(fn)
    return fn


@case
def euclidean_rotate30_translate():
    out = run(['30', '2', '3', '1', '2'], ['2D TRANSFORM', 'EUCLIDEAN R+T', 'MORE TOOLS', 'QUIT'])
    v = nums(out)
    assert close(v[-2], 1.86603) and close(v[-1], 5.23205)


@case
def scale_translate_swap_check():
    out = run(['2', '3', '1', '4', '2', '3'], ['2D TRANSFORM', 'SCALE SX,SY + T', 'MORE TOOLS', 'QUIT'])
    assert 'SO CANNOT SWAP S,T' in out
    v = nums(out)
    assert close(v[-2], 5) and close(v[-1], 13)


@case
def affine_rows():
    out = run(['1', '1', '2', '3', '4'], ['PTS TO A,B,H', 'AFFINE 6 UNK', 'MORE TOOLS', 'QUIT'])
    assert 'LST([1., 2., 1., 0., 0., 0.])' in out
    assert 'LST([0., 0., 0., 1., 2., 1.])' in out
    assert 'LST([3., 4.])' in out


@case
def homography_solve_4pts():
    H = np.array([[2, 1, 3], [0, 1, -1], [0.1, 0.2, 1]])
    inp = ['4']
    for x, y in [(0, 0), (1, 0), (0, 1), (1, 1)]:
        w = H @ [x, y, 1]
        inp += [str(x), str(y), repr(w[0] / w[2]), repr(w[1] / w[2])]
    out = run(inp, ['PTS TO A,B,H', 'HOMOGRAPHY 9 UNK', 'MORE TOOLS', 'QUIT'])
    assert any('0.1  0.2  1.' in o for o in out)


@case
def two_cameras_and_epipolar_line():
    inp = (['1'] + K + ['0', '0', '0', '0', '0', '10', '1', '3', '10'] +
           ['2'] + K + ['2', '0', '0', '0', '0', '10', '0.4', '1.2', '-0.4', '1.2'])
    menus = ['CAMERA P AND H', 'NONE R=I', 'WORLD PT VIA P', 'MAIN MENU',
             'CAMERA P AND H', 'NONE R=I', 'MAIN MENU',
             'EPIPOLAR E,F', 'MAIN MENU', 'MORE TOOLS', 'QUIT']
    out = run(inp, menus)
    i = out.index('A*X2+B*Y2+C=')
    assert close(float(eval(out[i + 1], {'np': np})), 0)


@case
def decompose_P():
    out = run(['-1600,40,-640,6440', '0,2000,-480,4400', '0,0,-2,10'],
              ['MORE TOOLS', 'P TO K,R,C', 'MORE TOOLS', 'QUIT'])
    assert any('800.' in o and '320.' in o for o in out)
    assert any('2. -1.  5.' in o for o in out)


@case
def ransac_iterations():
    out = run(['.25', '3', '.99'], ['MORE TOOLS', 'RANSAC ITERATIONS', 'MORE TOOLS', 'QUIT'])
    assert close(nums(out)[-1], 9)


@case
def stereo_costs():
    out = run(['10,20,30,20', '12,19,29,22'], ['MORE TOOLS', 'SAD SSD ZNCC', 'MAIN MENU', 'MORE TOOLS', 'QUIT'])
    v = nums(out)
    assert close(v[0], 6) and close(v[1], 10) and close(v[2], 0.98478)


if __name__ == '__main__':
    bad = 0
    for fn in CASES:
        try:
            fn()
            print('PASS', fn.__name__)
        except Exception as e:  # noqa: BLE001
            bad += 1
            print('FAIL', fn.__name__, repr(e))
    sys.exit(1 if bad else 0)
