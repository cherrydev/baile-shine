#pragma once
typedef struct{
	float* values;
	int size;
}vector;

typedef struct{
	vector denomCoeffs;
	/*
	  The filter implementation finishes each round by dividing the sum by the first value of the denom coeffs.
	  Multiply by reciprocal instead
	*/
	float denomZeroReciprocal;
	float stateSizeReciprocal;
	vector numCoeffs;
	vector state;
}iirFilter;

typedef struct{
	float strength;
	float sizeReciprocal;
	int size;
	vector state;
}combFilter;

typedef struct{
	combFilter *combFilters;
	int firstFilterSize;
	int filterCount;
}combFilterSet;

typedef struct{
	int filterSize;
	float strength;
}strengthResult;