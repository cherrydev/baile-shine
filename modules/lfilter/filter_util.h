#pragma once
#include "structs.h"
#include <stdlib.h>

#define max(a,b) (a >= b) ? a : b
#define min(a,b) (a <= b) ? a : b

iirFilter newIirFilter(int stateSize, vector denomCoeffs, vector numCoeffs);

vector newVector(int size);

combFilterSet newCombFilterSet(int firstFilterSize, int filterCount, float strength);

strengthResult newStrengthResult(int filterSize, float strength);

combFilter* getFilter(int filterSize, combFilterSet *combFilters);

void insertSample(vector *samples, float newSample);

void updateFilter(iirFilter* filter, vector *parentState);

void updateCombFilter(combFilter* filter, vector *parentState);

vector makeCombFilterDenom(int combSampleSize, float filterStrength);

vector makeCombFilterNum(float filterStrength);

float bpmFromCombSize(int combSize, int sampleRate);

int combSizeFromBpm(float bpm, int sampleRate);

float calculateStrength(vector filteredSignal, int windowSize, float windowSizeReciprocal);