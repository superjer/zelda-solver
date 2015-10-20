import sys
from collections import namedtuple

hyrule = """\
                                                                 \
                                             .l. <.._...     ... \
                                             .5W .F. ...     .C. \
                                              V   |   |       |  \
                     ..._<.._<.._<.._<.._<.._<..<<.._..._..._... \
                     ... ... ... ... ... ... ... ... .+. ... ... \
                      |       |                   |   |          \
 ..._... bal ..._..._... <.._<.._.f._..._..._..._..._..._... .r. \
 ... .S. .6. .+. .P. .A. .M. ... .T. ... ... ... .H. .T. ... .H. \
  |   |   |   |       |   |       |       |   |       |   |   |  \
 ..._..._..._... ... <.._... ..._...     ..._... ... ... <.._... \
 ... ... ... ... DM. ... ... .1B ...     ... ... .2. .T. ... ... \
  |   |           |               |       |   |   |   |       |  \
 ..._... mwl     ... .r. .f._.f._.f. ..._..._... ..._.f.     <.. \
 ... ... .7F     .A. .4L .M. .H. .T. .+. .A. ... ... .M.     ... \
  |       |       |   |   |       |   |       |       |       |  \
 ... <.._..._..._..._..._.f._..._..._..._..._..._..._..._... <l. \
 ... ... ... ... ... ... .X. ... ... ... ... ... ... ... .F. .H. \
  |   V   |   |   |   |           |   |       |   |   |       |  \
 <..>..._.f._..._..._..._..._..._..._..._..._.f. ..._.f._..._... \
 ... ... .C. ... ... ... .F. .T. ... ... ... .C. ... .8. ... .A. \
      ^   |   |       |   |   |   |           |               |  \
     ..._..._..._... <.._<.._..._..._..._..._..._..._..._..._... \
     .T* ... ..* .3R ... ... .$. ... .+. ... .H* ... ... ... ... \
                                                                 \
"""

level_money = [0, 10, 25, 5, 15, 0, 0, 0, 0]

legend = """
1-8 lvls
S   magical
H   heart
X   10
T   30
C   100 
+   take any road
P   power bracelet
A   arrow (80)
M   meat (100)
D   discount
w   need whistle
f   need fire
r   need raft
l   need ladder
a   need arrow
b   need bow
m   need meat
<   scrollable left
>   scrollable right
$   start
*   warp to start
"""

colors = [
    0xd8,0xcc,0xc5,0xc4,0xa0,0x7c,0x82,0x88,0x6a,0x46,0x22,
    0x1d,0x18,0x13,0x15,0x39,0x5d,0x81,0xa5,0xc8,0xcd,0xd3
]

needs = 'wfrlabm'
items = 'WFRLABM'
nodes = []
start_nr = 0
pois = []
warps = [0] * 9
roads = []

class Node:
    lvl=0
    need=0
    item=0
    money=0
    heart=False
    scrl=False
    scrr=False
    up=False
    down=False
    left=False
    right=False
    road=False
    discount=False
    links=None

    def __init__(self):
        self.links = []

    def __str__(self):
        return ' '.join([
            str(self.lvl),
            str(self.need),
            str(self.item),
            str(self.money),
        ])

class State:
    visited = None
    backlinks = None
    items = 0
    lvls = None

    def __init__(self):
        self.visited = [9999] * 128
        self.backlinks = [False] * 128
        self.lvls = []

for y in range(0,8):
    for x in range(0,16):
        node_nr = y * 16 + x
        pos = 66 + y * 65 * 3 + x * 4
        flags = hyrule[pos:pos+3] + hyrule[pos+65:pos+68]
        up = hyrule[pos - 64]
        down = hyrule[pos + 65 + 66]
        left = hyrule[pos - 1]
        right = hyrule[pos + 3]

        node = Node()

        for i in range(0,6):
            f = flags[i]
            if f >= '1' and f <= '8':
                node.lvl = int(f)
                node.money = level_money[node.lvl]
            elif f in needs:
                node.need |= 2 ** needs.index(f)
            elif f in items:
                node.item |= 2 ** items.index(f)
            elif f == 'X':
                node.money = 10
            elif f == 'T':
                node.money = 30
            elif f == 'C':
                node.money = 100
            elif f == 'H':
                node.heart = True
            elif f == '<':
                node.scrl = True
            elif f == '>':
                node.scrr = True
            elif f == '+':
                node.road = True
                roads.append(node_nr)
            elif f == 'D':
                node.discount = True
            elif f == '$':
                start_nr = node_nr

        if up in '|^':
            node.links.append(node_nr - 16)

        if down in '|V':
            node.links.append(node_nr + 16)

        if left in '_<' or node.scrl:
            node.links.append(node_nr - 1)

        if right in '_>' or node.scrr:
            node.links.append(node_nr + 1)

        if node.lvl > 0 or node.item > 0 or node.heart or node.money > 0:
            pois.append(node_nr)

        nodes.append(node)

def statout(state, path=[]):
    for i, node in enumerate(nodes):
        if i not in path:
            sys.stdout.write("\x1B[38;5;236m")
        elif state.visited[i] < 9999:
            sys.stdout.write("\x1B[38;5;" + str(colors[state.visited[i]]) + "m")
        else:
            sys.stdout.write("\x1B[0m")

        if node.lvl > 0:
            sys.stdout.write(str(node.lvl))
        elif node.item & 2:
            sys.stdout.write('f')
        elif node.item & 16:
            sys.stdout.write('a')
        elif node.item & 64:
            sys.stdout.write('m')
        elif node.heart:
            sys.stdout.write('H')
        elif node.road:
            sys.stdout.write('+')
        elif i == start_nr:
            sys.stdout.write('$')
        else:
            sys.stdout.write('.')

        if i % 16 == 15:
            sys.stdout.write('\n')
    sys.stdout.write("[0m\n")

def flood(state, cur, prev, step):
    if state.visited[cur] <= step:
        return
    state.visited[cur] = step
    state.backlinks[cur] = prev

    for x in nodes[cur].links:
        flood(state, x, cur, step+1)

def shortest(state, cur):
    out = []
    while state.visited[cur] > 0:
        out.append(cur)
        cur = state.backlinks[cur]
    return out
    
state = State()
flood(state, start_nr, 0, 0)
path = shortest(state, pois[3])
print path

statout(state, path)
