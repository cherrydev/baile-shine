#import "filter_util.h"

static float HPF_DENOM_SAMPLES[] = {  1.     ,    -2.98452829,  2.96915226, -0.98462372};
// static float HPF_DENOM_SAMPLES[] = {  -0.98462372, 2.96915226,  -2.98452829, 1.0};
static float HPF_NUM_SAMPLES[] = {  0.99228803, -2.9768641,   2.9768641,  -0.99228803};
// static float HPF_NUM_SAMPLES[] = { -0.99228803, 2.9768641, -2.9768641, 0.99228803 };

static const vector HPF_DENOM = {
    .size = sizeof(HPF_DENOM_SAMPLES) / sizeof(float),
    .values = HPF_DENOM_SAMPLES
};

static const vector HPF_NUM = {
    .size = sizeof(HPF_NUM_SAMPLES) / sizeof(float),
    .values = HPF_NUM_SAMPLES
};

static vector inputBuffer;
static iirFilter hpfFilter;
static combFilterSet combFilters;
static int systemSampleRate;

// debugging
combFilterSet* getCombFilterSet() { return &combFilters; }
iirFilter* getHpfFilter() { return &hpfFilter; }
int getSystemSampleRate() { return systemSampleRate; }
vector* getInputBuffer() { return &inputBuffer; }
// end

void init(float minBpm, float maxBpm, int sampleRate) {
    systemSampleRate = sampleRate;
    int combSizeMin = combSizeFromBpm(maxBpm, sampleRate);
	int combSizeMax = combSizeFromBpm(minBpm, sampleRate);
    printf("Initting with bpms %.1f-%.1f, sample rate %ihz, comb sizes %i-%i\n",
        minBpm, maxBpm, sampleRate, combSizeMin, combSizeMax
    );
    inputBuffer = newVector(combSizeMax);
    hpfFilter = newIirFilter(
        combSizeMax, 
        HPF_DENOM, 
        HPF_NUM
    );
    combFilters = newCombFilterSet(combSizeMin, combSizeMax - combSizeMin + 1);
}

strengthResult findBestStrength() {
    strengthResult bestResult = {.strength = 0, .filterSize = 0};
    for (int i = 0; i < combFilters.filterCount; i++) {
        float strength = calculateStrength(
            combFilters.combFilters[i].state,
            combFilters.combFilters[i].state.size,
            combFilters.combFilters[i].stateSizeReciprocal
        );
        if (strength > bestResult.strength) {
            bestResult.strength = strength;
            bestResult.filterSize = combFilters.combFilters[i].state.size;
        }
    }
    return bestResult;
}

strengthResult updateFilterChain(float sample) {
    insertSample(&inputBuffer, sample);
    updateFilter(&hpfFilter, &inputBuffer);
    for (int i = 0; i < combFilters.filterCount; i++) {
        updateFilter(&combFilters.combFilters[i], &hpfFilter.state);
    }
    return findBestStrength();
}