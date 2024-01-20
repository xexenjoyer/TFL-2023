import itertools
import random
import re


class Cfg:
    def __init__(self, init_path=''):
        self.variables = []
        self.simbols = []
        self.rules = dict()
        self.start_rule = ''
        self.prefix_var = []
        if init_path:
            f = open(init_path).read()
            strings = f.replace('\n', '')
            strings = strings.strip()
            strings = strings.split(";")
            self.variables = strings[0].split(': ')[1].split(',')
            self.simbols = strings[1].split(': ')[1].split(',')
            self.start_rule = strings[2].split(': ')[1].split(',')
            P = strings[3].split(':')[1].split(',')
            P_Left = [''] * len(P)
            P_Right = [''] * len(P)
            for i in range(len(P)):
                P_Left[i], P_Right[i] = P[i].split(' -> ')
            for i in range(len(P_Left)):
                rules = P_Right[i].split(' | ')
                value = []
                for rule in rules:
                    list_of_simbols = rule.split(' ')
                    value.append(list_of_simbols)

                if P_Left[i] in self.rules.keys():
                    self.rules[P_Left[i]].extend(value)
                else:
                    self.rules[P_Left[i]] = value

    def get_nullable_variables(self):
        N = set(self.rules.keys())
        nullable_vars = ['#']

        while True:
            oldN = N
            for rule in list(self.rules.keys()):
                for var in list(self.rules[rule]):
                    if (len(set(var) - set(nullable_vars))) == 0 and rule not in nullable_vars:
                        nullable_vars.append(rule)
            N = N - set(nullable_vars)
            if oldN == N:
                break

        nullable_vars.remove('#')
        return nullable_vars

    def lists_all_combinations_of_removal(self, l, removal, existent, rule):
        combinations = existent.copy()
        indexlist = []
        bin_size = 0

        for i, ele in enumerate(l):
            if ele in removal:
                indexlist.append([None, 1, ele])
                bin_size += 1
            else:
                indexlist.append([None, 0, ele])

        if bin_size == 0:
            return combinations

        bin_list = list(itertools.product([0, 1], repeat=bin_size))

        for b in bin_list:
            new_combo = []

            bindigit = 0
            for i, listele in enumerate(indexlist):
                if listele[1] == 1:
                    indexlist[i][0] = b[bindigit]
                    bindigit += 1
                else:
                    indexlist[i][0] = 0
            for listele in indexlist:
                if listele[0] == 0:
                    new_combo.append(listele[2])

            if new_combo not in combinations and new_combo != [] and not (len(new_combo) == 1 and new_combo[0] == rule):
                combinations.append(new_combo)

        return combinations

    def find_if_rule_gens_eps(self, init_rule, nullable_vars, visited=None):
        for var in self.rules[init_rule]:
            for simbol in var:
                if simbol == '#':
                    return True
            if len(var) == 1 and var[0].isupper() and var[0] in self.rules.keys() and var not in visited:
                visited.append(var)
                return self.find_if_rule_gens_eps(var[0], nullable_vars, visited)
        return False

    def remove_eps_rules(self, nullable_vars, cfg=None):
        if not cfg:
            cfg = self

        start_rule_gens_eps = cfg.start_rule in nullable_vars
        combinations = []
        for rule in list(cfg.rules.keys()):
            for var in list(cfg.rules[rule]):
                if len(var) == 1 and var[0] == "#" and len(cfg.rules[rule]) == 1:
                    cfg.rules[rule] = [""]
                elif len(var) == 1 and var[0] == "#" and len(cfg.rules[rule]) > 1:
                    cfg.rules[rule].remove(var)
                else:
                    combinations = self.lists_all_combinations_of_removal(var, nullable_vars, cfg.rules[rule], rule)
                    cfg.rules[rule] = combinations.copy()

        if start_rule_gens_eps:
            cfg.rules[cfg.start_rule].append("#")

        return cfg

    def remove_unit_rules(self, cfg=None):
        if not cfg:
            cfg = self

        chaining = dict()

        for key in list(cfg.rules.keys()):
            chaining[key] = [''.join(key)]

        for rule in chaining.keys():
            for var in cfg.rules[rule]:
                if len(var) == 1 and var[0] in chaining.keys():
                    chaining[rule].extend(var)

        for key in chaining.keys():
            lookfor = list(chaining[key])[1:]
            if lookfor != []:
                for look in lookfor:
                    for var in cfg.rules[look]:
                        if len(var) == 1 and var[0] not in chaining[key] and var[0] in chaining.keys():
                            chaining[key].extend(var)

        rules_wo_unit_vars = dict()

        for key in chaining.keys():
            for gen in chaining[key]:
                for var in cfg.rules[gen]:
                    if len(var) != 1 or (len(var) == 1 and (not var[0].isupper())):
                        if key not in rules_wo_unit_vars.keys():
                            rules_wo_unit_vars[key] = []
                        if var not in rules_wo_unit_vars[key] and var:
                            rules_wo_unit_vars[key].append(var)

        cfg.rules = rules_wo_unit_vars

        return cfg

    def remove_useless_variables(self, cfg):
        if not cfg:
            cfg = self
        v1 = []
        for rule in cfg.rules.keys():
            for var in cfg.rules[rule]:
                if len(var) == 1 and ''.join(var) in cfg.simbols:
                    v1.append(rule)

        for rule in list(set(cfg.variables) - set(v1)):
            for var in cfg.rules[rule]:
                if not False in (((simbol in cfg.simbols) or simbol in v1) for simbol in var):
                    if (rule not in v1) and not ('' in var):
                        v1.append(rule)

        for rule in list(set(cfg.variables) - set(v1)):
            for var in cfg.rules[rule]:
                if not False in (((simbol in cfg.simbols) or simbol in v1) for simbol in var):
                    if (rule not in v1) and not ('' in var):
                        v1.append(rule)

        v1.append(''.join(cfg.start_rule))
        v1 = list(set(v1))
        r1 = dict()
        for rule in v1:
            new_var_for_rule = []
            for var in cfg.rules[rule]:
                if (False in (((x in v1 or x in cfg.simbols) and x not in new_var_for_rule) for x in var)) == False:
                    new_var_for_rule.append(var)
            r1[rule] = new_var_for_rule.copy()
        n = cfg.start_rule
        i2 = []
        while True:
            i2 = list(set().union(i2, n))
            y = list(set(v1) - set(i2))
            n2 = []
            for x in n:
                for var in r1[x]:
                    if True in ((somey in var) for somey in y):
                        for simbol in var:
                            if simbol in y:
                                index = var.index(simbol)
                                u = var[:index]
                                v = var[index:]
                                if not False in ((eleu in list(set().union(v1, cfg.simbols, ['']))) for eleu in u) \
                                        and not False in ((elev in list(set().union(v1, cfg.simbols, ['']))) for elev in
                                                          v) \
                                        and simbol not in n2:
                                    n2.append(simbol)
            n = n2.copy()
            if n2 == []:
                break
        v2 = i2.copy()
        r2 = dict()
        for rule in r1.keys():
            if rule in v2:
                r2[rule] = r1[rule].copy()

        cfg.variables = v2
        cfg.rules = r2

        return cfg

    def check_variables_only_rules(self, cfg):
        if not cfg:
            cfg = self

        for rule in cfg.rules.keys():
            for var in cfg.rules[rule]:
                if (len(var) > 1 and True in list((x in cfg.simbols) for x in var) and True in list(
                        (x in cfg.rules.keys()) for x in var)) or (
                        len(var) > 1 and not False in list((x in cfg.simbols for x in var))):
                    return True
        return False

    def enforce_variables_only_rules(self, cfg):
        if not cfg:
            cfg = self

        new_rules_qnt = 0
        rule_for_simbol = dict()
        while self.check_variables_only_rules(cfg):
            cfg2 = Cfg()
            for key, value in cfg.rules.items():
                cfg2.rules[key] = value
            cfg2.simbols = cfg.simbols.copy()
            cfg2.variables = cfg.variables.copy()
            cfg2.start_rule = cfg.start_rule

            done = False
            for rule in cfg.rules.keys():
                for i, var in enumerate(cfg2.rules[rule]):
                    only_lowers_in_var = (len(var) > 1 and not False in list((x in cfg.simbols for x in var)))
                    for j, simbol in enumerate(var):
                        if (simbol in cfg2.simbols and len(var) > 1) or only_lowers_in_var:
                            if simbol not in rule_for_simbol.keys():
                                while ('X' + str(new_rules_qnt) + '' in cfg.rules.keys()):
                                    new_rules_qnt += 1
                                new_rule_name = 'X' + str(new_rules_qnt) + ''
                                rule_for_simbol[simbol] = new_rule_name
                                cfg2.rules[new_rule_name] = [[simbol]]

                                if simbol in rule_for_simbol.keys():
                                    cfg2.rules[rule][i] = var[:j] + [rule_for_simbol[simbol]] + var[j + 1:]
                                else:
                                    cfg2.rules[rule][i] = [new_rule_name] + var[j + 1:]
                            else:
                                cfg2.rules[rule][i] = var[:j] + [rule_for_simbol[simbol]] + var[j + 1:]
                            done = True
                        if done:
                            break
                    if done:
                        break
                if done:
                    break
            for key, value in rule_for_simbol.items():
                cfg2.variables = list(set().union([value], cfg2.variables))

            for key, value in cfg2.rules.items():
                cfg.rules[key] = value
            cfg.simbols = cfg2.simbols.copy()
            cfg.variables = cfg2.variables.copy()
            cfg.start_rule = cfg2.start_rule

        return cfg

    def check_dual_variable_rules(self, cfg):
        for rule in cfg.rules.keys():
            for var in cfg.rules[rule]:
                if len(var) > 2:
                    return True
        return False

    def enforce_dual_variable_rules(self, cfg):
        if not cfg:
            cfg = self

        new_rules_qnt = 0
        rule_for_dualVarRule = dict()
        cfg2 = Cfg()
        for key, value in cfg.rules.items():
            cfg2.rules[key] = value
        cfg2.simbols = cfg.simbols.copy()
        cfg2.variables = cfg.variables.copy()
        cfg2.start_rule = cfg.start_rule
        while self.check_dual_variable_rules(cfg2):
            cfg2 = Cfg()
            for key, value in cfg.rules.items():
                cfg2.rules[key] = value
            cfg2.simbols = cfg.simbols.copy()
            cfg2.variables = cfg.variables.copy()
            cfg2.start_rule = cfg.start_rule

            done = False
            for rule in list(cfg.rules.keys()):
                for i, var in enumerate(cfg2.rules[rule]):
                    if not False in list(((x in cfg.variables) for x in var)) and len(var) > 2:
                        u = var[:-2]
                        v = var[-2:]

                        if str(v) in list(rule_for_dualVarRule.keys()):
                            cfg2.rules[rule][i] = u + rule_for_dualVarRule[str(v)]
                        else:
                            while ('Y' + str(new_rules_qnt) + '' in cfg.rules.keys()):
                                new_rules_qnt += 1
                            new_rule_name = 'Y' + str(new_rules_qnt) + ''
                            rule_for_dualVarRule[str(v)] = [new_rule_name]
                            cfg2.rules[rule][i] = u + [new_rule_name]
                            cfg2.rules[new_rule_name] = [v]

                        done = True
                    if done:
                        break
                if done:
                    break
            for key, value in rule_for_dualVarRule.items():
                cfg2.variables = list(set().union(value, cfg2.variables))

            for key, value in cfg2.rules.items():
                cfg.rules[key] = value
            cfg.simbols = cfg2.simbols.copy()
            cfg.variables = cfg2.variables.copy()
            cfg.start_rule = cfg2.start_rule

        return cfg

    def to_Cnf(self):
        cnf = self
        nullable_vars = self.get_nullable_variables()
        cnf = self.remove_eps_rules(nullable_vars, cnf)
        cnf = self.remove_unit_rules(cnf)
        if len(cnf.variables) > 1:
            cnf = self.remove_useless_variables(cnf)
        cnf = self.enforce_variables_only_rules(cnf)
        cnf = self.enforce_dual_variable_rules(cnf)

        cnf = self.proc_cfg(cnf)

        return cnf

    def get_str(self, pre=False, suf=False, vfile=False, inf=False):
        string = ''
        if vfile:
            string = 'V: ' + ','.join(self.variables) + ',' + ','.join(list(set(self.prefix_var))) + ';\n'
            string += 'Var: ' + ','.join(self.simbols) + ';\n'
            string += 'S: ' + ''.join(self.start_rule) + ';\n'
            string += 'P:\n'

        self.prefix_var = list(set(self.prefix_var))
        if not pre:
            if inf:
                t = self.rules[''.join(self.start_rule)]
                t2 = []
                for v in t:
                    f = True
                    if len(v) > 1:
                        for j in v:
                            if 'P' in j:
                                f = False
                                break
                    else:
                        f = False
                    if f:
                        t2.append(v)
                if len(t2) > 0:
                    self.rules[''.join(self.start_rule)] = t2
            for val in self.rules[''.join(self.start_rule)]:
                s = ' '.join(val)
                if vfile:
                    string += '\n' + ''.join(self.start_rule) + " -> " + s + ','
                else:
                    string += '\n' + ' ' + ''.join(self.start_rule) + " -> " + s + ' '

            for key, val in self.rules.items():
                if key != ''.join(self.start_rule):
                    for p in val:
                        s = ' '.join(p)
                        if vfile:
                            string += '\n' + '' + key + " -> " + s + ','

                        else:
                            string += '\n' + ' ' + key + " -> " + s + ' '
        else:
            ugabuga = 0
            temp = {}
            for v in self.prefix_var:
                temp[v] = self.rules[v]
            if temp.get(''.join(self.start_rule)) != None:
                temp.pop(''.join(self.start_rule))
            temp2 = {}

            for v in self.variables:
                temp2[v] = self.rules[v]
            if vfile:
                string += '' + ''.join(self.start_rule) + ' -> #,'
            else:
                string += ' ' + ''.join(self.start_rule) + ' -> #'

            for val in self.rules[''.join(self.start_rule)]:
                if vfile:
                    string += '\n' + '' + ''.join(self.start_rule) + ' -> '
                else:
                    string += '\n' + ' ' + ''.join(self.start_rule) + ' -> '
                for p in val:
                    if len(val) > 1:
                        s = []
                        if suf:
                            s.append(''.join(val[0]))
                            s.append(' '.join(val[1]))
                        else:
                            if vfile:
                                s.append(''.join(val[0]))
                                s.append(' '.join(val[1]))
                            else:
                                s.append(' '.join(val[0]))
                                s.append(''.join(val[1]))
                if len(s) > 0:
                    if vfile:
                        string += ' | '.join(s) + ','
                    else:
                        string += ' | '.join(s) + ' '

            for key, val in temp2.items():
                for p in val:
                    s = ' '.join(p)
                    if vfile:
                        string += '\n' + '' + key + " -> " + s + ','
                    else:
                        string += '\n' + ' ' + key + " -> " + s + ' '
            for key, val in temp.items():
                for p in val:
                    if str(type(p)) == "<class 'list'>":
                        s = []
                        if suf:
                            if ['#'] in p:
                                s.append(''.join(p[1]))
                                s.append(''.join(p[0]))
                            else:
                                s.append(''.join(p[0]))
                                s.append(' '.join(p[1]))
                        else:
                            if vfile:
                                s.append(''.join(p[0]))
                                s.append(' '.join(p[1]))
                            else:
                                s.append(' '.join(p[0]))
                                s.append(''.join(p[1]))
                        st = ' | '.join(s)
                        if vfile:
                            string += '\n' + '' + key + ' -> ' + st + ','
                        else:
                            string += '\n' + ' ' + key + ' -> ' + st + ' '
                    else:
                        if vfile:
                            string += '\n' + '' + key + ' -> ' + ' | '.join(p) + ','
                        else:
                            string += '\n' + ' ' + key + ' -> ' + ' | '.join(p) + ' '
                        break
        if not vfile:
            newalph, used_var = self.rename()
            for key, val in newalph.items():
                string = string.replace(' ' + key + ' ', ' ' + val + ' ', -1)
                string = string.replace(' ' + key + ' ', ' ' + val + ' ', -1)
            string = string.replace('\n ', '\n').strip()
        else:
            string = string[:len(string) - 1]
        if vfile:
            return string
        else:
            return string, used_var

    def reverse_cfg(self):
        cnfreversed = dict()
        for v, p in self.rules.items():
            cnfreversed[v] = []
            for p1 in p:
                if len(p1) == 2:
                    p2 = [p1[1], p1[0]]
                    cnfreversed[v].append(p2)
                else:
                    cnfreversed[v].append(p1)
        self.rules = cnfreversed

    def proc_cfg(self, cfg):
        if not cfg:
            cfg = self
        string = ''
        tempdict = cfg.rules.copy()
        for key, val in cfg.rules.items():
            for p in val:
                if ''.join(p) in cfg.simbols:
                    s = ''
                    counter = 0
                    while s + 'Q' + str(counter) + '' in cfg.variables:
                        counter += 1
                    temp = s + 'Q' + str(counter) + ''
                    cfg.variables.append(temp)
                    tempdict[key][val.index(p)] = [temp]
                    tempdict[temp] = []
                    tempdict[temp].append(p)
                    string += temp + ' -> ' + ''.join(p) + '\n'
                else:
                    string += key + ' -> ' + ' '.join(p) + '\n'
        cfg.rules = tempdict.copy()
        return cfg

    def prefix_cfg(self):
        cnfprefix = {}
        for v1, Ps in self.rules.items():
            cnfprefix[v1] = []
            for p1 in Ps:
                v2 = v1 + "P"
                if v2 not in cnfprefix.keys():
                    cnfprefix[v2] = []
                if v2 not in self.variables:
                    self.prefix_var.append(v2)

                if len(p1) == 1:
                    cnfprefix[v2].append([[p1[0]], ['#']])
                else:
                    v3 = p1[1] + "P"
                    if v3 not in self.variables:
                        self.prefix_var.append(v3)
                    v4 = p1[0] + "P"
                    if v4 not in self.variables:
                        self.prefix_var.append(v4)

                    cnfprefix[v2].append([[p1[0], v3], [v4]])

                cnfprefix[v1].append(p1)

        self.start_rule = ''.join(self.start_rule) + 'P'
        self.rules = cnfprefix

    def rename(self):
        arr = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U",
               "W", "X", "Y", "Z"]
        alph = self.prefix_var + self.variables
        alph2 = {}
        arr2 = []
        for v in alph:
            alph2[v] = 'A' + 'A' + 'A'
            while alph2[v] in arr2:
                alph2[v] = random.choice(arr) + random.choice(arr) + random.choice(arr)
            arr2.append(alph2[v])
        return alph2, arr2


def main(init_path, anti=False):
    if not anti:
        cfgdefault = Cfg(init_path)
        cfgdefault.to_Cnf()
        default, default_var = cfgdefault.get_str()
        de = default.replace('#', '').replace('\n', '.\n') + '.'
        # print(de)
        cfg = Cfg(init_path)
        cfg.to_Cnf()
        cfg.prefix_cfg()
        prefix, prefix_var = cfg.get_str(pre=True)
        pre = prefix.replace('#', '').replace('\n', '.\n') + '.'
        # print(pre)
        cfg2 = Cfg(init_path)
        cfg2.to_Cnf()
        cfg2.reverse_cfg()
        cfg2.prefix_cfg()
        cfg2.reverse_cfg()
        suffix, suffix_var = cfg2.get_str(pre=True, suf=True)
        suf = suffix.replace('#', '').replace('\n', '.\n') + '.'
        # print(suf)
        cfg3 = Cfg(init_path)
        cfg3.to_Cnf()
        cfg3.reverse_cfg()
        cfg3.prefix_cfg()
        cfg3.reverse_cfg()
        shtuka = cfg3.get_str(pre=True, suf=True, vfile=True)
        f = open('infix.txt', 'w')
        f.write(shtuka)
        f.close()
        cfg3 = Cfg('infix.txt')
        cfg3.to_Cnf()
        infix, infix_var = cfg3.get_str(inf=True)
        inf = infix.replace('#', '').replace('\n', '.\n') + '.'
        # print(inf)
        var = ' '.join(default_var) + ' ' + ' '.join(prefix_var) + ' ' + ' '.join(suffix_var) + ' ' + ' '.join(
            infix_var)
        f = open('var.txt', 'w')
        f.write(var)
        f.close()

        return prefix, suffix, infix, default

    if anti:
        cfgdefault = Cfg(init_path)
        cfgdefault.to_Cnf()
        default, default_var = cfgdefault.get_str()
        # print(default)
        return None, None, None, default


if __name__ == '__main__':
    main("G.txt")