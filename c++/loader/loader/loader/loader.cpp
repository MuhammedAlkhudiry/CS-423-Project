#define _CRT_SECURE_NO_WARNINGS
#define EOF -1

#include<iostream>
#include <random>

//#include<fstream>
//using namespace std;
//using std::ifstream;

//open file
FILE* file = fopen("objectCode.txt", "r");

//skip spaces when reading from file
char getCharacter();
int main();
//read the address, consist of 3 bytes
int readAddress();
//calculate the value of the given number of bytes
int getByteValue(int numberOfBytes = 1);

int generateRandomStart(int);

int main()
{
	bool sic = true;	//else , sic/xe
	int memorySize;
	char lookahead;
	int header_startAddress;
	int end_startAddress;
	int programSize;

	//define the size based on arcticture
	{
		if (sic)
		{
			memorySize = int(pow(2, 15));
		}
		else	//sicxe
		{
			memorySize = int(pow(2, 20));
		}
	}

	//initialze memory allocation
	char* memory = (char*)malloc(memorySize);
	char* ptr = memory;


	//read file
	{
		lookahead = getCharacter();

		while (lookahead != EOF)
		{

			//read header line
			if (toupper(lookahead) == 'H')
			{
				//read next character and skip the spaces
				lookahead = getCharacter();

				//skip the program name
				while (isalpha(lookahead))
				{
					//read next character
					lookahead = getc(file);
				}

				//read start address
				header_startAddress = readAddress();

				//read program size
				programSize = readAddress();	//program size has the same number of bits as the address
			}

			// forbiddenLocation = the bottom of the memory
			int forbiddenLocation = memorySize - programSize;
			int givenLocation = generateRandomStart(forbiddenLocation);
			ptr += givenLocation;

			// save the starting point of the program for later use
			char* startPtr = ptr;

			lookahead = getCharacter();

			//read text record
			while (toupper(lookahead) == 'T')
			{
				//read Address of instruction | potential of relocation
				int instructionAddress = readAddress();

				//read size of instructions
				int sizeOfInstruction = getByteValue();

				//write into memory
				for (; sizeOfInstruction > 0; sizeOfInstruction--, ptr++)
				{
					char byte = getByteValue();

					*ptr = byte;

				}

				lookahead = getCharacter();
			}

			// mod...

			while (toupper(lookahead) == 'M')
			{
				//e.g: M [000000] 05
				int modLocation = readAddress();

				//e.g: M 000000 [05]
				int length = getByteValue();

				int oldAddress = 0;
				char* modPtr = startPtr;
				modPtr += modLocation;

				char* oldAddressPtr = modPtr;
				int bytes[3];
				int disp = startPtr - memory;

				for (int i = 0; i < 3; i++, oldAddressPtr++)
				{
					bytes[i] = *oldAddressPtr;

				}

				int inst = bytes[0] << 16;
				inst += bytes[1] << 8;
				inst += bytes[2];

				inst = inst + (disp & 0xfffff);

				char* newAddressPtr = modPtr;

				*newAddressPtr++ = (inst & 0xff0000) >> 16;
				*newAddressPtr++ = (inst & 0xff00) >> 8;
				*newAddressPtr = inst & 0xff;

				lookahead = getCharacter();
			}


			if (toupper(lookahead) == 'E') {

				getCharacter();
				end_startAddress = readAddress();
				lookahead = getCharacter();


			}
		}
	}

	return 0;
}

int readAddress()
{
	return getByteValue(3);
}

int getByteValue(int numberOfBytes)
{
	int address = NULL;	//store the address
	char token;

	for (int shiftBits = (numberOfBytes * 8) - 4; shiftBits >= 0; shiftBits -= 4)
	{
		//read next character from file
		token = getCharacter();

		//read digit
		if (isdigit(token))
		{
			address += (token - '0') << shiftBits;
		}

		//read alphabit[10->15|A->F]
		else if (toupper(token) >= 'A' && toupper(token) <= 'F')
		{
			address += (10 + toupper(token) - 'A') << shiftBits;
		}
	}
	return address;

}

char getCharacter()
{
	char token = getc(file);
	while (token == ' ' || token == '\t' || token == '\n')
	{
		token = getc(file);
	}

	return token;
}

int generateRandomStart(int forbiddenLocation) {

	std::random_device rd;
	std::mt19937 gen(rd());

	std::uniform_int_distribution<> dis(0, forbiddenLocation);

	int start = dis(gen);
	return start;
}