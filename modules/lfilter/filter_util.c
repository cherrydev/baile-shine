
#include "filter_util.h"
#include <stdio.h>
#include <math.h>

iirFilter newIirFilter(int stateSize, const vector denomCoeffs, const vector numCoeffs) {
    float numZeroReciprocal = 1 / numCoeffs.values[0];
    iirFilter newFilter = {
        .state = newVector(stateSize),
        .denomCoeffs = denomCoeffs,
        .numCoeffs = numCoeffs,
        .numZeroReciprocal = numZeroReciprocal,
        .stateSizeReciprocal = 1.0f / stateSize
    };
    return newFilter;
}

vector newVector(int size) {
    return (vector) {
        .size = size,
        .values = (float*) calloc(size, sizeof(float))
    };
}

combFilterSet newCombFilterSet(int firstFilterSize, int filterCount) {
    combFilterSet result = {
        .firstFilterSize = firstFilterSize,
        .filterCount = filterCount,
        .combFilters = calloc(filterCount, sizeof(iirFilter))
    };
    for (int i = 0; i < filterCount; i++) {
        int filterSize = firstFilterSize + i;
        result.combFilters[i] = newIirFilter(filterSize, newVector(filterSize), newVector(1));
    }
    return result;
}

strengthResult newStrengthResult(int filterSize, float strength) {
    return (strengthResult) {
        .filterSize = filterSize,
        .strength = strength
    };
}

iirFilter* getFilter(int filterSize, combFilterSet *combFilters) {
    int largestFilter = combFilters->filterCount - 1;
    if (filterSize > combFilters->firstFilterSize + largestFilter) {
        fprintf(stderr, "Invalid filter size %i. Largest filter is %i\n", filterSize, largestFilter);
        abort();
    }
    return &combFilters->combFilters[filterSize - combFilters->firstFilterSize];
}

void insertSample(vector *samples, float newSample) {
    float temp;

    // Advance [1] to [0], then [2] to [1], etc. Discard original [0]
    for(int i = 1; i < samples->size; i++) {
        samples->values[i - 1] = samples->values[i];
    }
    samples->values[samples->size - 1] = newSample;
}

void updateFilter(iirFilter* filter, vector *parentState) {
    int newStateSampleIdx, newParentSampleIdx, j;
	float sum = 0.0f;
    
    // Advance the filter state by one sample
    insertSample(&filter->state, 0.0f);
    newStateSampleIdx = filter->state.size - 1;
    newParentSampleIdx = parentState->size - 1;
    // printf("Last sample in state is %f\n", filter->state.values[newStateSampleIdx]);
    // printf("Second last sample in state is %f\n", filter->state.values[newStateSampleIdx-1]);
    for(j=0;j<filter->numCoeffs.size;j++){
        int currentParentSampleIdx = newParentSampleIdx-j;
        if(currentParentSampleIdx>=0) {
            sum += filter->numCoeffs.values[j]*parentState->values[currentParentSampleIdx];
            // printf("numCoef[%i](%f) * parent[%i](%f) = ")
            // printf("with num[%i]=[%f] calculating from parent[%i] Sum is now %f\n",
            //  j, numCoeffs.values[j], currentParentSampleIdx, sum
            //  );
        }
        else {
            break;
        }
    }
    
    for(j=0;j<filter->denomCoeffs.size;j++){
        int currentStateSampleIdx = newStateSampleIdx-j;
        if(currentStateSampleIdx>=0) {
            sum -= filter->denomCoeffs.values[j]*filter->state.values[currentStateSampleIdx];
            // printf("with denom[%i] calculating from parent[%i]. Sum is now %f\n",
            //  j, currentStateSampleIdx, sum
            //  );
        }
        else {
            break;
        }
    }
    sum /= filter->denomCoeffs.values[0]; // recriprocal
    // printf("Setting state %i/%i to %f\n", newStateSampleIdx, filter->state.size - 1, sum);
    filter->state.values[newStateSampleIdx] = sum;
    // filter->state.values[i] = sum * filter->numZeroReciprocal;
}


float bpmFromCombSize(int combSize, int sampleRate) {
    return ((float)combSize - 1) / (float)sampleRate * 60.0f;
}

int combSizeFromBpm(float bpm, int sampleRate) {
    return roundf(sampleRate / (bpm / 60.0f) + 1);
}

float calculateStrength(vector filteredSignal, int windowSize, float windowSizeReciprocal) {
	float sum = 0.0f;
	for (int i = filteredSignal.size - windowSize; i < filteredSignal.size; i++) {
		sum += fabsf(filteredSignal.values[i]);
	}
	// Use reciprical of windowSize and a multiply!
	float str = sum * windowSizeReciprocal;
	// printf("Str %f for size %i\n", str, windowSize);
	return str;
}