#pragma once
#include "filter_util.h"

void init(float minBpm, float maxBpm, int sampleRate, float filterStrength);
strengthResult findBestStrength();
strengthResult updateFilterChain(float sample);