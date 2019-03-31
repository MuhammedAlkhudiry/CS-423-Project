#include <iostream>
#include <stdlib.h>
#include <stdio.h>
using namespace std;

int main()
{

   char *str;

   /* Initial memory allocation */
   str = (char *) malloc(177775);
   printf("String = %s,  Address = %u\n", str, str);

    return 0;
}
