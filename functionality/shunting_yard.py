from string import digits


def getPrecedence(c):
    if c in digits or c == ".":
        return 1
    elif c == "+" or c == "-":
        return 2
    elif c == "*" or c == "/":
        return 3
    elif c == "^":
        return 4
    elif c == "(" or c == ")":
        return 0
    else:
        return -1


def hasLeftAssociativity(c):
    if c == "+" or c == "-" or c == "/" or c == "*":
        return True
    else:
        return False


def shuntingYardAlgo(expression):
    "coverts infix notation to reverse polish notation"
    output = ""
    stack = []
    for c in expression:
        if getPrecedence(c) < 0:
            raise ValueError(c)
        elif getPrecedence(c) == 1:
            output = output + c
        elif c == "(":
            stack.append(c)
        elif c == ")":
            while len(stack) != 0 and stack[-1] != "(":
                output = output + stack.pop()
            stack.pop()
        else:
            while (
                len(stack) != 0
                and getPrecedence(c) <= getPrecedence(stack[-1])
                and hasLeftAssociativity(c)
            ):
                output = output + stack.pop()
            stack.append(c)
            output = output + " "
    while len(stack) != 0:
        if stack[-1] == "(":
            raise ValueError(c)
        output = output + stack.pop()
    return output
