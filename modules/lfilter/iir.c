#include<stdlib.h>
#include<string.h>
#include<stdio.h>
#include "iir.h"

#define MAX_LEN 1000

float coeff1_a[] = {1.00000000, -2.77555756e-16, 3.33333333e-01, -1.85037171e-17};
float coeff2_a[] = {0.16666667, 0.5, 0.5, 0.16666667};
float values_a[] = {-0.917843918645, 0.141984778794, 1.20536903482, 0.190286794412, -0.662370894973, -1.00700480494, -0.404707073677, 0.800482325044, 0.743500089861, 1.01090520172, 0.741527555207, 0.277841675195, 0.400833448236, -0.2085993586, -0.172842103641, -0.134316096293, 0.0259303398477, 0.490105989562, 0.549391221511, 0.9047198589};

vector extractVector(char* str){
	vector coeff;
	int i=0,count = 1;
	char *token;
	
	while(str[i]!=00){
		if(str[i++]==' ')
			count++;
	}
	
	coeff.values = (float*)malloc(count*sizeof(float));
	coeff.size = count;
	
	token = strtok(str," ");
	
	i = 0;
	
	while(token!=NULL){
		coeff.values[i++] = (float) atof(token);
		token = strtok(NULL," ");
	}
	
	return coeff;
}

vector processSignalFile(){
	int i,j;
	float sum;
	char str[MAX_LEN];
	vector coeff1,coeff2,signal,filteredSignal;

	// FILE* fp = fopen(fileName,"r");
	
	// fgets(str,MAX_LEN,fp);
	// coeff1 = extractVector(str);
	
	// fgets(str,MAX_LEN,fp);
	// coeff2 = extractVector(str);
	
	// fgets(str,MAX_LEN,fp);
	// signal = extractVector(str);

    //     fclose(fp);
    coeff1.values = coeff1_a;
    coeff1.size = sizeof(coeff1_a) / sizeof(float);

    coeff2.values = coeff2_a;
    coeff2.size = sizeof(coeff2_a) / sizeof(float);

    signal.values = values_a;
    signal.size = sizeof(values_a) / sizeof(float);
	
	filteredSignal.values = (float*)calloc(signal.size,sizeof(float));
	filteredSignal.size = signal.size;
	
	for(i=0;i<signal.size;i++){
		sum = 0;
		
		for(j=0;j<coeff2.size;j++){
			if(i-j>=0)
				sum += coeff2.values[j]*signal.values[i-j];
		}
		
		for(j=0;j<coeff1.size;j++){
			if(i-j>=0)
				sum -= coeff1.values[j]*filteredSignal.values[i-j];
		}
		sum /= coeff1.values[0];
		filteredSignal.values[i] = sum;
	}

    printVector(filteredSignal);
	
	return filteredSignal;
}

void printVector(vector v){
	int i;
	
	printf("[");
    for(i=0;i<v.size;i++)
        printf("%.12f, \n",v.values[i]);
    printf("\b\b]");
	
}