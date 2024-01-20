import pasha
import my_teacher
import my_angluin
import rstr

grammar = ''


def isin(arr, el):
    for a in arr:
        if a == el:
            return True
    return False


def rename(transitions, states, endstates, initial):
    states.sort()
    newstates = []
    newendstates = []
    counter = 0
    for i in range(len(states)):
        if initial == states[i]:
            initial = counter
        newstates.append(counter)
        for j in range(len(transitions)):
            if transitions[j].get('source') == states[i]:
                if endstates in transitions[j].get('source') and newendstates not in counter:
                    newendstates.append(counter)
                transitions[j].update({'source': counter})

            if transitions[j].get('dest') == states[i]:
                if endstates in transitions[j].get('dest') and newendstates not in counter:
                    newendstates.append(counter)
                transitions[j].update({'dest': counter})
        counter += 1
    return transitions, newstates, newendstates, initial


def intersect(initial1, states1, transitions1, endstates1, initial2, states2, transitions2, endstates2):
    initial3 = int(str(initial1) + str(initial2))
    states3 = []
    transitions3 = []
    endstates3 = []

    for i in range(len(states1)):
        for j in range(len(states2)):
            states3.append(int(str(states1[i]) + str(states2[j])))
            if isin(endstates1, states1[i]) and isin(endstates2, states2[j]):
                endstates3.append(int(str(states1[i]) + str(states2[j])))

    for i in range(len(states1)):
        for j in range(len(states2)):
            for p in range(len(transitions1)):
                if transitions1[p].get('source') == states1[i]:
                    for q in range(len(transitions2)):
                        if transitions2[q].get('source') == states2[j] and transitions1[p].get('trigger') == \
                                transitions2[q].get('trigger'):
                            transitions3.append({'trigger': transitions1[p].get('trigger'),
                                                 'source': (str(states1[i]) + str(states2[j])), 'dest': (
                                        str(transitions1[p].get('dest')) + str(transitions2[q].get('dest')))})
                            break

    transitions3, states3, endstates3, initial3 = rename(transitions3, states3, endstates3, initial3)

    return transitions3, states3, initial3, endstates3


def reverseDFA(transitions, states, initial_state, final_states):
    new_final = []
    for i in states:
        if i not in final_states:
            new_final.append(i)
    return transitions, states, initial_state, new_final


def main():
    global grammar
    w1 = input('w1: ')
    w2 = input('w2: ')
    w3 = input('w3: ')
    w4 = input('w4: ')
    w5 = input('w5: ')
    С = input('C: ')
    pref, rev, infix, string = pasha.main('G.txt')
    infix = infix.replace('#', "")
    pref = pref.replace('#', "")
    rev = rev.replace('#', '')
    string = string.replace('#', '')

    grammar = pref
    with open('grammar.txt', 'w') as f:
        f.write(grammar)
    alph = []
    for i in w1:
        if i.isalpha():
            if i not in alph:
                alph.append(i)

    regex_w1, transitions1, states1, initial_state1, final_states1 = my_angluin.main(alph)

    grammar = rev
    with open('grammar.txt', 'w') as f:
        f.write(grammar)
    alph = []
    for i in w5:
        if i.isalpha():
            if i not in alph:
                alph.append(i)

    regex_w5, transitions5, states5, initial_state5, final_states5 = my_angluin.main(alph)

    grammar = infix
    with open('grammar.txt', 'w') as f:
        f.write(grammar)
    alph = []
    for i in w3:
        if i.isalpha():
            if i not in alph:
                alph.append(i)
    regex_w3, transitions3, states3, initial_state3, final_states3 = my_angluin.main(alph)
    grammar = string
    with open('grammar.txt', 'w') as f:
        f.write(grammar)
    w1_problem = []
    w5_problem = []
    for i in range(int(С)):
        w1_random = rstr.xeger(regex_w1)
        while len(w1_random) >= len(regex_w1):
            w1_random = rstr.xeger(regex_w1)
        w5_random = rstr.xeger(regex_w5)
        while len(w5_random) >= len(regex_w5):
            w5_random = rstr.xeger(regex_w5)
        pump = w1_random + w2 * i + w3 + w4 * i + w5_random
        pump = pump.replace('ε','')
        if my_teacher.word_occurrence(grammar, pump.replace('ε','')) == 1:
            print('No Problem')
            print(pump)
            continue
        else:
            print('Problem')
            print(pump)
            w1_problem.append(w1_random)
            w5_problem.append(w5_random)
    if len(w1_problem) > len(states5) + len(states1):
        f = open('problem.txt', 'w')
        f.write("V: S;\n")

        alphabet = []
        alph2write = ''
        for i in w1:
            if i not in alphabet:
                alphabet.append(i)
        for i in alphabet:
            alph2write += i + ','
        alph2write += '#;\n'
        f.write("Var: " + alph2write)
        f.write('S: S;\n')
        f.write('P:\n')
        trans2write = ''
        res = []
        [res.append(x) for x in w1_problem if x not in res]
        for i in range(len(res)):
            if res[i] == "ε":
                res[i] = ""

        for i in res:
            if i == "":
                trans2write += ' '.join("#") + " | "
            else:
                trans2write += ' '.join(i) + " | "
        f.write('S -> ' + trans2write[:-2])
        f.close()
        if res == ['']:
            with open('grammar.txt', 'w') as f:
                f.write(("AAA -> "))
        else:
            _, _, _, antiw1 = pasha.main('problem.txt', anti=True)
            with open('grammar.txt', 'w') as f:
                f.write(antiw1.replace("#", ""))
        # p for problem

        pregex_w1, ptransitions1, pstates1, pinitial_state1, pfinal_states1 = my_angluin.main(alph2write[:-4])

        f = open('problem.txt', 'w')
        f.write("V: S;\n")

        alphabet = []
        alph2write = ''
        for i in w5:
            if i not in alphabet:
                alphabet.append(i)
        for i in alphabet:
            alph2write += i + ','
        alph2write += '#;\n'
        f.write("Var: " + alph2write)
        f.write('S: S;\n')
        f.write('P:\n')
        trans2write = ''
        res = []
        [res.append(x) for x in w5_problem if x not in res]
        for i in range(len(res)):
            if res[i] == "ε":
                res[i] = ""

        for i in res:
            if i == "":
                trans2write += ' '.join("#") + " | "
            else:
                trans2write += ' '.join(i) + " | "
        f.write('S -> ' + trans2write[:-2])
        f.close()
        if res == ['']:
            with open('grammar.txt', 'w') as f:
                f.write(("AAA -> "))
        else:
            _, _, _, antiw5 = pasha.main('problem.txt', anti=True)
            with open('grammar.txt', 'w') as f:
                f.write(antiw5.replace("#", ""))
        # p for problem

        pregex_w5, ptransitions5, pstates5, pinitial_state5, pfinal_states5 = my_angluin.main(alph2write[:-4])

        # c for complement
        ctransitions1, cstates1, cinitial_state1, cfinal_states1 = reverseDFA(ptransitions1, pstates1, pinitial_state1,
                                                                              pfinal_states1)
        ctransitions5, cstates5, cinitial_state5, cfinal_states5 = reverseDFA(ptransitions5, pstates5, pinitial_state5,
                                                                              pfinal_states5)
        # i for intersect
        itransitions1, istates1, iinitial_state1, ifinal_states1 = intersect(initial_state1, states1, transitions1,
                                                                             final_states1, cinitial_state1, cstates1,
                                                                             ctransitions1, cfinal_states1)
        itransitions5, istates5, iinitial_state5, ifinal_states5 = intersect(initial_state5, states5, transitions5,
                                                                             final_states5, cinitial_state5, cstates5,
                                                                             ctransitions5, cfinal_states5)
        regex_w1_anti = my_angluin.dfa_to_regex(itransitions1, istates1, iinitial_state1, ifinal_states1)
        regex_w5_anti = my_angluin.dfa_to_regex(itransitions5, istates5, iinitial_state5, ifinal_states5)
        print("Регулярка w3")
        print(regex_w3)
        print("Регулярка w1 как разность между исходным языком и языкам контрпримеров")
        print(regex_w1_anti)
        print("но Регулярка w1 до пересечения")
        print(regex_w1)
        print("Регулярка w5 как разность между исходным языком и языкам контрпримеров")
        print(regex_w5_anti)
        print("но Регулярка w5 до пересечения")
        print(regex_w5)
    else:
        print("Регулярка w3")
        print(regex_w3)
        print("Регулярка w1")
        print(regex_w1)
        print("Регулярка w5")
        print(regex_w5)


if __name__ == '__main__':
    main()