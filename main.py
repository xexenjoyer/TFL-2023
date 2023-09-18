import os
import subprocess
alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'y', 'z']
alphabet_bool = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
declare_fun = []
help_num = 0


def parser(exp):
    ans = ""
    global alphabet_bool
    global help_num
    global declare_fun
    open_num = help_num
    start_num = open_num
    remember_num = []
    remember_litera = []
    temporary_num = 0

    for i in range(len(exp)):
        if exp[i] != "(" and exp[i] != ")" and exp[i + 1] == "(" and not (exp[i] in declare_fun):
            ans += "(+ " + "(* " + alphabet[open_num] + str(1) + " "
            alphabet_bool[open_num] = 1
            open_num += 1
            help_num += 1
            declare_fun.append(exp[i])

        elif exp[i] != "(" and exp[i] != ")" and exp[i + 1] == "(" and (exp[i] in declare_fun):
            temporary_num = declare_fun.index(exp[i])
            ans += "(+ " + "(* " + alphabet[temporary_num] + str(1) + " "
            open_num += 1
            remember_num.append(open_num)
            remember_litera.append(alphabet[temporary_num])
            declare_fun.append(exp[i])

        if exp[i] != "(" and exp[i] != ")" and exp[i + 1] == ")":
            ans += exp[i] + " "

    while open_num > start_num:
        if (open_num in remember_num):
            temporary_num = remember_num.index(open_num)
            ans += ") " + remember_litera[temporary_num] + str(0) + " )"
        else:
            ans += ") " + alphabet[open_num - 1] + str(0) + " )"
        open_num -= 1

    return (ans)


def xcoeff(exp):
    coeff = ""
    ans = ""
    coeff_list = []
    flag = 0
    for i in range(len(exp) - 1):
        if exp[i + 1] == " " and flag == 1:
            flag = 0
            coeff += exp[i]
            coeff_list.append(coeff[1:])
            coeff = ""
        if exp[i] == "*":
            flag = 1
        if flag == 1 and exp[i] != "*":
            coeff += exp[i]
    for i in range(len(coeff_list)):
        ans += " " + coeff_list[i]
    ans = ans.split(" ")
    while ("" in ans):
        ans.remove("")
    ans_list = []
    for i in range(len(ans)):
        litera = ans[i][0]
        if i == 0:
            ans_list = [[litera + "11", litera + "12"], [litera + "21", litera + "22"]]
        else:
            helpstr = ans_list[0][0]
            ans_list[0][0] = "(+ " + "(* " + ans_list[0][0] + " " + litera + "11) " + "(* " + ans_list[0][
                1] + " " + litera + "21) )"
            ans_list[0][1] = "(+ " + "(* " + helpstr + " " + litera + "12) " + "(* " + ans_list[0][
                1] + " " + litera + "22) )"
            helpstr = ans_list[1][0]
            ans_list[1][0] = "(+ " + "(* " + ans_list[1][0] + " " + litera + "11) " + "(* " + ans_list[1][
                1] + " " + litera + "21) )"
            ans_list[1][1] = "(+ " + "(* " + helpstr + " " + litera + "12) " + "(* " + ans_list[1][
                1] + " " + litera + "22) )"

    return (ans_list)


"""
(+ (* a11 b11) (* a12 b12) )
"""


def freecoeff(exp):
    coeff = ""
    coeff_list = []
    freecoeff_list = []
    flag = 0
    ans = "(+"
    for i in range(len(exp)):
        if exp[i] == "0":
            freecoeff_list.append((exp[i - 1] + exp[i]))
        if exp[i] == "1":
            coeff_list.append((exp[i - 1] + exp[i]))
    freecoeff_list = freecoeff_list[::-1]
    coeff_list = coeff_list

    ans_list = []

    for i in range(len(freecoeff_list)):
        if i != 0:
            xcoeff_mult = [["", ""], ["", ""]]
            litera_free = freecoeff_list[i][0]
            freecoeff_matrix = [litera_free + "1", litera_free + "2"]
            for j in range(i):
                if j == 0:
                    litera = coeff_list[j][0]
                    xcoeff_mult = [[litera + "11", litera + "12"], [litera + "21", litera + "22"]]
                else:
                    litera = coeff_list[j][0]
                    helpstr = xcoeff_mult[0][0]
                    xcoeff_mult[0][0] = "(+ " + "(* " + xcoeff_mult[0][0] + " " + litera + "11) " + " " + "(* " + \
                                        xcoeff_mult[0][
                                            1] + " " + litera + "21) )"
                    xcoeff_mult[0][1] = "(+ " + "(* " + helpstr + " " + litera + "12) " + " " + "(* " + xcoeff_mult[0][
                        1] + " " + litera + "22) )"
                    helpstr = xcoeff_mult[1][0]
                    xcoeff_mult[1][0] = "(+ " + "(* " + xcoeff_mult[1][0] + " " + litera + "11) " + " " + "(* " + \
                                        xcoeff_mult[1][
                                            1] + " " + litera + "21) )"
                    xcoeff_mult[1][1] = "(+ " + "(* " + helpstr + " " + litera + "12) "+ " " + "(* " + xcoeff_mult[1][
                        1] + " " + litera + "22) )"
            helpstr = freecoeff_matrix[0]
            freecoeff_matrix[0] = "(+ (* " + xcoeff_mult[0][0] + " " + freecoeff_matrix[0] + ")" + " " + "(* " + \
                                  xcoeff_mult[0][
                                      1] + " " + freecoeff_matrix[1] + ") )"
            freecoeff_matrix[1] = "(+ (* " + xcoeff_mult[1][0] + " " + helpstr + ")" + " " + "(* " + xcoeff_mult[1][
                1] + " " + freecoeff_matrix[1] + ") )"
            ans_list.append(freecoeff_matrix)
        else:
            litera_free = freecoeff_list[i][0]
            freecoeff_matrix = [litera_free + "1", litera_free + "2"]
            ans_list.append(freecoeff_matrix)
    final_matrix = ans_list[0]
    for i in range(len(ans_list)):
        for j in range(len(final_matrix)):
            if i !=0:
                final_matrix[j]="(+ " + final_matrix[j]+ " " + ans_list[i][j] + " )"
    return(final_matrix)


def makesolution(list1, list2, list3, list4):
    for i in range(len(list1)):
        for j in range(len(list1[i])):
            list1[i][j] = list1[i][j].replace("*","arc_plus")
            list1[i][j] = list1[i][j].replace("+", "arc_max")
    for i in range(len(list2)):
            list2[i] = list2[i].replace("*","arc_plus")
            list2[i] = list2[i].replace("+", "arc_max")
    for i in range(len(list3)):
        for j in range(len(list3[i])):
            list3[i][j] = list3[i][j].replace("*","arc_plus")
            list3[i][j] = list3[i][j].replace("+", "arc_max")
    for i in range(len(list4)):
        list4[i] = list4[i].replace("*", "arc_plus")
        list4[i] = list4[i].replace("+", "arc_max")
    return(list1, list2, list3, list4)


if __name__ == '__main__':
    print("Пример ввода: f(g(x))=g(x)")
    exp = input().split("=")
    left = parser(exp[0])
    right = parser(exp[1])
    print(left)
    print(right)
    xleft, freeleft, xright, freeright = makesolution(xcoeff(left), freecoeff(left), xcoeff(right), freecoeff(right))
    f = open("lab1.smt2", "w")
    f.write("(set-logic QF_NIA)"+"\n")
    for i in range (len(alphabet_bool)):
        if alphabet_bool[i]== 1:
            f.write("(declare-fun " + alphabet[i] +"11" + " () Int)"+"\n")
            f.write("(declare-fun " + alphabet[i] + "12" + " () Int)" + "\n")
            f.write("(declare-fun " + alphabet[i] + "21" + " () Int)" + "\n")
            f.write("(declare-fun " + alphabet[i] + "22" + " () Int)" + "\n")
            f.write("(declare-fun " + alphabet[i] + "1" + " () Int)" + "\n")
            f.write("(declare-fun " + alphabet[i] + "2" + " () Int)" + "\n")
    f.write("(define-fun arc_max ((a Int) (b Int)) Int (ite (>= a b) a b))\n")
    f.write("(define-fun arc_plus ((a Int) (b Int)) Int (ite (or (= a -1) (= b -1)) -1 (+ a b) ) )\n")
    f.write("(define-fun arc_greater ((a Int) (b Int)) Bool (ite (and (= a -1) (= b -1) ) true (> a b)))\n")
    for i in range(len(alphabet_bool)):
        if alphabet_bool[i] == 1:
            f.write("(assert (or (> " + alphabet[i] + "11" + " -1) (and (= " + alphabet[i] +"11 0) (= " + alphabet[i] +"1 0) ) ) )" + "\n")
            f.write("(assert (> " + alphabet[i] + "1" + " -1))" + "\n")

            f.write("(assert (>= " + alphabet[i] + "12" + " -1))" + "\n")
            f.write("(assert (>= " + alphabet[i] + "21" + " -1))" + "\n")
            f.write("(assert (>= " + alphabet[i] + "22" + " -1))" + "\n")
            f.write("(assert (>= " + alphabet[i] + "2" + " -1))" + "\n")
    f.write("(assert (arc_greater " + xleft[0][0] + " " + xright[0][0] + "))\n")
    f.write("(assert (arc_greater " + xleft[0][1] + " " + xright[0][1] + "))\n")
    f.write("(assert (arc_greater " + xleft[1][0] + " " + xright[1][0] + "))\n")
    f.write("(assert (arc_greater " + xleft[1][1] + " " + xright[1][1] + "))\n")
    f.write("(assert (arc_greater " + freeleft[0] + " " + freeright[0] + "))\n")
    f.write("(assert (arc_greater " + freeleft[1] + " " + freeright[1] + "))\n")
    f.write("(check-sat)\n(get-model)\n(exit)")

    os.system('z3 -smt2 lab1.smt2 > output.txt')
    out = subprocess.run('z3 -smt2 lab1.smt2', stdout=subprocess.PIPE , encoding='utf-8' )
    print(alphabet_bool)
    out.stdout
