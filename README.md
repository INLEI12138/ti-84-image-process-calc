# ti-84-image-process-calc — IMGGEO

**[中文](#中文说明) | [English](#english)**

A TI-84 Plus CE program for image geometry and multi-view computations: 2D transforms, building and solving `A·p = b` from point correspondences, camera projection matrices and plane homographies, essential/fundamental matrices and epipolar lines, decomposing `P` into `K, R, C`, RANSAC iteration counts, and SAD / SSD / ZNCC stereo matching costs.

一个 TI-84 Plus CE 程序，用来做图像几何和多视图几何的计算：二维变换、由对应点写出并求解 `A·p = b`、相机投影矩阵与平面单应、本质矩阵 / 基础矩阵与对极线、把 `P` 分解成 `K, R, C`、RANSAC 迭代次数，以及立体匹配的 SAD / SSD / ZNCC。

---

## 中文说明

### 安装

1. 在电脑上安装 [TI Connect CE](https://education.ti.com/en/products/computer-software/ti-connect-ce-sw)，用数据线连接计算器。
2. 先让计算器回到主屏幕（不要在运行任何程序）。否则会提示 *Calculator is Busy*。
3. TI Connect CE 菜单 **Actions → Add Files from Computer**，选择 `IMGGEO.8xp`，点 **Send**。
4. 计算器上按 `prgm`，选 `IMGGEO`，按 `enter` 运行。

建议确认能用之后在 `2nd` → `mem` → `Archive` 里归档，防止清内存时丢失。

### 输入小贴士

| 情况 | 怎么做 |
|---|---|
| 输入一行数（矩阵的一行、一个窗口） | 直接输 `4,0,0`，**不用**花括号 |
| 负数 | 用 `(-)` 键（在 `.` 旁边），**不要**用减号 `−` 键 |
| 中途退出 | 按 `on`，再选 `1:Quit` |
| 矩阵太宽看不全 | 显示时用左右方向键滚动 |
| 每一屏结果 | 按 `enter` 继续 |
| 角度 | 一律用**度**，逆时针为正（程序会自动切到 Degree 模式） |
| 结果 | 都是小数，例如 0.8660 = √3/2，0.7071 = √2/2 |

### 菜单结构

```
IMG GEOMETRY
1: 2D TRANSFORM      → TRANSLATION / EUCLIDEAN R+T / SIMILARITY R+S+T /
                       SCALE SX,SY + T / GENERAL R,S,T / BACK
2: DOF AND NOTES     → 自由度表、两视图单应成立条件、变换顺序、SIFT 步骤
3: PTS TO A,B,H      → AFFINE 6 UNK / HOMOGRAPHY 9 UNK /
                       SIMILARITY 4 UNK / TRANSLATE 2 UNK / BACK
4: CAMERA P AND H    → 相机 1 或 2：P、物体坐标下的 P̃、平面单应 H，投影点
5: EPIPOLAR E,F      → 用相机 1、2 的数据算 R、t、E、F 和对极线
6: APPLY H TO PT     → 任意 3×3 矩阵变换一个点
7: MORE TOOLS        → P TO K,R,C / RANSAC ITERATIONS / SAD SSD ZNCC /
                       BACK / QUIT
```

### 1. 2D TRANSFORM — 二维变换

约定：`H = Ht · Hs · Hr`，即**先旋转、再缩放、最后平移**。

先选类型，程序只问该类型需要的参数：

| 类型 | 要输入 | DOF |
|---|---|---|
| TRANSLATION | TX, TY | 2 |
| EUCLIDEAN R+T | 角度, TX, TY | 3 |
| SIMILARITY R+S+T | 角度, 统一缩放 S, TX, TY | 4 |
| SCALE SX,SY + T | SX, SY, TX, TY | 4 |
| GENERAL R,S,T | 角度, SX, SY, TX, TY | 5（一般仿射为 6） |

最后输入要变换的点 (X, Y)；只想看矩阵就输 0, 0。

依次显示：类型与 DOF → cos/sin → `HR` → `HS` → `HT` → `H` →（有缩放时）交换缩放和平移顺序后的矩阵，以及能否交换（`SO CANNOT SWAP S,T` / `SO CAN SWAP S,T`）→ 矩阵方程 `H*[X;Y;1] = [X2;Y2;1]` → `X2, Y2`。

例：选 EUCLIDEAN，角度 30，TX=2，TY=3，点 (1,2) → `X2=1.86603, Y2=5.23205`。

### 2. DOF AND NOTES — 速查

四页文字：各变换的自由度与最少点数；两视图之间存在单应的三种情况（平面场景 / 纯旋转 / 场景在无穷远）；矩阵乘法顺序；SIFT 主要步骤。

### 3. PTS TO A,B,H — 对应点 → 方程 A·p = b

| 模型 | 未知数 p | 每对点的两行 | b |
|---|---|---|---|
| AFFINE 6 UNK | a1…a6 | `[x y 1 0 0 0]`, `[0 0 0 x y 1]` | `(x', y')` |
| HOMOGRAPHY 9 UNK | h1…h9 | `[x y 1 0 0 0 −x'x −x'y −x']`, `[0 0 0 x y 1 −y'x −y'y −y']` | `0`（Σh²=1 形式） |
| SIMILARITY 4 UNK | a, b, tx, ty（H=[[a,−b,tx],[b,a,ty],[0,0,1]]） | `[x −y 1 0]`, `[y x 0 1]` | `(x', y')` |
| TRANSLATE 2 UNK | tx, ty | `[1 0]`, `[0 1]` | `(x'−x, y'−y)` |

输入：`NUM PTS=`（几对点），然后每对点输 `X, Y, X2, Y2`（X2、Y2 就是 x′、y′）。

- 每对点会显示 A 的两行和 b。
- 点数够了（仿射 3、单应 4、相似 2、平移 1）会自动求解（多于最少点数时用最小二乘），显示 `SOLVED P` 和 `SOLVED H`；单应还会额外给出 Σh²=1 归一化的 H。
- 点数不够就只显示方程，然后回到主菜单。

### 4. CAMERA P AND H — 相机投影矩阵与平面单应

约定：`P = K [R | t]`，`t = −R·C`。`R` 把**世界坐标方向转到相机坐标**，`C` 是相机中心在世界坐标里的位置。

输入顺序：

1. `CAMERA NO 1 OR 2=` — 存成相机 1 还是相机 2（供菜单 5 使用）。
2. K 的三行，例如 `4,0,0` / `0,4,0` / `0,0,1`。
3. 旋转 R：`NONE R=I`、绕 X / Y / Z 轴转某角度，或 `TYPE R ROWS` 手动输三行。
4. 相机中心 `POS X, Y, Z`（世界坐标）。题目只给 `t` 时，先换算 `C = −Rᵀt`。
5. 物体坐标系原点 `OX, OY, OZ`（世界坐标；坐标轴与世界坐标系平行）。不需要就输 0, 0, 0。

依次显示：`K` → `[R | t]` → `P` → `P̃`（物体坐标）→ `H = P̃ 的第 1、2、4 列` → H 归一化（h9=1）。

然后进入 `PROJECT POINT` 菜单：
- `WORLD PT VIA P`：输入世界点 (X, Y, Z) → 图像坐标和深度 W。
- `OBJ PT VIA H`：输入物体平面上的点 (P, Q)（z=0）→ 图像坐标。

例：K=diag(4,4,1)，R=I，C=(2,0,0)，物体原点 (0,0,10) → `P=[[4,0,0,−8],[0,4,0,0],[0,0,1,0]]`，`H=[[0.4,0,−0.8],[0,0.4,0],[0,0,1]]`。

### 5. EPIPOLAR E,F — 本质矩阵、基础矩阵、对极线

先用菜单 4 分别设好相机 1 和相机 2。程序计算：

```
R = R2·R1ᵀ,  t = t2 − R·t1      (相机 2 坐标 = R·相机 1 坐标 + t)
E = [t]× R
F = K2⁻ᵀ · E · K1⁻¹             (满足 p'ᵀ F p = 0)
```

然后输入相机 1 图像中的点 (x, y) → 相机 2 中的对极线 `a·x' + b·y' + c = 0`（并给出斜截式），再输入一个相机 2 中的点检验，结果为 0 表示在线上。E、F 都只确定到相差一个比例因子。

### 6. APPLY H TO PT

按行输入任意 3×3 矩阵，再反复输入点 (X, Y)，显示 `X2, Y2` 和齐次分量 W。

### 7. MORE TOOLS

**P TO K,R,C** — 按行输入 3×4 的 P，例如 `-1600,40,-640,6440`。输出：

- 相机中心 `C = −M⁻¹ p4`（M 是 P 的左 3×3 块，p4 是第 4 列）
- `K`（归一化 K33=1）及 fx, fy, skew, cx, cy
- `R = K⁻¹ M / λ`（det R = +1）和比例 λ

**RANSAC ITERATIONS** — 输入外点比例（如 0.25）、最小样本数 s、置信度 p（如 0.99）：

```
N ≥ log(1 − p) / log(1 − wˢ),  w = 1 − 外点比例
```

屏幕会先提示常用的 s：平移 1、相似 2、仿射 3、单应 4、F 7（8 点法 8）。

**SAD SSD ZNCC** — 左窗口一行输完（如 `10,20,30,20`），右窗口同样输完，显示：

```
SAD  = Σ|L − R|                         越小越好
SSD  = Σ(L − R)²                        越小越好
ZNCC = Σ(L−L̄)(R−R̄) / √(Σ(L−L̄)² Σ(R−R̄)²)   越大越好（对亮度增益和偏移不变）
```

选 `ANOTHER RIGHT` 可以接着比下一个候选窗口，左窗口不用重输。窗口长度任意（2D 窗口按行展开），左右长度必须相同。

### 会被覆盖的变量

运行时会使用并覆盖：实数变量 A–Z、θ，矩阵 `[A]`–`[J]`，列表 `L1`–`L4`，字符串 `Str1`。相机 1 存在 `[A]`(K)、`[E]`([R|t])、`[C]`(P)；相机 2 存在 `[B]`、`[F]`、`[D]`。这些在退出程序后仍保留，直到重新设置相机或清内存。

### 限制

- 没有符号运算，所有结果都是小数。
- 绕轴旋转只有 X / Y / Z 三种，其他 R 用 `TYPE R ROWS` 手动输入。
- 物体坐标系只支持平移（坐标轴与世界坐标系平行）。

### 从源码构建

`IMGGEO.txt` 是可读的源码（`->` 表示 →，`~` 表示负号 ⁻，`^-1`、`^T`、`!=`、`<=`、`>Frac` 等见 `tools/build8xp.py` 的符号表）。

```bash
python tools/build8xp.py IMGGEO.txt IMGGEO.8xp   # 生成 .8xp
python tools/test_examples.py                    # 在电脑上用模拟器跑示例
```

`tools/sim.py` 是一个只支持本程序用到的语句的 TI-BASIC 小模拟器，测不出计算器本身的限制（例如 `Menu(` 最多 7 项、矩阵不能直接除以数）。

---

## English

### Install

1. Install [TI Connect CE](https://education.ti.com/en/products/computer-software/ti-connect-ce-sw) and connect the calculator by USB.
2. Put the calculator on the home screen (no program running), otherwise you get *Calculator is Busy*.
3. In TI Connect CE: **Actions → Add Files from Computer**, choose `IMGGEO.8xp`, click **Send**.
4. On the calculator press `prgm`, pick `IMGGEO`, press `enter`.

Once it works, archive it (`2nd` → `mem` → `Archive`) so a RAM clear does not delete it.

### Input tips

| Situation | What to do |
|---|---|
| A row of numbers (a matrix row, a window) | Type `4,0,0` — **no braces** needed |
| Negative numbers | Use the `(-)` key, **not** the `−` subtract key |
| Leave the program | Press `on`, then `1:Quit` |
| Matrix too wide | Scroll with the left/right arrows |
| Each result screen | Press `enter` to continue |
| Angles | Degrees, counter-clockwise positive (the program switches to Degree mode) |
| Results | Decimals, e.g. 0.8660 = √3/2, 0.7071 = √2/2 |

### Menu

```
IMG GEOMETRY
1: 2D TRANSFORM      → TRANSLATION / EUCLIDEAN R+T / SIMILARITY R+S+T /
                       SCALE SX,SY + T / GENERAL R,S,T / BACK
2: DOF AND NOTES     → DOF table, when two views are related by a homography,
                       transform order, SIFT steps
3: PTS TO A,B,H      → AFFINE 6 UNK / HOMOGRAPHY 9 UNK /
                       SIMILARITY 4 UNK / TRANSLATE 2 UNK / BACK
4: CAMERA P AND H    → camera 1 or 2: P, object-frame P̃, plane homography H, projections
5: EPIPOLAR E,F      → R, t, E, F and epipolar lines from cameras 1 and 2
6: APPLY H TO PT     → map a point with any 3×3 matrix
7: MORE TOOLS        → P TO K,R,C / RANSAC ITERATIONS / SAD SSD ZNCC /
                       BACK / QUIT
```

### 1. 2D TRANSFORM

Convention: `H = Ht · Hs · Hr` — **rotate first, then scale, then translate**.

Pick a type; only the needed parameters are asked:

| Type | Inputs | DOF |
|---|---|---|
| TRANSLATION | TX, TY | 2 |
| EUCLIDEAN R+T | angle, TX, TY | 3 |
| SIMILARITY R+S+T | angle, uniform scale S, TX, TY | 4 |
| SCALE SX,SY + T | SX, SY, TX, TY | 4 |
| GENERAL R,S,T | angle, SX, SY, TX, TY | 5 (general affine is 6) |

Then enter the point (X, Y); use 0, 0 if you only need the matrices.

Screens: type & DOF → cos/sin → `HR` → `HS` → `HT` → `H` → (when scaling is present) the matrix with scale and translation swapped plus a verdict (`SO CANNOT SWAP S,T` / `SO CAN SWAP S,T`) → the matrix equation `H*[X;Y;1] = [X2;Y2;1]` → `X2, Y2`.

Example: EUCLIDEAN, angle 30, TX=2, TY=3, point (1,2) → `X2=1.86603, Y2=5.23205`.

### 2. DOF AND NOTES

Four text pages: DOF and minimum correspondences per transform; the three cases where two views are related by a homography (planar scene / pure rotation / scene at infinity); multiplication order; main SIFT steps.

### 3. PTS TO A,B,H — correspondences → A·p = b

| Model | Unknowns p | Two rows per pair | b |
|---|---|---|---|
| AFFINE 6 UNK | a1…a6 | `[x y 1 0 0 0]`, `[0 0 0 x y 1]` | `(x', y')` |
| HOMOGRAPHY 9 UNK | h1…h9 | `[x y 1 0 0 0 −x'x −x'y −x']`, `[0 0 0 x y 1 −y'x −y'y −y']` | `0` (Σh²=1 form) |
| SIMILARITY 4 UNK | a, b, tx, ty (H=[[a,−b,tx],[b,a,ty],[0,0,1]]) | `[x −y 1 0]`, `[y x 0 1]` | `(x', y')` |
| TRANSLATE 2 UNK | tx, ty | `[1 0]`, `[0 1]` | `(x'−x, y'−y)` |

Enter `NUM PTS=` and then `X, Y, X2, Y2` for each pair (X2, Y2 = x′, y′).

- The two rows of A and the b entries are shown for every pair.
- With enough pairs (affine 3, homography 4, similarity 2, translation 1) it solves the system (least squares if over-determined) and shows `SOLVED P` and `SOLVED H`; for a homography it also shows H scaled to Σh²=1.
- With fewer pairs it only shows the equations.

### 4. CAMERA P AND H

Convention: `P = K [R | t]`, `t = −R·C`. `R` maps **world directions into camera coordinates**; `C` is the camera center in world coordinates.

Inputs:

1. `CAMERA NO 1 OR 2=` — slot to store this camera (used by menu 5).
2. The three rows of K, e.g. `4,0,0` / `0,4,0` / `0,0,1`.
3. Rotation R: `NONE R=I`, about the X / Y / Z axis by an angle, or `TYPE R ROWS`.
4. Camera center `POS X, Y, Z` in world coordinates. If only `t` is given, convert with `C = −Rᵀt`.
5. Object-frame origin `OX, OY, OZ` in world coordinates (axes parallel to the world axes). Use 0, 0, 0 if not needed.

Screens: `K` → `[R | t]` → `P` → `P̃` (object frame) → `H = columns 1, 2, 4 of P̃` → H normalized so h9 = 1.

Then the `PROJECT POINT` menu:
- `WORLD PT VIA P`: world point (X, Y, Z) → image coordinates and depth W.
- `OBJ PT VIA H`: object-plane point (P, Q) with z = 0 → image coordinates.

Example: K = diag(4,4,1), R = I, C = (2,0,0), object origin (0,0,10) → `P = [[4,0,0,−8],[0,4,0,0],[0,0,1,0]]`, `H = [[0.4,0,−0.8],[0,0.4,0],[0,0,1]]`.

### 5. EPIPOLAR E,F

Set up cameras 1 and 2 in menu 4 first. The program computes

```
R = R2·R1ᵀ,  t = t2 − R·t1      (camera-2 coords = R·camera-1 coords + t)
E = [t]× R
F = K2⁻ᵀ · E · K1⁻¹             (so that p'ᵀ F p = 0)
```

Then enter a camera-1 image point (x, y) to get the camera-2 epipolar line `a·x' + b·y' + c = 0` (also in slope-intercept form), and a camera-2 point to check: 0 means it lies on the line. E and F are defined up to scale.

### 6. APPLY H TO PT

Enter any 3×3 matrix row by row, then points (X, Y); shows `X2, Y2` and the homogeneous W.

### 7. MORE TOOLS

**P TO K,R,C** — enter the 3×4 P row by row, e.g. `-1600,40,-640,6440`. Output:

- camera center `C = −M⁻¹ p4` (M = left 3×3 block, p4 = 4th column)
- `K` normalized to K33 = 1, plus fx, fy, skew, cx, cy
- `R = K⁻¹ M / λ` (det R = +1) and the scale λ

**RANSAC ITERATIONS** — outlier fraction (e.g. 0.25), minimum sample size s, confidence p (e.g. 0.99):

```
N ≥ log(1 − p) / log(1 − wˢ),  w = 1 − outlier fraction
```

The screen lists common s values: translation 1, similarity 2, affine 3, homography 4, F 7 (8 for the 8-point algorithm).

**SAD SSD ZNCC** — type the whole left window on one line (e.g. `10,20,30,20`), then the right window:

```
SAD  = Σ|L − R|                         lower is better
SSD  = Σ(L − R)²                        lower is better
ZNCC = Σ(L−L̄)(R−R̄) / √(Σ(L−L̄)² Σ(R−R̄)²)   higher is better (invariant to gain and offset)
```

`ANOTHER RIGHT` compares the next candidate without re-typing the left window. Any window length works (flatten 2D windows row by row); left and right must have the same length.

### Variables overwritten

Real variables A–Z and θ, matrices `[A]`–`[J]`, lists `L1`–`L4`, and `Str1`. Camera 1 is stored in `[A]` (K), `[E]` ([R|t]), `[C]` (P); camera 2 in `[B]`, `[F]`, `[D]`. They persist after the program exits until you set the camera again or clear RAM.

### Limitations

- No symbolic math; all results are decimals.
- Built-in rotations are about X, Y or Z only; enter any other R with `TYPE R ROWS`.
- The object frame supports translation only (axes parallel to the world axes).

### Build from source

`IMGGEO.txt` is readable source (`->` is →, `~` is the negative sign ⁻; see the token table in `tools/build8xp.py` for `^-1`, `^T`, `!=`, `<=`, `>Frac`, …).

```bash
python tools/build8xp.py IMGGEO.txt IMGGEO.8xp   # build the .8xp
python tools/test_examples.py                    # run worked examples in the PC simulator
```

`tools/sim.py` is a tiny TI-BASIC simulator that only understands the statements this program uses. It cannot catch calculator-only limits (e.g. `Menu(` shows at most 7 items; a matrix cannot be divided by a number).

---

by INLEI
