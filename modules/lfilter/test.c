// This is a main entry point for testing in a local computer

#include "structs.h"
#include "filter_util.c"
#include "bpm_filter_chain.c"
#include <stdio.h>
#include <string.h>

#define error(msg, ...) fprintf(stderr, msg, __VA_ARGS__); abort()

char * getLine(FILE* fp) {
    char * line = malloc(100), * linep = line;
    size_t lenmax = 100, len = lenmax;
    int c;

    if(line == NULL)
        return NULL;

    for(;;) {
        c = fgetc(fp);
        if(c == EOF)
            break;

        if(--len == 0) {
            len = lenmax;
            char * linen = realloc(linep, lenmax *= 2);

            if(linen == NULL) {
                free(linep);
                return NULL;
            }
            line = linen + (line - linep);
            linep = linen;
        }

        if((*line++ = c) == '\n')
            break;
    }
    *line = '\0';
    return linep;
}

vector loadSignal(char* fileName) {
	FILE* fp = fopen(fileName,"r");
	int size = 0;
	vector signal;
	// Do it twice, once for size…
	char* line;
	for (;;) {
		line = getLine(fp);
		if (line != NULL && strlen(line) > 0) {
			size++;
			free(line);
		} else {
			if (line == NULL) free(line);
			break;
		}
	}
	printf("Got %i lines\n", size);
	fclose(fp);
	signal.size = size;
	signal.values = (float*) calloc(size, sizeof(float));
	fp = fopen(fileName,"r");
	for (int i = 0; i < size; i++) {
		line = getLine(fp);
		signal.values[i] = atof(line);
		free(line);
	}
	printf("Loaded %i samples\n", size);
	fclose(fp);
	return signal;
}

void printVector(vector v, char* outputFile){
	int i;
	
	if(outputFile==NULL){
		// printf("[");
		for(i=0;i<v.size;i++)
			printf("%.12f\n",v.values[i]);
		// printf("\b\b]");
	}
	
	else{
		FILE* fp = fopen(outputFile,"w");
		for(i=0;i<v.size;i++)
			fprintf(fp, "%.12f\n",v.values[i]);
		fclose(fp);
	}
	
}

int main(int argC,char* argV[])
{
	// char *str;
	// if(argC != 3)
	// 	printf("Usage : %s <dataFile> <sampleRate>",argV[0]);
	// else{
	// 	int sampleRate = atoi(argV[2]);
	// 	if (! (sampleRate > 0)) {
	// 		printf("Invalid sample rate %i\n", sampleRate);
	// 		return 1;
	// 	}
	// 	processSignalFile(argV[1], sampleRate);
	// }
    init(100,190, 200);
    combFilterSet *filters = getCombFilterSet();
    printf("Got filters starting with size %i and count %i\n", filters->firstFilterSize, filters->filterCount);
    int firstFilterSize = filters->firstFilterSize;
    for (int i = 0; i < filters->filterCount; i++) {
        int filterSize = filters->firstFilterSize + i;
        int stateSize = getFilter(filterSize, filters)->state.size;
        if(stateSize != filterSize) {
            error("Filter target size %i doesn't match filter state size %i\n", filterSize, stateSize);
        }
    }
    puts("All filters correct size\n");

    printVector(getHpfFilter()->denomCoeffs, "/tmp/denomCoeffs");
    printVector(getHpfFilter()->numCoeffs, "/tmp/numCoeffs");

    if (argC > 1) {
        vector signal = loadSignal(argV[1]);
        printf("Loaded signal with %i samples\n", signal.size);
        // for (int i = 0; i < 100; i++) {
        //     strengthResult best = updateFilterChain(signal.values[i]);
        // }
        for (int i = 0; i < signal.size; i++) {
            strengthResult best = updateFilterChain(signal.values[i]);
            printf("At sample %i best strength is %f at size %i\n", i, best.strength, best.filterSize);
        }
    }
    // printVector(getCombFilterSet()->combFilters[0].state, "/tmp/combFilterState.txt");
    printVector(getHpfFilter()->state, "/tmp/hpf.txt");
	return 0;
}