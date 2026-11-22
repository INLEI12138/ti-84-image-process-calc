"""Tokenize IMGGEO.txt into a TI-84 Plus CE .8xp program."""
import sys

T = {
    '->': b'\x04', '^': b'\xf0', 'log(': b'\xc0', 'int(': b'\xb1', 'sum(': b'\xb6', 'det(': b'\xb3', 'mean(': b'\x21', 'Str1': b'\xaa\x00', 'expr(': b'\xbb\x2a', '>Frac': b'\x03', ' or ': b'\x3c', 'abs(': b'\xb2', '[': b'\x06', ']': b'\x07', '{': b'\x08', '}': b'\x09',
    '^-1': b'\x0c', '^2': b'\x0d', '^T': b'\x0e',
    '(': b'\x10', ')': b'\x11', 'round(': b'\x12', 'augment(': b'\x14',
    ' ': b'\x29', '"': b'\x2a', ',': b'\x2b', '.': b'\x3a', '\n': b'\x3f',
    ' and ': b'\x40', 'θ': b'\x5b',
    'Degree': b'\x65', '=': b'\x6a', '<': b'\x6b', '>': b'\x6c', '!=': b'\x6f', '<=': b'\x6d', '>=': b'\x6e',
    '+': b'\x70', '-': b'\x71', '*': b'\x82', '/': b'\x83', '|': None,
    '~': b'\xb0', 'identity(': b'\xb4', 'dim(': b'\xb5', 'sqrt(': b'\xbc',
    'sin(': b'\xc2', 'cos(': b'\xc4',
    'If ': b'\xce', 'Then': b'\xcf', 'Else': b'\xd0', 'For(': b'\xd3', 'End': b'\xd4',
    'Lbl ': b'\xd6', 'Goto ': b'\xd7', 'Pause ': b'\xd8', 'Pause': b'\xd8', 'Stop': b'\xd9',
    'Input ': b'\xdc', 'Disp ': b'\xde', 'ClrHome': b'\xe1', 'Fill(': b'\xe2', 'Menu(': b'\xe6',
}
for i, c in enumerate('ABCDEFGHIJ'):
    T[f'[{c}]'] = b'\x5c' + bytes([i])
for i in range(6):
    T[f'L{i+1}'] = b'\x5d' + bytes([i])
for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
    T[c] = bytes([ord(c)])
for c in '0123456789':
    T[c] = bytes([0x30 + int(c)])
T = {k: v for k, v in T.items() if v is not None}
KEYS = sorted(T, key=len, reverse=True)


def tokenize(src):
    out = bytearray(); i = 0; line = 1
    while i < len(src):
        for k in KEYS:
            if src.startswith(k, i):
                out += T[k]; i += len(k)
                if k == '\n': line += 1
                break
        else:
            raise SystemExit(f'line {line}: cannot tokenize {src[i:i+20]!r}')
    return bytes(out)


def build(name, tokens, comment=b'IMGGEO by INLEI'):
    body = len(tokens).to_bytes(2, 'little') + tokens
    nm = name.encode().ljust(8, b'\0')
    entry = (b'\x0d\x00' + len(body).to_bytes(2, 'little') + b'\x05' + nm + b'\x00\x00'
             + len(body).to_bytes(2, 'little') + body)
    hdr = b'**TI83F*\x1a\x0a\x00' + comment.ljust(42, b'\0')
    chk = (sum(entry) & 0xffff).to_bytes(2, 'little')
    return hdr + len(entry).to_bytes(2, 'little') + entry + chk


if __name__ == '__main__':
    # usage: python tools/build8xp.py [IMGGEO.txt] [IMGGEO.8xp]
    inp = sys.argv[1] if len(sys.argv) > 1 else 'IMGGEO.txt'
    outp = sys.argv[2] if len(sys.argv) > 2 else 'IMGGEO.8xp'
    src = open(inp, encoding='utf-8').read().rstrip('\n')
    lines = [l.rstrip() if not l.startswith('Pause') else l for l in src.split('\n')]
    tok = tokenize('\n'.join(lines))
    data = build('IMGGEO', tok)
    open(outp, 'wb').write(data)
    print('tokens', len(tok), 'file', len(data))
