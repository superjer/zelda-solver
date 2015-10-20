import sys
import random

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

needbits = 'wfrlabm'
itembits = 'WFRLABM'
nodes = []
start_nr = 0
poi_list = []
warps = [0] * 9
roads = []

# changey things
pois = []
lvls = None
items = 0
hearts = 3
#budget = 200
#wallet = 10
lunk = 0
sequence = None
distance = 0
report = ""

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

class State:
    visited = None
    backlinks = None

    def __init__(self):
        self.visited = [9999] * 128
        self.backlinks = [False] * 128

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
                warps[node.lvl] = node_nr
            elif f in needbits:
                node.need |= 2 ** needbits.index(f)
            elif f in itembits:
                node.item |= 2 ** itembits.index(f)
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

        if node.lvl > 0 or node.item > 0 or node.heart:
            poi_list.append(node_nr)

        nodes.append(node)

def node2chr(node):
    if node.lvl > 0:
        return str(node.lvl)
    elif node.item & 2:
        return 'f'
    elif node.item & 16:
        return 'a'
    elif node.item & 64:
        return 'm'
    elif node.money == 10:
        return 'X'
    elif node.money == 30:
        return 'T'
    elif node.money == 100:
        return 'C'
    elif node.heart:
        return 'H'
    elif node.road:
        return '+'
    else:
        return '.'

def statout(state, path=[]):
    out = ""
    for i, node in enumerate(nodes):
        if i not in path:
            out += "\x1B[38;5;236m"
        elif state.visited[i] < 9999:
            out += "\x1B[38;5;" + str(colors[state.visited[i]]) + "m"
        else:
            out += "\x1B[0m"

        if i == start_nr:
            out += "$"
        else:
            out += node2chr(node)

        if i % 16 == 15:
            out += "\n"
    out += "[0m"
    return out

def flood(state, cur, prev, step):
    if state.visited[cur] <= step:
        return
    state.visited[cur] = step
    state.backlinks[cur] = prev

    for x in nodes[cur].links:
        flood(state, x, cur, step+1)

    if step == 0 and items & 1: # whistle warps
        for x in lvls:
            flood(state, warps[x], cur, step+1)

def shortest(state, cur):
    out = []
    while state.visited[cur] > 0:
        out.append(cur)
        cur = state.backlinks[cur]
    return out

best = 9999

while True:
    pois[:] = poi_list
    lvls = []
    items = 0
    hearts = 3
    #budget = 200
    #wallet = 10
    lunk = start_nr
    sequence = []
    distance = 0
    report = ""

    while len(lvls) < 8:
        # choose a destination
        random.shuffle(pois)
        found = False
        for rot in range(0, len(pois)):
            node = nodes[pois[-1]]

            # wfrlabm
            if node.lvl == 0 and node.item & 2:
                cost = 60
            elif node.item & 16:
                cost = 80
            elif node.item & 64:
                cost = 60 if node.discount else 100
            else:
                cost = 0

            # if node.lvl == 0 and node.money > 0 and wallet >= budget:
            #     # too much money
            #     pass
            # if cost > wallet:
            #     # not enough money
            #     pass
            if node.heart and hearts >= 12:
                # too many hearts
                pass
            elif node.lvl in [6,8] and hearts < 12:
                # not enough hearts
                pass
            elif node.lvl == 0 and node.item > 0 and node.item & items == node.item:
                # already have this item
                pass
            elif node.need & items == node.need:
                found = True
                break
            else:
                # print 'missing item:', node.need & ~items
                pass
            pois[:] = pois[1:] + pois[:1]

        if not found:
            print "error"
            print "lvls:", lvls
            print "pois:", pois
            print "items:", items
            sys.exit(0)

        node_nr = pois.pop()

        # wallet -= cost
        # budget -= cost
        # if node.lvl == 7 and items & 2 == 0: # don't have candle already
        #     budget -= 60

        items |= node.item

        if node.heart:
            hearts += 1

        # wallet += node.money

        state = State()
        flood(state, lunk, 0, 0)
        path = shortest(state, node_nr)
        distance += len(path)
        seqpoint = [node_nr, node2chr(node)]
        sequence.append(seqpoint)
        lunk = node_nr
        report += statout(state, path)

        if node.lvl > 0:
            lvls.append(node.lvl)
            hearts += 1

    report += "levels: " + str(lvls) + "\n"
    report += "hearts: " + str(hearts) + "\n"
    report += "sequence: " + str(sequence) + "\n"
    report += "distance: " + str(distance) + "\n"

    if distance < best:
        best = distance
        print report
