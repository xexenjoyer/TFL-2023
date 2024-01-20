import random
from transitions import Machine
import re
import pickle
from typing import List
from collections import deque


class Node:
    def __init__(self, data, stars, left=None, right=None):
        self.val = data
        self.under = stars
        self.left = left
        self.right = right


class Node1:
    def __init__(self, data, left=None, right=None):
        self.val = data
        self.left = left
        self.right = right


word = ''
c = 0
remainder = 0
alphabet = []
operator = []
everything = []
epsilon = []
maxlevel = 0
operations = {'(': 0, '#': 1, '|': 2, '·': 3, '*': 4}
ends = []
trans = []
matrix = []


def isin(arr, el):
    for a in arr:
        if a == el:
            return True
    return False


def generate(node):
    global remainder
    if remainder == 0:
        node.val = alphabet[random.randint(0, len(alphabet) - 1)]
        return
    elif remainder == 1 or remainder == 2:
        remainder -= 1
        node.val = alphabet[random.randint(0, len(alphabet) - 1)]
    else:
        if node.val is None:
            node.val = everything[random.randint(0, len(everything) - 1)]
        if node.val == '*':
            node.left = Node(everything[random.randint(0, len(everything) - 2)], node.under + 1)
            remainder -= 1
            generate(node.left)
        elif node.val == '#' or node.val == '·':
            if node.under < maxlevel:
                node.left = Node(everything[random.randint(0, len(everything) - 1)], node.under)
                node.right = Node(everything[random.randint(0, len(everything) - 1)], node.under)
            else:
                node.left = Node(everything[random.randint(0, len(everything) - 2)], node.under)
                node.right = Node(everything[random.randint(0, len(everything) - 2)], node.under)
            remainder -= 2
            generate(node.left)
            generate(node.right)
        elif node.val == '|':
            if node.under < maxlevel:
                node.left = Node(epsilon[random.randint(0, len(epsilon) - 1)], node.under)
                node.right = Node(epsilon[random.randint(0, len(epsilon) - 1)], node.under)
            else:
                node.left = Node(epsilon[random.randint(0, len(epsilon) - 2)], node.under)
                node.right = Node(epsilon[random.randint(0, len(epsilon) - 2)], node.under)
            remainder -= 2
            generate(node.left)
            generate(node.right)


def statesfinder(transitions):
    states = []
    for t in transitions:
        if not isin(states, t.get('source')):
            states.append(t.get('source'))
        if not isin(states, t.get('dest')) and t.get('dest') != 'FinalState':
            states.append(t.get('dest'))
    return states


def deloop(transitions, states):
    for state in states:
        loops = []
        branches = []
        for i in range(len(transitions)):
            if transitions[i].get('source') == state:
                if transitions[i].get('dest') == state:
                    loops.append(i)
                else:
                    branches.append(i)

        update = ''
        if len(loops) > 1:
            update += '('
            for i in range(len(loops) - 1):
                update += transitions[loops[i]].get('trigger') + '|'
            update += transitions[len(loops) - 1].get('trigger') + ')*'
        elif len(loops) == 1:
            if len(transitions[loops[0]].get('trigger')) == 1:
                update += transitions[loops[0]].get('trigger') + '*'
            else:
                update += '(' + transitions[loops[0]].get('trigger') + ')*'
        update += ''
        for i in range(len(branches)):
            transitions[branches[i]].update({'trigger': update + transitions[branches[i]].get('trigger')})

        cleartransitions = []
        for i in range(len(transitions)):
            if not isin(loops, i):
                cleartransitions.append(transitions[i])
        transitions = cleartransitions
    return transitions


def unite(transitions):
    for i in range(len(transitions)):
        similar = []
        for j in range(len(transitions)):
            if transitions[j].get('source') != 'used' and transitions[i].get('source') == transitions[j].get(
                    'source') and transitions[i].get('dest') == transitions[j].get('dest') and i != j:
                similar.append(j)
                transitions[j].update({'source': 'used'})

        update = ''
        if len(similar) != 0:
            update += '('
        for s in similar:
            update += transitions[s].get('trigger') + '|'
        update += transitions[i].get('trigger')
        if len(similar) != 0:
            update += ')'
        transitions[i].update({'trigger': update})

    cleartransitions = []
    for i in range(len(transitions)):
        if transitions[i].get('source') != 'used':
            cleartransitions.append(transitions[i])
    return cleartransitions


def stateelim(states, transitions, initial):
    state = ''
    for i in range(len(states)):
        if states[i] != initial:
            state = states[i]
            break

    ins = []
    outs = []

    for j in range(len(transitions)):
        if transitions[j].get('source') == state:
            outs.append(j)
        elif transitions[j].get('dest') == state:
            ins.append(j)

    for j in ins:
        for k in outs:
            transitions.append({'trigger': transitions[j].get('trigger') + transitions[k].get('trigger'),
                                'source': transitions[j].get('source'), 'dest': transitions[k].get('dest')})

    cleartransitions = []
    for j in range(len(transitions)):
        if not isin(ins, j) and not isin(outs, j):
            cleartransitions.append(transitions[j])
    transitions = cleartransitions

    return transitions


triggerlist = []


def eliminate(chars, initial_regex):
    global trans, ends, matrix
    global triggerlist
    endstates, transitions, initial_regex = fsm(chars, initial_regex)

    initial = ''
    counter = 0
    states = statesfinder(transitions)

    for j in range(len(states)):
        fl = False
        for k in range(len(transitions)):
            if transitions[k].get('source') == states[j]:
                fl = True
                if states[j] == initial_regex:
                    initial = str(counter)
                transitions[k].update({'source': str(counter)})
            if transitions[k].get('dest') == states[j]:
                fl = True
                transitions[k].update({'dest': str(counter)})
        for k in range(len(endstates)):
            if endstates[k] == states[j]:
                endstates[k] = str(counter)
        if fl:
            counter += 1

    states = statesfinder(transitions)

    mat = []

    for i in range(len(states)):
        buf = []
        for j in range(len(states)):
            buf.append('')
        mat.append(buf)

    for t in transitions:
        if t.get('dest') == 'FinalState':
            continue
        mat[int(t.get('source'))][int(t.get('dest'))] = t.get('trigger')

    for e in endstates:
        ends.append(e)

    global triggerlist
    for t in transitions:
        # print(t)
        result = pickle.dumps(t)
        triggerlist.append(result)

    for m in mat:
        matrix.append(m)

    for f in endstates:
        transitions.append({'trigger': '', 'source': f, 'dest': 'FinalState'})

    while len(states) != 1:
        transitions = unite(transitions)

        transitions = deloop(transitions, states)

        transitions = stateelim(states, transitions, initial)

        states = statesfinder(transitions)

    transitions = deloop(transitions, states)
    transitions = unite(transitions)

    return transitions[0].get('trigger').replace('|)', '|ε)').replace('(|', '(ε|').replace('||', '|ε|')


def concat(s):
    if not s:
        return 'ε'
    res = s[0]
    for i in range(1, len(s)):
        if not (isin(')|#*', s[i]) or isin('(|#', s[i - 1])):
            res += '·'
        res += s[i]
    return res


def inorder(root):
    if root is None:
        return ''
    if root.val == '*':
        return '(' + inorder(root.left) + ')*'
    if root.val != '·':
        res = inorder(root.left) + root.val + inorder(root.right)
    else:
        res = inorder(root.left) + inorder(root.right)
    if isin('·#|*', root.val):
        return '(' + res + ')'
    return res


def postorder(root):
    if root is None:
        return
    postorder(root.left)
    postorder(root.right)
    if isin('|·*#', root.val):
        if root.val == '|':
            if root.left.val.isalpha() and root.right.val.isalpha():
                arr = [root.left.val, root.right.val]
                arr.sort()
                root.left.val = arr[0]
                root.right.val = arr[1]

            if root.left.val == '∅':
                root.val = root.right.val
                root.left = root.right.left
                root.right = root.right.right

            elif root.right.val == '∅':
                root.val = root.left.val
                root.right = root.left.right
                root.left = root.left.left

            elif eqvTree(root.right, root.left):
                temp = copy(root.left)
                root.val = temp.val
                root.left = temp.left
                root.right = temp.right

            elif (root.left.val == '|' and (
                    eqvTree(root.right, root.left.left) or eqvTree(root.right, root.left.right))) or eqvTree(root.right,
                                                                                                             root.left):
                temp = copy(root.left)
                root.left = temp.left
                root.right = temp.right
                root.val = temp.val

        elif root.val == '·':
            if root.left.val == '∅' or root.right.val == '∅':
                root.val = '∅'
                root.left = None
                root.right = None

            elif root.right.val == 'ε':
                root.val = root.left.val
                root.left = root.left.left
                root.right = root.left.right

            elif root.left.val == 'ε':
                root.val = root.right.val
                root.left = root.right.left
                root.right = root.right.right

        elif root.val == '#':
            if root.left.val == 'ε':
                root.val = root.right.val
                root.left = root.right.left
                root.right = root.right.right

            elif root.right.val == 'ε':
                root.val = root.left.val
                root.right = root.left.right
                root.left = root.left.left

            elif root.left.val == '∅' or root.right.val == '∅':
                root.val = '∅'
                root.left = None
                root.right = None

        elif root.val == '*':
            if root.left.val == '*':
                root.left = copy(root.left.left)


def getPost(expr):
    stack = []
    res = []
    for s in expr:
        if s.isalpha():
            res += s
        elif s == '(':
            stack.append(s)
        elif s == ')':
            while len(stack) > 0 and stack[len(stack) - 1] != '(':
                res += stack.pop()
            else:
                stack.pop()
        else:
            while len(stack) > 0 and operations[stack[len(stack) - 1]] >= operations[s]:
                res += stack.pop()
            stack.append(s)

    while len(stack) > 0:
        res += stack.pop()
    return res


def getBin(postfix):
    if not postfix:
        return
    stack = []
    for s in postfix:
        if isin('#|·', s):
            right, left = stack.pop(), stack.pop()
            stack.append(Node1(s, left, right))
        elif s in "*":
            left = stack.pop()
            stack.append(Node1(s, left))
        else:
            stack.append(Node1(s))

    return stack[len(stack) - 1]


def copy(node):
    if node is None:
        return None
    return Node1(node.val, copy(node.left), copy(node.right))


def null(node):
    if node is None:
        return False
    elif node.val == 'ε':
        return True
    elif node.val == '*':
        return True
    elif node.val == '|':
        return null(node.left) or null(node.right)
    elif node.val == '·' or node.val == '#':
        return null(node.left) and null(node.right)

    else:
        return False


def deriv(root, s):
    stack = [root]
    while len(stack) > 0:
        node = stack.pop()
        if node is None or node.val == '∅':
            continue

        elif node.val == 'ε':
            node.val = '∅'

        elif node.val == '|':
            stack.append(node.left)
            stack.append(node.right)

        elif node.val == '·':
            if null(node.left):
                node.val = '|'
                dnode = Node1('·', node.left, node.right)
                node.left = dnode
                node.right = copy(dnode.right)
                stack.append(node.left.left)
                stack.append(node.right)
            else:
                stack.append(node.left)

        elif node.val == s:
            node.val = 'ε'

        elif node.val == '*':
            temp = copy(node)
            node.val = '·'
            node.right = temp
            stack.append(node.left)

        elif node.val == '#':
            node.val = '|'
            temp1 = Node1('#', node.left, node.right)
            temp2 = Node1('#', copy(node.left), copy(node.right))
            node.left = temp1
            node.right = temp2
            stack.append(node.left.left)
            stack.append(node.right.right)

        else:
            node.val = '∅'
    return root


def derive(regex, s):
    node = getBin(getPost(concat(regex)))
    postorder(node)
    node = makeLeft(node)
    postorder(node)
    a = deriv(node, s)
    postorder(a)
    a = makeLeft(a)
    postorder(a)
    return inorder(a)


def fsm(chars, regex):
    counter = 0
    treeStates = []
    final_states = []
    transitions = []

    tree = getBin(getPost(concat(regex)))
    postorder(tree)

    tree = makeLeft(tree)
    postorder(tree)
    regex = inorder(tree)

    if null(tree):
        final_states.append(regex)

    states = [regex]

    for s in chars:
        derivative = derive(regex, s)

        if null(getBin(getPost(concat(derivative)))) and not isin(final_states, derivative):
            final_states.append(derivative)

        while derivative[0] == '(' and derivative[len(derivative) - 1] == ')':
            if brackets(derivative[1:]):
                derivative = derivative[1:]
            else:
                break

        if derivative != '∅' and not isin(treeStates, haveEqvTree(treeStates, getBin(getPost(concat(derivative))))):
            treeStates.append(getBin(getPost(concat(derivative))))
            states.append(inorder(getBin(getPost(concat(derivative)))))

        if not derivative == '∅':
            if not isin(transitions, {'trigger': s, 'source': states[counter],
                                      'dest': inorder(getBin(getPost(concat(derivative))))}):
                transitions.append(
                    {'trigger': s, 'source': states[counter], 'dest': inorder(getBin(getPost(concat(derivative))))})
    counter += 1

    while counter < len(states):
        for s in chars:
            derivative = derive(states[counter], s)

            if null(getBin(getPost(concat(derivative)))) and not isin(final_states, derivative):
                final_states.append(derivative)

            while derivative[0] == '(' and derivative[len(derivative) - 1] == ')':
                if brackets(derivative[1:]):
                    derivative = derivative[1:]
                else:
                    break

            if derivative != '∅' and not isin(treeStates, haveEqvTree(treeStates, getBin(getPost(concat(derivative))))):
                treeStates.append(getBin(getPost(concat(derivative))))
                states.append(inorder(getBin(getPost(concat(derivative)))))

            if derivative != '∅':
                eqv = haveEqvTree(treeStates, getBin(getPost(concat(derivative))))
                if not isin(transitions, {'trigger': s, 'source': states[counter],
                                          'dest': inorder(getBin(getPost(concat(derivative))))}):
                    transitions.append({'trigger': s, 'source': states[counter], 'dest': inorder(eqv)})

        counter += 1

    return final_states, transitions, regex


def brackets(str):
    stack = []
    for s in str:
        if s == '(':
            stack.append('(')
        elif s == ')':
            if len(stack) < 1:
                return False
            stack.pop()
    return len(stack) == 0


def eqvTree(q, p):
    if q is None and p is None:
        return True
    if q is None or p is None:
        return False
    if q.val != p.val:
        return False
    if q.val == '·' or p.val == '·' or q.val == '#' or p.val == '#':
        return eqvTree(p.left, q.left) and eqvTree(p.right, q.right)
    return (eqvTree(p.left, q.left) and eqvTree(p.right, q.right)) or (
            eqvTree(p.left, q.right) and eqvTree(p.right, q.left))


def haveEqvTree(forest, tree):
    for i in forest:
        if eqvTree(i, tree):
            return i
    return tree


def makeLeft(node):
    if node is None:
        return node
    if node.val == '|' and node.right.val == '|':
        node = rotate(node)
    node.left = makeLeft(node.left)
    node.right = makeLeft(node.right)
    return node


def rotate(root):
    res = root.right
    if not res:
        return root
    try:
        temp = res.left
    except:
        pass
    res.left = root
    root.right = temp
    return res


def createwords(list: List[int], start: int, end: int, states):
    global word
    if start == end:
        return word
    else:
        nextstate = random.randint(0, len(states) - 1)
        while list[start][nextstate][random.randint(0, len(list[start][nextstate]) - 1)] == "":
            nextstate = random.randint(0, len(states) - 1)

        word += list[start][nextstate][random.randint(0, len(list[start][nextstate]) - 1)]
        createwords(list, nextstate, end, states)

    return word


def isNotVisited(x: int, path: List[int]) -> int:
    size = len(path)
    for i in range(size):
        if path[i] == x:
            return 0

    return 1


def findpaths(g: List[List[int]], src: int,
              dst: int, v: int, matrix) -> None:
    anslist = []
    q = deque()

    path = [src]
    q.append(path.copy())
    while q:

        path = q.popleft()
        last = path[len(path) - 1]

        if last == dst:
            anslist.append(printans(path, matrix))

        for i in range(len(g[last])):
            if isNotVisited(g[last][i], path):
                newpath = path.copy()
                newpath.append(g[last][i])
                q.append(newpath)

    return anslist


def printans(list, matrix):
    ans = ""
    for i in range(len(list) - 1):
        ans += matrix[list[i]][list[i + 1]]
    return ans


def get_available_transitions(self, src) -> []:
    return [i[0] for i in list(filter(lambda x: src in x[1], self.transitions))]


upcount, downcount, neutralcount = 0, 0, 0


def checkword(word, states, deserialized, regexnoshuffle, alphabet, used_words):
    global upcount, downcount, neutralcount
    cases = ["multiple", "delete", "shuffle", "plus", "nothing"]

    todo = random.choice(cases)

    match todo:
        case "multiple":
            word += word

        case "delete":
            word = word[random.randint(0, len(word) // 2):]
        case "shuffle":
            word = word.join(random.sample(word, len(word)))
        case "plus":
            word += random.choice(alphabet)
        case "nothing":
            word
    if len(word) >= 51:
        word = word[:50]

    if word in used_words:
        checkword(word, states, deserialized, regexnoshuffle, alphabet, used_words)
        return used_words
    else:
        used_words.append(word)

    lump = Matter()
    flag = 0

    machine = Machine(lump, states=states, transitions=deserialized, initial='0')

    for i in word:
        try:
            lump.trigger(i)
        except (MachineError, KeyError):
            flag = 1

    if regexnoshuffle.count("ε") > 0:
        regexnoshuffle = regexnoshuffle.replace("ε", "^$")

    if re.fullmatch(regexnoshuffle, word) and (lump.state in ends) and flag == 0:
        print("Проверка прошла успешно в обоих случаях, проверочная строка:", word)
        upcount += 1
    elif (flag == 1 and not (re.fullmatch(regexnoshuffle, word))) or (
            flag == 0 and not (lump.state in ends) and not (re.fullmatch(regexnoshuffle, word))):
        print("Проверка прошла неуспешно в обоих случаях, проверочная строка:", word)
        downcount += 1
    else:
        print("Проблема со строкой:", word)
        neutralcount += 1

    return used_words


from transitions import Machine, MachineError


class Matter(object):
    pass


def main():
    global alphabet, operator, everything, remainder, epsilon, maxlevel
    characters = ['a', 'b', 'c', 'd', 'e']
    alphabet = characters[:random.randint(1, 5)]
    operator = ['|', '#', '·', '*']

    remainder = 0
    maxlevel = 0
    regex = ''
    print("Введите количество тестов: ")
    testnum = int(input())
    print("Введите 1, если хотите ввести регулярку руками и 0, если хотите, чтобы она сгенерировалась сама: ")
    self = int(input())

    if self == 0:
        print('Введите максимальную длину генерируемой регулярки (считаются символы алфавита и знаки операций): ')
        remainder = int(input())
        print('Введите максимальную звёздную вложенность: ')
        maxlevel = int(input())

        everything = []
        for j in alphabet:
            everything.append(j)
            epsilon.append(j)
        for j in operator:
            epsilon.append(j)
            everything.append(j)

        epsilon[len(epsilon) - 1] = 'ε'
        epsilon.append('*')

        rng = operator[random.randint(0, 3)]
        if rng == '*':
            node = Node(rng, 1)
        else:
            node = Node(rng, 0)
        generate(node)
        print('Сгенерированная регулярка:', inorder(node))
        regex = inorder(node)

    elif self == 1:
        regex = input()

    alphabet = []
    for s in regex:
        if s.isalpha() and not isin(alphabet, s) and s != 'ε':
            alphabet.append(s)

    print('Преобразованная регулярка:', eliminate(alphabet, regex), '\n')

    g = [[] for _ in range(len(matrix))]
    ans = [[[] for _ in range(len(matrix))] for _ in range(len(matrix))]
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            if matrix[i][j] != "":
                g[i].append(j)
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            if len(findpaths(g, i, j, len(matrix), matrix)) != 0:
                ans[i][j] = (findpaths(g, i, j, len(matrix), matrix))
            else:
                ans[i][j] = [""]
            if i == j:
                ans[i][j] = [matrix[i][j]]

    randomendstate = int(random.choice(ends))

    word = random.choice(ans[0][randomendstate])
    wordlist = []
    if len(ans[0][randomendstate]) > 1:
        wordlist = ans[0][randomendstate]
    else:
        for i in range(len(ends)):
            for j in range(len(ans[0][int(ends[i])])):
                wordlist.append(ans[0][int(ends[i])][j])

    states = []
    for i in range(len(matrix)):
        states.append(str(i))

    deserialized = []
    for i in range(len(triggerlist)):
        deserialized.append(pickle.loads(triggerlist[i]))

    regexnoshuffle = eliminate(alphabet, regex)

    used_words = []
    for i in range(testnum):
        used_words = checkword(random.choice(wordlist), states, deserialized, regexnoshuffle, alphabet, used_words)
    global neutralcount, upcount, downcount
    print("Положительных тестов ", upcount)
    print("Отрицательных тестов ", downcount)
    print("Аномальных тестов ", neutralcount)


if __name__ == '__main__':
    main()
