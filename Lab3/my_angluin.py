import my_teacher
import backend_elim
import main as finale
'''answer = ''
rows = {}
T = {}
SA = []
E = []
S = []
A = []
c = 0'''

def consistent(S: list, A: list, rows: dict):
    for i in S:
        for j in S:
            if rows[i]==rows[j] and i!=j:
                for a in A:
                    #print(rows)
                    if i+a in rows.keys() and j+a in rows.keys():
                        if rows[i+a]!=rows[j+a]:
                            return False, a
    return True, ''

def closed(SA: list, S: list, rows: dict):
    for i in SA:
        to_save = ""
        flag = 0
        for j in S:
            to_save = j
            if rows[i] == rows[j]:
                flag = 1
        if flag == 0:
            return False, i, to_save
    return True, "", ""
def delete_epsilon(transitions):
    for i in range(len(transitions)):
        if transitions[i]['trigger'] == "":
            transitions.pop(i)
            break
    return transitions
def table2dfa(S,SE,T,A):
    states = []
    finals = []
    for i in S:
        name = ''
        if i in T.keys():
            for j in T[i].values():
                name += str(j)
            if name[0] == "1":
                finals.append(name)
            states.append(name)
    name = ''
    for i in T[''].values():
        name += str(i)
    initial = name
    transitions = []
    for i in SE.keys():
        fromstatename = ''
        for j in T[i].values():
            fromstatename += str(j)
        for a in A:
            tostatename=''
            key = i + a
            if key in T.keys():
                for j in T[key].values():
                    tostatename += str(j)
                if tostatename not in states:
                    states.append(tostatename)
                transition = {'source': fromstatename, 'dest': tostatename, 'trigger': a}
                if transition not in transitions:
                    transitions.append(transition)


    return states, transitions, finals, initial
    #equivalence(states,transitions,endstates,initial, grammar)

def closeandconsist(alphabet, A, SA, rows, grammar, S, T, E, SE):
    for i in alphabet:
        A.append(i)
        if i not in SA:
            SA.append(i)

    for a in SA:
        rows[a] = [my_teacher.word_occurrence(grammar, a)]
    for a in SA:
        T[a] = {'': my_teacher.word_occurrence(grammar, a)}

    while not closed(SA, S, rows)[0] or not consistent(S, A, rows)[0]:
        ans, word = consistent(S, A, rows)
        if not ans:
            if word not in E:
                E.append(word)
            else:
                word = word + word
                E.append(word)
            for a in SA:
                rows[a] = []
            for e in E:
                for a in SA:
                    rows[a].append(my_teacher.word_occurrence(grammar, a+e))
                    T[a] = {**T[a], **{e: my_teacher.word_occurrence(grammar, a+e)}}


        ans, word, _ = closed(SA, S, rows)
        if not ans:
            S.append(word)
            for i in A:
                if word + i not in SA:
                    SA.append(word + i)
            for a in SA:
                rows[a] = my_teacher.word_occurrence(grammar, a)
            for e in E:
                for a in SA:
                    T[a] = {e: my_teacher.word_occurrence(grammar, a + e)}
    for i in E:
        for j in S:
            SE[j] = {i: my_teacher.word_occurrence(grammar, j)}
    """print('---')
    print(S)
    print(SA)
    print(T)
    print('---')"""
    return alphabet, A, SA, rows, grammar, S, T, E, SE

def dfa_to_regex(transitions, states, initial_state, final_states):
    transitions = backend_elim.removeStates(transitions, states, initial_state, final_states)
    regular = ''
    for transition in transitions:
        if not (transition['trigger'] == ''):
            if '()' in transition['trigger']:
                regular += transition['trigger'].replace('()', '(ε)') + '|'
            else:
                regular += transition['trigger'] + '|'

    regular = regular[:-1]
    minRegex = regular
    return minRegex

def main(alphabet):
    f = open("grammar.txt", "r")
    grammar = f.read()
    f.close()
    #global E, T, S, A, SA, rows
    S = [""]
    E = [""]
    A = [""]
    SA = [""]
    SE = {}
    rows = {}
    T = {}

    closeandconsist(alphabet, A, SA, rows, grammar, S, T, E, SE)
    ans = 0
    index = 0
    while not ans:
        states, transitions, final_states, initial_state = table2dfa(S, SE, T, alphabet)
        ans, word = my_teacher.equivalence(states, transitions, final_states, initial_state, my_teacher.grammar, alphabet)
        newbies = []
        if not ans:
            toappend = ''
            for i in word:
                toappend += i
                newbies.append(toappend)
                S.append(toappend)

        for i in S:
            if i not in SA:
                SA.append(i)
        for a in SA:
            rows[a] = my_teacher.word_occurrence(grammar, a)

        for i in E:
            for j in newbies:
                T[j] = {i: my_teacher.word_occurrence(grammar, j)}

        for i in E:
            for j in S:
                SE[j] = {i: my_teacher.word_occurrence(grammar, j)}
        for a in SA:
            rows[a] = my_teacher.word_occurrence(grammar, a)
        closeandconsist(alphabet, A, SA, rows, grammar, S, T, E, SE)
    regex = dfa_to_regex(transitions, states, initial_state, final_states)
    return regex, transitions, states, initial_state, final_states

''' print(closed(SA, S, rows))
    print(consistent(S, A, rows))
    print('---')
    print([''])
    print(S)
    print(E)
    print(T)
    print('---')
    print(rows)
    print(SE)
    print(SA)
'''