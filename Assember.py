import re
import instfile


class Entry:
    def __init__(self, string, token, attribute, btype):
        self.string = string
        self.token = token
        self.att = attribute
        self.btype = btype


symtable = []


# print(symtable[12].string + ' ' + str(symtable[12].token) + ' ' + str(symtable[12].att))


def lookup(s):
    for i in range(0, symtable.__len__()):
        if s == symtable[i].string:
            return i
    return -1


def insert(s, t, a, b):
    symtable.append(Entry(s, t, a, b))
    return symtable.__len__() - 1


def init():
    for i in range(0, instfile.inst.__len__()):
        insert(instfile.inst[i], instfile.token[i], instfile.opcode[i], None)
    for i in range(0, instfile.directives.__len__()):
        insert(instfile.directives[i],
               instfile.dirtoken[i], instfile.dircode[i], None)


file = open('inputfromCH4.sic', 'r')
filecontent = []
bufferindex = 0
tokenval = 0
lineno = 1
pass1or2 = 1
locctr = 0
lookahead = ''
startLine = True

# Bbit4set = 0x400000
# Pbit4set = 0x200000
Ebit4set = 0x100000

Nbit4set = 0x2000000
Ibit4set = 0x1000000
Xbit4set = 0x800000

Nbitset = 2
Ibitset = 1

Xbit3set = 0x8000
Bbit3set = 0x4000
Pbit3set = 0x2000
Ebit3set = 0x1000

Nbit3set = 0x20000
Ibit3set = 0x10000

# Our variables:
IdIndex = 0
startAddress = 0
totalSize = 0
inst = 0

# SIC/EX variables
isLiteral = False  # is HEX/STRING a literal?
isExtd = False
isBASE = False  # Are we using the base?
isAddressed = False  # is the literals addressed or still -1?
base = None
PCrange = range(-2048, 2048)  # to 2048 not 2047 because range() is exclusive
BASErange = range(0, 4096)  # to 4096 not 4095 because range() is exclusive
disp = 0
literalArray = []  # saving the indices of the literal in symtable for later use
literalIndex = 0
literalValueASCII = []  # saving the ASCII code of literal for later use

# Program Blocks variables:
locctrArray = [0, 0, 0]
blockType = 0
RTP = 0  # Relative To Program = sizeOfBlockTybes + Target Address (TA)
sizeOfBlocks = [0, 0, 0]


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
    global filecontent, tokenval, lineno, bufferindex, locctrArray, startLine, literalValueASCII

    while True:
        # if filecontent == []:
        if len(filecontent) == bufferindex:
            return 'EOF'
        elif filecontent[bufferindex] == '%':
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
    elif filecontent[bufferindex] in ['+', '#', ',', '@', '=', '*']:
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
            literalValueASCII.append(bytestringvalue)  # saving the ASCII code of literal
            bytestring = '_' + bytestring
            p = lookup(bytestring)
            if p == -1:
                # should we deal with literals?
                p = insert(bytestring, 'STRING', (bytestringvalue if isLiteral is False else -1), blockType)
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
                p = insert(bytestring, 'STRING', bytestringvalue, blockType)
            tokenval = p
        elif (filecontent[bufferindex].upper() == 'X') and (filecontent[bufferindex + 1] == '\''):
            bufferindex += 2
            bytestring = filecontent[bufferindex]
            bufferindex += 2
            # if filecontent[bufferindex] != '\'':# should we take into account the missing ' error?

            bytestringvalue = bytestring
            if isLiteral:
                literalValueASCII.append(bytestringvalue)  # saving the ASCII code of literal
            if len(bytestringvalue) % 2 == 1:
                bytestringvalue = '0' + bytestringvalue
            bytestring = '_' + bytestring
            p = lookup(bytestring)
            if p == -1:
                # should we deal with literals?
                p = insert(bytestring, 'HEX', (bytestringvalue if isLiteral is False else -1), blockType)
            tokenval = p
        else:
            p = lookup(filecontent[bufferindex].upper())
            if p == -1:
                if startLine:
                    # should we deal with case-sensitive?
                    p = insert(filecontent[bufferindex].upper(), 'ID', locctrArray[blockType], blockType)
                else:
                    # forward reference
                    p = insert(filecontent[bufferindex].upper(), 'ID', -1, -1)
            else:
                if (symtable[p].att == -1) and startLine:
                    symtable[p].att = locctrArray[blockType]
                    symtable[p].btype = blockType
            tokenval = p
            # del filecontent[bufferindex]
            bufferindex = bufferindex + 1
        return symtable[p].token


def error(s):
    global lineno
    print('line ' + str(lineno) + ': ' + s)
    exit(1)


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


def removeDuplicates():
    global literalArray
    newliteralArray = []
    [newliteralArray.append(x) for x in literalArray if x not in newliteralArray]

    literalArray = newliteralArray


def addressLiteral():
    global locctrArray, inst, literalArray, isAddressed
    if not isAddressed:
        removeDuplicates()
        for i in range(0, len(literalArray)):

            symtable[literalArray[i]].att = locctrArray[blockType]
            symtable[literalArray[i]].btype = blockType

            if symtable[literalArray[i]].token == 'STRING':
                locctrArray[blockType] += len(symtable[literalArray[i]].string) - 1

            elif symtable[literalArray[i]].token == 'HEX':
                locctrArray[blockType] += (len(symtable[literalArray[i]].string) - 1) // 2

        isAddressed = True


def parse():
    sic()


def sic():
    header()
    body()
    tail()


def header():
    global IdIndex, startAddress, locctrArray, totalSize, pass1or2
    IdIndex = tokenval
    match("ID")
    match("START")
    startAddress = symtable[IdIndex].att = tokenval

    # assinging the 3 locctrs for program blocking.
    for i in range(0, len(locctrArray)):
        locctrArray[i] = tokenval

    match("NUM")
    if pass1or2 == 2:
        print("H ", symtable[IdIndex].string, format(startAddress, "06X"), format(totalSize, "06x"))


def body():
    global inst, pass1or2, startLine, lookahead, isBASE, IdIndex

    if lookahead == "ID":
        if pass1or2 == 2:
            inst = 0
        IdIndex = tokenval
        match("ID")
        startLine = False
        rest1()
        body()

    elif lookahead == "f1" or lookahead == "f2" or lookahead == "f3" or lookahead == "+":
        if pass1or2 == 2:
            inst = 0
        rest1()
        body()

    # is it directive? like EQU, ORG, USE
    elif instfile.directive2dircode(lookahead) == 11:
        if pass1or2 == 2:
            inst = 0
        rest1()
        body()


def tail():
    global totalSize, locctrArray, startAddress, inst, literalArray, literalValueASCII, literalIndex
    addressLiteral()
    if pass1or2 == 2:
        for i in range(0, len(literalArray)):
            inst = literalValueASCII[i]
            print("L ", blockType, format(locctrArray[blockType] - 1, '06x'), " 03 ", inst)

            if symtable[literalArray[i]].token == 'STRING':
                locctrArray[blockType] += len(symtable[literalArray[i]].string)

            elif symtable[literalArray[i]].token == 'HEX':
                locctrArray[blockType] += (len(symtable[literalArray[i]].string)) // 2

    literalArray = []
    literalValueASCII = []
    literalIndex = 0

    match("END")
    match("ID")

    # calculate the size of each block
    sizeOfBlocks[0] = locctrArray[0] - startAddress
    sizeOfBlocks[1] = locctrArray[1] - startAddress
    sizeOfBlocks[2] = locctrArray[2] - startAddress

    # calculate the total size
    for i in range(0, len(locctrArray)):
        totalSize += sizeOfBlocks[i]

    if pass1or2 == 2:
        print("E ", format(startAddress, '06x'))


def rest1():
    global locctrArray, inst, startLine

    if lookahead == "f1" or lookahead == "f2" or lookahead == "f3" or lookahead == "+":

        stmt()

    elif lookahead == "WORD" or lookahead == "BYTE" or lookahead == "RESW" or lookahead == "RESB":
        data()

    elif instfile.directive2dircode(lookahead) == 11:
        directive()

    else:
        error("syntax error")


def stmt():
    global locctrArray, inst, pass1or2, startLine, isExtd, isBASE
    ind = tokenval
    startLine = False

    # --------------- Format 1 ------------------------------
    if lookahead == "f1":
        if pass1or2 == 2:
            inst = symtable[tokenval].att
        match("f1")
        locctrArray[blockType] += 1
        if pass1or2 == 2:
            print("T ", blockType, format(locctrArray[blockType] - 1, '06x').upper(), " 01 ",
                  format(inst, '02x').upper())
    # --------------- Format 1 ------------------------------

    # --------------- Format 2 ------------------------------
    elif lookahead == "f2":
        if pass1or2 == 2:
            inst = symtable[tokenval].att << 8
        match("f2")
        if pass1or2 == 2:
            inst += (symtable[tokenval].att << 4)
        match("REG")
        locctrArray[blockType] += 2
        # rest3:
        if lookahead == ",":
            match(",")
            inst += symtable[tokenval].att
            match("REG")
        if pass1or2 == 2:
            print("T ", blockType, format(locctrArray[blockType] - 2, '06x').upper(), " 02 ",
                  format(inst, '04x').upper())

    # --------------- Format 2 ------------------------------

    # --------------- Format 3 ------------------------------
    elif lookahead == "f3":
        # --------------- for RSUB --------------------------
        if symtable[ind].string == 'RSUB':
            match("f3")
            locctrArray[blockType] += 3
        # --------------- for RSUB --------------------------
        else:
            if pass1or2 == 2:
                inst = symtable[tokenval].att << 16
            match("f3")
            locctrArray[blockType] += 3
            rest4()
            if pass1or2 == 2:
                print("T ", blockType, format(locctrArray[blockType] - 3, '06x').upper(), " 03 ",
                      format(inst, '06x').upper())
    # --------------- Format 3 ------------------------------

    # --------------- Format 4 ------------------------------
    elif lookahead == "+":
        isExtd = True
        match("+")
        if pass1or2 == 2:
            inst = symtable[tokenval].att << 24
            inst += Ebit4set
        match("f3")
        if pass1or2 == 2 and lookahead != "#":
            inst += symtable[tokenval].att
        locctrArray[blockType] += 4
        rest4()
        isExtd = False
        if pass1or2 == 2:
            print("T ", blockType, format(locctrArray[blockType] - 4, '06x'), " 04 ", format(inst, '08x'))
    # --------------- Format 4 ------------------------------


def data():
    global locctrArray, inst, startLine
    if lookahead == "WORD":
        match("WORD")
        locctrArray[blockType] += 3
        if pass1or2 == 2:
            inst = tokenval
            print("T ", blockType, format(locctrArray[blockType] - 3, '06x'), " 03 ", format(inst, '06x'))
        startLine = False
        match("NUM")
        startLine = True

    elif lookahead == "RESW":
        match("RESW")
        startLine = False
        locctrArray[blockType] += tokenval * 3
        match("NUM")
        startLine = True

    elif lookahead == "RESB":
        match("RESB")
        startLine = False
        locctrArray[blockType] += tokenval
        match("NUM")
        startLine = True

    elif lookahead == "BYTE":
        match("BYTE")
        startLine = False
        rest2()


def directive():
    global literalIndex, literalArray, literalValueASCII, blockType, isBASE, locctrArray, inst

    # --------------- for EQU --------------------------
    if lookahead == "EQU":
        match("EQU")
        if lookahead == "*":
            symtable[IdIndex].att = locctrArray[blockType]
            match("*")
        else:
            symtable[IdIndex].att = tokenval
            match("NUM")
    # --------------- for BASE --------------------------
    elif lookahead == 'BASE':
        match("BASE")
        isBASE = True
        rest4()

    # --------------- for LTORG --------------------------
    elif lookahead == "LTORG":
        addressLiteral()
        if pass1or2 == 2:
            removeDuplicates()
            for i in range(0, len(literalArray)):
                inst = literalValueASCII[i]
                print("L ", blockType, format(locctrArray[blockType] - 1, '06x'), " 03 ", inst)
                if symtable[literalArray[i]].token == 'STRING':
                    locctrArray[blockType] += len(symtable[literalArray[i]].string)

                elif symtable[literalArray[i]].token == 'HEX':
                    locctrArray[blockType] += (len(symtable[literalArray[i]].string)) // 2
        literalArray = []
        literalValueASCII = []
        literalIndex = 0
        match("LTORG")
    # --------------- for ORG --------------------------
    elif lookahead == "ORG":
        match("ORG")
        if lookahead == "ID":
            if symtable[tokenval].att == -1:
                error("Forward reference is not allowed")
            else:
                locctrArray[blockType] = symtable[tokenval].att
                match("ID")
        elif lookahead == "NUM":
            locctrArray[blockType] = tokenval
            match("NUM")
    # --------------- for USE --------------------------
    elif lookahead == "USE":
        match("USE")
        if lookahead == "CDATA":
            blockType = 1
            match("CDATA")
        elif lookahead == "CBLKS":
            blockType = 2
            match("CBLKS")
        else:
            blockType = 0
            symtable[tokenval].att = locctrArray[blockType]
            symtable[tokenval].btype = blockType

    # --------------------------------------------------
    else:
        error("syntax error")


def rest4():
    global inst, disp, PCrange, base, isLiteral, literalIndex, RTP
    addressMode()
    if lookahead == "ID" or isLiteral:

        if pass1or2 == 2 and not isExtd:

            if symtable[tokenval].att == -1:
                error("varible is not defined")

            if lookahead == "ID" and not isLiteral:

                # normal addressing
                TA = symtable[tokenval].att
                if blockType != symtable[tokenval].btype:
                    RTP = getRelativeToProgram(symtable[tokenval].btype, TA)
                else:
                    RTP = TA
            else:

                # for literal addressing.
                TA = symtable[literalArray[literalIndex]].att
                RTP = getRelativeToProgram(symtable[literalArray[literalIndex]].btype, TA)
                literalIndex = literalIndex + 1

            PC = locctrArray[blockType]
            disp = RTP - PC
            if disp in PCrange:
                # if disp is negative, It's a special case...
                if disp < 0:
                    temp = hex(disp & 0xfff)
                    disp = int(temp, 16)

                inst += Pbit3set
                inst += disp
            elif base is not None and not isExtd:
                # base = symtable[tokenval].att
                disp = TA - base
                inst += disp
                inst += Bbit3set
            else:
                error("PC and base is not applicable")

        if lookahead == "ID" and not isLiteral:
            if isExtd:
                inst += symtable[tokenval].att
            match("ID")

    elif lookahead == "NUM" is not isLiteral:
        if pass1or2 == 2:
            inst += tokenval
        if isBASE:
            base = tokenval
        match("NUM")
    isLiteral = False
    index()


def addressMode():
    global inst, isLiteral, isAddressed
    if lookahead == "@":
        inst += Nbit3set if isExtd is False else Nbit4set
        match("@")

    elif lookahead == "#":
        inst += Ibit3set if isExtd is False else Ibit4set
        match("#")
    elif lookahead == "=":
        isLiteral = True
        match("=")
        literalArray.append(tokenval)
        if pass1or2 == 1:
            isAddressed = False
        inst += Nbit3set if isExtd is False else Nbit4set
        inst += Ibit3set if isExtd is False else Ibit4set

        rest2()
    else:
        inst += Nbit3set if isExtd is False else Nbit4set
        inst += Ibit3set if isExtd is False else Ibit4set


def getRelativeToProgram(blocktybe, TA):
    if blocktybe == 0:
        return TA
    elif blocktybe == 1:
        return TA + sizeOfBlocks[0]
    elif blocktybe == 2:
        return TA + sizeOfBlocks[0] + sizeOfBlocks[1]


def index():
    global inst, pass1or2, Xbit3set, startLine
    if lookahead == ",":
        match(",")
        match("REG")
        if pass1or2 == 2:
            inst += Xbit3set
    startLine = True


def rest2():
    global locctrArray, inst, pass1or2, startLine, literalIndex
    if lookahead == "HEX":

        if not isLiteral:
            locctrArray[blockType] += (len(symtable[tokenval].string) - 1) // 2
            if pass1or2 == 2:
                inst = symtable[tokenval].att
                print("T ", blockType, format(locctrArray[blockType] - 3, '06x').upper(), " 03 ", inst.upper())

        match("HEX")
        startLine = True

    elif lookahead == "STRING":

        if not isLiteral:
            locctrArray[blockType] += len(symtable[tokenval].string) - 1
            if pass1or2 == 2:
                inst = symtable[tokenval].att
                print("T ", blockType, format(locctrArray[blockType] - 3, '06x').upper(), " 03 ", inst.upper())
        match("STRING")
        startLine = True


def main():
    global file, filecontent, locctrArray, pass1or2, bufferindex, lineno, lookahead, literalIndex, blockType
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
        lookahead = lexan()
        parse()
        bufferindex = 0
        locctrArray[blockType] = 0
        lineno = 1
        literalIndex = 0
        blockType = 0
    file.close()


main()
