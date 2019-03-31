def main():
    file = open('objectCode', 'r')
    fileString = file.read()

    fileString = ''.join(fileString.split())

    fileContent = list(fileString)
    lengthAsString = ""
    i = 0
    fileBinary = ""
    lineno = 0
    startAddressString = ""
    modArray = []

    while i in range(0, len(fileContent)):

        if fileContent[i] == "H":
            i += 1
            while fileContent[i].isalpha():
                i += 1
            for i in range(i, i + 12):
                fileBinary += str(bin(int(fileContent[i], 16))[2:])
            i += 1
            lineno += 1

        elif fileContent[i] == "T":
            while fileContent[i] == "T":
                i += 1
                lineno += 1
                for i in range(i, i + 6):
                    fileBinary += str(bin(int(fileContent[i], 16))[2:])
                i += 1

                for i in range(i, i + 2):
                    fileBinary += str(bin(int(fileContent[i], 16))[2:])
                    lengthAsString += fileContent[i]
                i += 1

                length = int(lengthAsString, 16) * 2
                lengthAsString = ""

                for i in range(i, i + length):
                    fileBinary += str(bin(int(fileContent[i], 16))[2:])
                i += 1

        elif fileContent[i] == "M":
            while fileContent[i] == "M":
                i += 1
                lineno += 1

                for i in range(i, i + 6):
                    fileBinary += str(bin(int(fileContent[i], 16))[2:])
                    startAddressString += fileContent[i]
                i += 1

                modArray.append(int(startAddressString, 16))
                startAddressString = ""

                for i in range(i, i + 2):
                    fileBinary += str(bin(int(fileContent[i], 16))[2:])
                    i += 1

        elif fileContent[i] == "E":
            i += 1
            for i in range(i, i + 6):
                fileBinary += str(bin(int(fileContent[i], 16))[2:])
            i += 1
            lineno += 1

    print(fileBinary)


main()
