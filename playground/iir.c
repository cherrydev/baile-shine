#include<stdlib.h>
#include<string.h>
#include<stdio.h>
#include<math.h>

typedef struct{
	float* values;
	int size;
}vector;

float hpf_denom[] = { 1.        , -2.94287818,  2.88635027, -0.94345706};
float hpf_num[] = { 0.97158569, -2.91475706,  2.91475706, -0.97158569};

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

vector extractVector(char* str){
	vector coeff;
	int i=0,count = 1;
	char *token, *stopstring;
	
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

vector makeCombFilterCoeff1(int combSampleSize) {
	vector coeff1;
	coeff1.values = (float*)calloc(combSampleSize, sizeof(float));
	coeff1.size = combSampleSize;
	coeff1.values[combSampleSize - 1] = -0.9f;
	coeff1.values[0] = 1.0f;
	return coeff1;
}

vector makeCombFilterCoeff2() {
	vector coeff2;
	coeff2.values = (float*)calloc(1, sizeof(float));
	coeff2.values[0] = 1.0f;
	coeff2.size = 1;
	return coeff2;
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



float calculateStrength(vector filteredSignal, int windowSize) {
	float sum = 0.0f;
	for (int i = filteredSignal.size - windowSize - 1; i < filteredSignal.size; i++) {
		sum += fabsf(filteredSignal.values[i]);
	}
	float str = sum / windowSize;
	printf("Str %f for size %i\n", str, windowSize);
	return str;

	// float sum = 0.0f;
	// for (int i = 0; i < filteredSignal.size; i++) {
	// 	sum += fabsf(filteredSignal.values[i]);
	// }
	// float str = sum / filteredSignal.size;
	// printf("Str %f for size %i\n", str, windowSize);
	// return str;
}

vector processSignal(vector coeff1, vector coeff2, vector signal) {
	int i,j;
	float sum;
	vector filteredSignal;

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
	
	return filteredSignal;
}

void normalizeOffset(vector signal) {
	// float sum = 0;
	// for (int i = 0; i < signal.size; i++) {
	// 	sum += signal.values[i];
	// }
	// float offset = sum / signal.size;
	// printf("Normalizing with offset %f (%.5f / %i)\n", offset, sum, signal.size);
	// for (int i = 0; i < signal.size; i++) {
	// 	signal.values[i] -= offset;
	// }
	// printVector(signal, "normalized.txt");
	vector num, denom, result;
	num.values = hpf_num;
	num.size = sizeof(hpf_num) / sizeof(float);
	denom.values = hpf_denom;
	denom.size = sizeof(hpf_denom) / sizeof(float);
	result = processSignal(denom, num, signal);
	printVector(result, "hpf.txt");
	signal.values = result.values;
}

int findBestFitCombFilter(vector signal, int combSizeMin, int combSizeMax) {
	vector coeff1, coeff2, filteredSample;

	coeff2 = makeCombFilterCoeff2();

	float bestStrength = 0.0f;
	int bestStrengthCombSize = -1;
    
	for (int combSize = combSizeMin; combSize <= combSizeMax; combSize++) {
		coeff1 = makeCombFilterCoeff1(combSize);
		vector filteredSample = processSignal(coeff1, coeff2, signal);
		// if (combSize == 44) {
		// 	printVector(filteredSample, NULL);
		// }
		float strength = calculateStrength(filteredSample, combSize);
		if (strength > bestStrength) {
			bestStrength = strength;
			bestStrengthCombSize = combSize;
		}
		free(coeff1.values);
		free(filteredSample.values);
	}
	printf("Best strength is %f for comb size %i\n",
		bestStrength,
		bestStrengthCombSize
	);
	free(coeff2.values);
	return bestStrengthCombSize;
}

int processSignalFile(char* fileName, int sampleRate){
	vector signal;

	signal = loadSignal(fileName);
	normalizeOffset(signal);

	int minBpm = 100;
	int maxBpm = 250;

	int combSizeMin = sampleRate / (maxBpm / 60.0f) + 1;
	int combSizeMax = sampleRate / (minBpm / 60.0f) + 1;
	
	int bestStrengthCombSize = findBestFitCombFilter(signal, combSizeMin, combSizeMax);

	printf("Best fit bpm is %.2f\n", (((float)sampleRate)/ ((float)bestStrengthCombSize - 1)) * 60.0f);

	return bestStrengthCombSize;
}



int main(int argC,char* argV[])
{
	char *str;
	if(argC != 3)
		printf("Usage : %s <dataFile> <sampleRate>",argV[0]);
	else{
		int sampleRate = atoi(argV[2]);
		if (! (sampleRate > 0)) {
			printf("Invalid sample rate %i\n", sampleRate);
			return 1;
		}
		processSignalFile(argV[1], sampleRate);
	}
	return 0;
}