#include<stdlib.h>
#include<string.h>
#include<stdio.h>
#include<math.h>

typedef struct{
	float* values;
	int size;
}vector;

// 0.01 hz
// float hpf_denom[] = { 1.      ,   -2.99767411,  2.99534915, -0.99767505};
// float hpf_num[] = { 0.99883729, -2.99651186,  2.99651186, -0.99883729};

// [ 1.         -2.98452829  2.96915226 -0.98462372] [ 0.99228803 -2.9768641   2.9768641  -0.99228803]
// 0.1 hz
float hpf_denom[] = {  1.     ,    -2.98452829,  2.96915226, -0.98462372};
float hpf_num[] = {  0.99228803, -2.9768641,   2.9768641,  -0.99228803};

// 0.5 hz
// float hpf_denom[] = { 1.        , -2.94287818,  2.88635027, -0.94345706};
// float hpf_num[] = { 0.97158569, -2.91475706,  2.91475706, -0.97158569};

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
	coeff2.values[0] = 0.1f;
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
	// Use reciprical of windowSize and a multiply!
	float str = sum / windowSize;
	printf("Str %f for size %i\n", str, windowSize);
	return str;
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

float calcDcBias(vector signal) {
	float sum = 0;
	for (int i = 0; i < signal.size; i++) {
		sum += signal.values[i];
	}
	return sum / signal.size;
}

void normalizeOffsetHpf(vector signal) {
	vector num, denom, result;
	num.values = hpf_num;
	num.size = sizeof(hpf_num) / sizeof(float);
	denom.values = hpf_denom;
	denom.size = sizeof(hpf_denom) / sizeof(float);
	result = processSignal(denom, num, signal);
	printf("HPF result has %f remaining bias\n", calcDcBias(result));
	printVector(result, "hpf.txt");
	for (int i = 0; i < result.size; i++) {
		signal.values[i] = result.values[i];
	}
}

void normalizeOffset(vector signal) {
	float offset = calcDcBias(signal);
	for (int i = 0; i < signal.size; i++) {
		signal.values[i] -= offset;
	}
	// printVector(signal, "normalized.txt");
}

void normalizeOffsetFixed(vector signal) {
	float offset = -9.8f;
	for (int i = 0; i < signal.size; i++) {
		signal.values[i] -= offset;
	}
	// printVector(signal, "normalized.txt");
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
	normalizeOffsetHpf(signal);

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