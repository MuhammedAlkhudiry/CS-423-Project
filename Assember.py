import re
import instfile


class Entry:
    def __init__(self, string, token, attribute):
        self.string = string
        self.token = token
        self.att = attribute


symtable = []


# print(symtable[12].string + ' ' + str(symtable[12].token) + ' ' + str(symtable[12].att))


def lookup(s):
    for i in range(0, symtable.__len__()):
        if s == symtable[i].string:
            return i
    return -1


def insert(s, t, a):
    symtable.append(Entry(s, t, a))
    return symtable.__len__() - 1


def init():
    for i in range(0, instfile.inst.__len__()):
        insert(instfile.inst[i], instfile.token[i], instfile.opcode[i])
    for i in range(0, instfile.directives.__len__()):
        insert(instfile.directives[i],
               instfile.dirtoken[i], instfile.dircode[i])


file = open('input.sic', 'r')
filecontent = []
bufferindex = 0
tokenval = 0
lineno = 1
pass1or2 = 1
locctr = 0
lookahead = ''
startLine = True

Xbit4set = 0x800000
Bbit4set = 0x400000
Pbit4set = 0x200000
Ebit4set = 0x100000

Nbitset = 2
Ibitset = 1

Xbit3set = 0x8000
Bbit3set = 0x4000
Pbit3set = 0x2000
Ebit3set = 0x1000

# Our variable:
IdIndex = 0
startAddress = 0
totalSize = 0
inst = 0
hexOrStrIndex = 0


def is_hex(s):
    if s[0:2].upper() == '0X':
        try:
            int(s[2:], 16)
            return True
        except ValueError:
            return False
    else:
        return False


def lexan():
    global filecontent, tokenval, lineno, bufferindex, locctr, startLine

    while True:
        # if filecontent == []:
        if len(filecontent) == bufferindex:
            return 'EOF'
        elif filecontent[bufferindex] == '#':
            startLine = True
            while filecontent[bufferindex] != '\n':
                bufferindex = bufferindex + 1
            lineno += 1
            bufferindex = bufferindex + 1
        elif filecontent[bufferindex] == '\n':
            startLine = True
            # del filecontent[bufferindex]
            bufferindex = bufferindex + 1
            lineno += 1
        else:
            break
    if filecontent[bufferindex].isdigit():
        # all number are considered as decimals
        tokenval = int(filecontent[bufferindex])
        # del filecontent[bufferindex]
        bufferindex = bufferindex + 1
        return 'NUM'
    elif is_hex(filecontent[bufferindex]):
        # all number starting with 0x are considered as hex
        tokenval = int(filecontent[bufferindex][2:], 16)
        # del filecontent[bufferindex]
        bufferindex = bufferindex + 1
        return 'NUM'
    elif filecontent[bufferindex] in ['+', '#', ',']:
        c = filecontent[bufferindex]
        # del filecontent[bufferindex]
        bufferindex = bufferindex + 1
        return c
    else:
        # check if there is a string or hex starting with C'string' or X'hex'
        if (filecontent[bufferindex].upper() == 'C') and (filecontent[bufferindex + 1] == '\''):
            bytestring = ''
            bufferindex += 2
            # should we take into account the missing ' error?
            while filecontent[bufferindex] != '\'':
                bytestring += filecontent[bufferindex]
                bufferindex += 1
                if filecontent[bufferindex] != '\'':
                    bytestring += ' '
            bufferindex += 1
            bytestringvalue = "".join("%02X" % ord(c) for c in bytestring)
            bytestring = '_' + bytestring
            p = lookup(bytestring)
            if p == -1:
                # should we deal with literals?
                p = insert(bytestring, 'STRING', bytestringvalue)
            tokenval = p
        # a string can start with C' or only with '
        elif filecontent[bufferindex] == '\'':
            bytestring = ''
            bufferindex += 1
            # should we take into account the missing ' error?
            while filecontent[bufferindex] != '\'':
                bytestring += filecontent[bufferindex]
                bufferindex += 1
                if filecontent[bufferindex] != '\'':
                    bytestring += ' '
            bufferindex += 1
            bytestringvalue = "".join("%02X" % ord(c) for c in bytestring)
            bytestring = '_' + bytestring
            p = lookup(bytestring)
            if p == -1:
                # should we deal with literals?
                p = insert(bytestring, 'STRING', bytestringvalue)
            tokenval = p
        elif (filecontent[bufferindex].upper() == 'X') and (filecontent[bufferindex + 1] == '\''):
            bufferindex += 2
            bytestring = filecontent[bufferindex]
            bufferindex += 2
            # if filecontent[bufferindex] != '\'':# should we take into account the missing ' error?

            bytestringvalue = bytestring
            if len(bytestringvalue) % 2 == 1:
                bytestringvalue = '0' + bytestringvalue
            bytestring = '_' + bytestring
            p = lookup(bytestring)
            if p == -1:
                # should we deal with literals?
                p = insert(bytestring, 'HEX', bytestringvalue)
            tokenval = p
        else:
            p = lookup(filecontent[bufferindex].upper())
            if p == -1:
                if startLine == True:
                    # should we deal with case-sensitive?
                    p = insert(filecontent[bufferindex].upper(), 'ID', locctr)
                else:
                    # forward reference
                    p = insert(filecontent[bufferindex].upper(), 'ID', -1)
            else:
                if (symtable[p].att == -1) and (startLine == True):
                    symtable[p].att = locctr
            tokenval = p
            # del filecontent[bufferindex]
            bufferindex = bufferindex + 1
        return symtable[p].token


def error(s):
    global lineno
    print('line ' + str(lineno) + ': ' + s)


def match(token):
    global lookahead
    if lookahead == token:
        lookahead = lexan()
    else:
        error('Syntax error')


def checkindex():
    global bufferindex, symtable, tokenval
    if lookahead == ',':
        match(',')
        if symtable[tokenval].att != 1:
            error('index regsiter should be X')
        match('REG')
        return True
    return False


def parse():
    sic()


def sic():
    header()
    body()
    tail()


def header():
    global IdIndex, startAddress, locctr, totalSize, pass1or2
    IdIndex = tokenval
    match("ID")
    match("START")
    startAddress = locctr = symtable[IdIndex].att = tokenval
    match("NUM")
    if pass1or2 == 2:
        print("H ", symtable[IdIndex].string, format(startAddress, "06X"), format(totalSize, "06x"))


def body():
    global inst, pass1or2

    if lookahead == "ID":
        if pass1or2 == 2:
            inst = 0
        match("ID")
        rest1()
        body()

    elif lookahead == "f3":
        if pass1or2 == 2:
            inst = 0
        stmt()
        body()


def tail():
    global totalSize, locctr, startAddress
    match("END")
    match("ID")
    totalSize = locctr - startAddress
    if pass1or2 == 2:
        print("E ", format(startAddress, '06x'))


def rest1():
    global locctr, inst, hexOrStrIndex
    if lookahead == "f3":
        stmt()

    elif lookahead == "WORD":
        locctr += 3
        if pass1or2 == 2:
            inst = symtable[tokenval].att
            print("T ", format(locctr - 3, '06x'), " 03 ", format(inst, '06x'))
        match("WORD")
        match("NUM")

    elif lookahead == "RESW":
        locctr += tokenval * 3  # ???/
        if pass1or2 == 2:
            inst = symtable[tokenval].att
            print("T ", format(locctr - 3, '06x'), " 03 ", format(inst, '06x'))
        match("RESW")
        match("NUM")

    elif lookahead == "RESB":
        locctr += tokenval
        if pass1or2 == 2:
            inst = symtable[tokenval].att
            print("T ", format(locctr - 3, '06x'), " 03 ", format(inst, '06x'))
        match("RESB")
        match("NUM")

    elif lookahead == "BYTE":
        hexOrStrIndex = tokenval
        match("BYTE")
        rest2()

    else:
        error("Syntax error")


def stmt():
    global locctr, inst, pass1or2
    if pass1or2 == 2:
        inst = symtable[tokenval].att << 16
        locctr += 3
        inst += symtable[tokenval].att
        print("T ", format(locctr - 3, '06x'), " 03 ", format(inst, '06x'))

    match("f3")
    match("ID")
    index()


def index():
    global inst, pass1or2, Xbit3set
    if lookahead == ",":
        match(",")
        match("REG")
        if pass1or2 == 2:
            inst += Xbit3set


def rest2():
    global locctr, inst, pass1or2, hexOrStrIndex
    if lookahead == "HEX":
        locctr += int(len(symtable[tokenval].string) / 2)
        if pass1or2 == 2:
            inst = symtable[hexOrStrIndex].att
            print("T ", format(locctr - 3, '06x'), " 03 ", format(inst, '06x'))
        match("HEX")
    elif lookahead == "STRING":
        locctr += len(symtable[tokenval].string) - 1
        if pass1or2 == 2:
            inst = symtable[hexOrStrIndex].att
            print("T ", format(locctr - 3, '06x'), " 03 ", format(inst, '06x'))
        match("STRING")


def main():
    global file, filecontent, locctr, pass1or2, bufferindex, lineno
    init()
    w = file.read()
    filecontent = re.split("([\\W])", w)
    i = 0
    while True:
        while (filecontent[i] == ' ') or (filecontent[i] == '') or (filecontent[i] == '\t'):
            del filecontent[i]
            if len(filecontent) == i:
                break
        i += 1
        if len(filecontent) <= i:
            break
    # to be sure that the content ends with new line
    if filecontent[len(filecontent) - 1] != '\n':
        filecontent.append('\n')
    for pass1or2 in range(1, 3):
        global lookahead
        lookahead = lexan()
        parse()
        bufferindex = 0
        locctr = 0
        lineno = 1

    file.close()


main()
