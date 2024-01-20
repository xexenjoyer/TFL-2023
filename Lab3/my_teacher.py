from cfg import CFG
from transitions import Machine
from nltk.parse.generate import generate
from nltk import CFG as nltkcfg
from collections import defaultdict
import pasha
import main
class Matter(object):
    pass

grammar =''

def change_grammar(new_grammar):
    global grammar
    grammar = new_grammar



def word_occurrence (grammar: str, string: str):
    alph = list()
    noterm = list()
    f = open("grammar.txt", "r")
    grammar = f.read()
    f.close()
    for i in grammar:
        if i.islower() and i not in alph:
            alph.append(i)
    grammar = grammar.split('\n')
    for i in range(len(grammar)):
            grammar[i]=grammar[i].split("->")
            grammar[i][1]=grammar[i][1].split("|")
            my_list=list()
            for j in range(len(grammar[i][1])):
                if grammar[i][1][j]=="" or grammar[i][1][j]==' ':
                    my_list.append("λ")
                else:
                    my_list.append(grammar[i][1][j].replace(' ', '').replace("'",''))
            for k in range(len(my_list)):
                if my_list[k] == "":
                    my_list[k] = "λ"
            grammar[i][1] = my_list
            grammar[i][0] = grammar[i][0].replace(' ', '')

    grammar=grammar[:len(grammar)]
    alphofterm = []
    for i in range(len(grammar)):
        if grammar[i][0] not in alphofterm:
            alphofterm.append(grammar[i][0])
    rules = {}
    for i in alphofterm:
        rules[i] = []
    for i in alphofterm:
        for j in grammar:
            if i == j[0]:
                rules[i].append(j[1])
    for key in rules.keys():
        flat_list = []
        for sublist in rules[key]:
            for item in sublist:
                flat_list.append(item)
        rules[key] = flat_list

    start, alph = grammar[0][0], alph
    alph.append('λ')
    f = open("var.txt", "r")
    list4noterm = f.read()
    f.close()
    list4noterm = list4noterm.split(" ")
    g = CFG(start_variable=start, terminals=alph, rules=rules, variables=list4noterm)

    if g.cyk(string):
        return 1
    else:
        return 0

def parsebydfa(word, states, transitions,   endstates, initial):
    lump = Matter()
    machine = Machine(model=lump,transitions=transitions, states=states, initial=initial)
    for i in word:
        try:
            lump.trigger(i)
        except Exception:
            return 0
    if lump.state in endstates:
        return 1
    else:
        return 0

def equivalence(states,transitions,endstates,initial, grammar, alph):
    f = open("grammar.txt", "r")
    grammar = f.read()
    f.close()
    for i in grammar:
        if i.islower():
            grammar = grammar.replace(" "+i," '"+i+"' ")
    grammar = nltkcfg.fromstring(grammar)
    for i in range(20):
        for sentence in generate(grammar, n=10, depth=i):
            flag = 0
            for i in sentence:
                if i not in alph:
                    flag = 1
                    continue
            if parsebydfa(sentence, states, transitions, endstates, initial):
                continue
            else:
                if flag == 0:
                    return 0, sentence
    return 1, ''


