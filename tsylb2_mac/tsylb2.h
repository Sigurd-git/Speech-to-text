#ifndef TSYLB2_H
#define TSYLB2_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

// Basic type definitions
typedef int boolean;
#define T 1
#define F 0

#define MAX_SYMBS_IN_STR 1000
#define WCHAR_T int

// Structures
typedef struct {
    int code;
    // Add other necessary fields
} pcodeset;

struct INTERVAL1 {
    int start;
    int end;
};

struct PRON2 {
    // Add necessary fields
};

struct SYLB1 {
    // Add necessary fields
};

struct WORD1 {
    // Add necessary fields
};

struct PRON_SPEC {
    // Add necessary fields
};

typedef struct {
    int num;
    int rel;
} NUM_REL;

// Function declarations
boolean syllabic(int ch, pcodeset *pcdp);
boolean stress_mark(int i, pcodeset *pcdp);
void nstrcpy(int *dest, int *src);
void db_enter_msg(const char *proc, int level);
void db_leave_msg(const char *proc, int level);
boolean no_word_boundr(WCHAR_T *bnd_int, struct INTERVAL1 cluster, int iwordbound);
boolean no_word_boundl(WCHAR_T *bnd_int, struct INTERVAL1 cluster, int iwordbound);

#endif 