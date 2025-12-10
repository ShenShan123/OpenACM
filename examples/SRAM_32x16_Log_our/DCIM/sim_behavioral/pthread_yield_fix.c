// File Name: pthread_yield_fix.c
#define _GNU_SOURCE
#include <sched.h>

int pthread_yield(void) {
    return sched_yield();
}
//Compile with the command:gcc -c pthread_yield_fix.c -o pthread_yield_fix.o