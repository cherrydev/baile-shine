// This is a main entry point for testing in a local computer

#include <algorithm>
#include <array>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <string>

#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdlib.h>

using std::int32_t;

template <int32_t BufSize>
class SignalSource {
public:
	static constexpr int32_t buf_size = BufSize;

	class Range {
	public:
		Range(std::array<float, BufSize> const & a_buf, int32_t a_origin, int32_t a_cur)
				: _buf(a_buf),
#ifndef NDEBUG
				_origin(a_origin),
#endif
				_cur(a_cur) {
			assert_self_okay();
		}

#ifndef NDEBUG
		void assert_self_okay() const {
			assert(_origin >= 0);
			assert(_origin < BufSize);
			assert(_cur >= 0);
			assert(_cur < BufSize);
		}

		void assert_n_okay(int32_t n) const {
			assert_self_okay();
			if (n > 0) {
				assert(BufSize - (_cur + BufSize - _origin) % BufSize > n);
			} else if (n < 0) {
				assert((_cur + BufSize - _origin) % BufSize >= -n);
			}
		}
#else
		void assert_self_okay() { }
		void assert_n_okay(int32_t n) { }
#endif

		float operator *() const {
			assert_self_okay();
			return _buf[_cur];
		}

		float operator [](int32_t n) const {
			assert_n_okay(n);
			int32_t a_cur = _cur + n;
			if (a_cur > BufSize) {
				a_cur -= BufSize;
			}
			return _buf[a_cur];
		}

		Range operator +(int32_t n) const {
			assert_n_okay(n);
			int32_t a_cur = _cur + n;
			if (a_cur > BufSize) {
				a_cur -= BufSize;
			}
			return Range(_buf, a_cur);
		}

		Range operator -(int32_t n) const {
			assert_n_okay(-n);
			int32_t a_cur = _cur + BufSize - n;
			if (a_cur > BufSize) {
				a_cur -= BufSize;
			}
			return Range(_buf, a_cur);
		}

		Range & operator +=(int32_t n) {
			assert_n_okay(n);
			int32_t a_cur = _cur + n;
			if (a_cur > BufSize) {
				a_cur -= BufSize;
			}
			_cur = a_cur;
			return *this;
		}

		Range & operator -=(int32_t n) {
			assert_n_okay(-n);
			int32_t a_cur = _cur + BufSize - n;
			if (a_cur > BufSize) {
				a_cur -= BufSize;
			}
			_cur = a_cur;
			return *this;
		}

		Range & operator ++() {
			assert_n_okay(1);
			++_cur;
			if (_cur >= BufSize) {
				_cur = 0;
			}
			return *this;
		}

		Range & operator --() {
			assert_n_okay(-1);
			if (_cur == 0) {
				_cur = BufSize;
			}
			--_cur;
			return *this;
		}

		Range operator ++(int) {
			auto result = *this;
			++*this;
			return result;
		}

		Range operator --(int) {
			auto result = *this;
			--*this;
			return result;
		}

	private:
		std::array<float, BufSize> const & _buf;
#ifndef NDEBUG
		int32_t _origin;
#endif
		int32_t _cur;
	};

	SignalSource() : _buf_head(0) {
		std::fill(_buf.begin(), _buf.end(), 0.0f);
	}

	Range range(int32_t n) const {
		assert(n >= 0);
		assert(n < buf_size);

		int32_t pos = _buf_head + n;
		while (pos >= buf_size) {
			pos -= buf_size;
		}
		return Range(_buf, _buf_head, pos);
	}

	float at(int32_t n) const {
		assert(n >= 0);
		assert(n < buf_size);

		int32_t pos = _buf_head + n;
		while (pos >= buf_size) {
			pos -= buf_size;
		}
		return _buf[pos];
	}

protected:
	int32_t _buf_head;
	std::array<float, buf_size> _buf;

	void add_sample(float sample) {
		int32_t head = _buf_head;

		assert(head < buf_size);
		assert(head >= 0);

		if (head == 0) {
			head = buf_size;
		}
		--head;
		_buf[head] = sample;
		_buf_head = head;
	}
};

template <int32_t BufSize>
class FileSource : public SignalSource<BufSize> {
public:
	using SignalSource<BufSize>::buf_size;

	FileSource(char const * filename) {
		_in_file.open(filename, std::ios::in);
		std::fill(SignalSource<BufSize>::_buf.begin(), SignalSource<BufSize>::_buf.end(), -9.8f);
	}

	bool valid() {
		return !_in_file.bad();
	}

	int32_t process(int32_t n) {
		for (int32_t i = 0; i < n; ++i) {
			float sample = at(0);
			if(!(_in_file.bad() || _in_file.eof())) {
				_in_file >> sample;
			}
			add_sample(sample);
		}
		return n;
	}

	using SignalSource<BufSize>::at;
	using SignalSource<BufSize>::range;

private:
	std::ifstream _in_file;

	using SignalSource<BufSize>::add_sample;
};


template <int32_t BufSize, int32_t CoeffsSize>
class IirFilter : public SignalSource<BufSize> {
public:
	using SignalSource<BufSize>::buf_size;
	static constexpr int32_t coeffs_size = CoeffsSize;

	IirFilter(std::array<float, coeffs_size> const & a_b_coeffs,
			std::array<float, coeffs_size> const & a_a_coeffs)
			: _b_coeffs(a_b_coeffs), _a_coeffs(a_a_coeffs) {
		// for(int i = 0; i < coeffs_size; ++i) { 
		// 	std::cout << i << ": b=" << _b_coeffs[i] << ", a=" << _a_coeffs[i] << std::endl;
		// }
	}

	template<class TPrevSource>
	int32_t process(TPrevSource const * source, int32_t n) {
		for(int32_t j = n; j > 0; --j) {
			auto p = source->range(j - 1);
			float y = *p * _b_coeffs[0];
			++p;
			auto q = range(0);
			for(int32_t i = 1; i < coeffs_size; ++i) {
				y += *(p++) * _b_coeffs[i] - *(q++) * _a_coeffs[i];
			}
			add_sample(y);
		}
		return n;
	}

	using SignalSource<BufSize>::at;
	using SignalSource<BufSize>::range;

private:
	std::array<float, coeffs_size> _b_coeffs;
	std::array<float, coeffs_size> _a_coeffs;

	using SignalSource<BufSize>::add_sample;
};


template<int32_t BufSize, int32_t ExtraBuf, int32_t SampleFreq, int32_t LowBpm, int32_t HighBpm>
struct IirCombFilterRange;


template <int32_t BufSize>
class IirCombFilter: public SignalSource<BufSize> {
public:
	using SignalSource<BufSize>::buf_size;

	IirCombFilter() {
	}

	IirCombFilter(int32_t a_filter_period, int32_t a_filter_decimation, float a_filter_q) {
		set_parameters(a_filter_period, a_filter_decimation, a_filter_q);
	}

	void set_parameters(int32_t a_filter_period, int32_t a_filter_decimation, float a_filter_q) {
		_filter_period = a_filter_period;
		_filter_decimation = a_filter_decimation;
		_filter_q = a_filter_q;
		_filter_1_minus_q_over_decimation = (1.0f - a_filter_q) / a_filter_decimation;
		_decimation_frac = 0;
		_y = 0.0f;
	}

	template<class TPrevSource>
	int32_t process(TPrevSource const * source, int32_t n) {
		int32_t out_n = 0;
		for(int32_t j = n; j > 0; --j) {
			if (_decimation_frac == 0) {
				_y = at(_filter_period) * _filter_q;
			}
			_y += source->at(j - 1) * _filter_1_minus_q_over_decimation;
			++_decimation_frac;
			if(_decimation_frac == _filter_decimation) {
				add_sample(_y);
				++out_n;
				_decimation_frac = 0;
			}
		}
		return out_n;
	}

	using SignalSource<BufSize>::at;
	using SignalSource<BufSize>::range;

	int32_t filter_period() const { return _filter_period; }
	int32_t filter_decimation() const { return _filter_decimation; }

private:
	int32_t _filter_period;
	int32_t _filter_decimation;
	float _filter_q;
	float _filter_1_minus_q_over_decimation;
	int32_t _decimation_frac;
	float _y;

	using SignalSource<BufSize>::add_sample;
};


template <int32_t BufSize>
class WindowedPowerCalculator : public SignalSource<BufSize> {
public:
	using SignalSource<BufSize>::buf_size;

	explicit WindowedPowerCalculator() {
	}

	explicit WindowedPowerCalculator(int32_t a_window_size, float a_window_q = 0.9999f) {
		set_parameters(a_window_size, a_window_q);
	}

	void set_parameters(int32_t a_window_size, float a_window_q = 0.9999f) {
		_window_size = a_window_size;
		_window_q = a_window_q;
	}

	template<class TPrevSource>
	int32_t process(TPrevSource const * source, int32_t n) {
		for(int32_t j = n; j > 0; --j) {
			float window_new_val = source->at(j - 1);
			float window_new_power = window_new_val * window_new_val;
			float window_old_val = source->at(j - 1 + _window_size);
			float window_old_power = window_old_val * window_old_val;
			_cur_power += window_new_power - window_old_power;
			// Make sure any accumulated error diminishes over time
			if(!(_cur_power > 0.0f)) {
				_cur_power = 0.0f;
			} else {
				_cur_power *= _window_q;
			}
			add_sample(_cur_power);
		}
		return n;
	}

	float cur_power() const { return _cur_power; }

	using SignalSource<BufSize>::at;
	using SignalSource<BufSize>::range;

private:
	int32_t _window_size;
	float _window_q;
	float _cur_power;

	using SignalSource<BufSize>::add_sample;
};


template<int32_t BufSize, int32_t ExtraBuf, int32_t SampleFreq, int32_t LowBpm, int32_t HighBpm>
struct IirCombFilterRangeUtil {
	static constexpr int32_t buf_size = BufSize;
	static constexpr int32_t extra_buf = ExtraBuf;
	static constexpr float sample_freq = SampleFreq;
	static constexpr float lowest_bpm = LowBpm;
	static constexpr float highest_bpm = HighBpm;

	static constexpr int32_t calc_decimation(int32_t filter_period) {
		constexpr int32_t buf_remain = buf_size - extra_buf;
		return std::max(1, (filter_period + buf_remain - 1) / buf_remain);
	}

	static constexpr int32_t first_filter_period() {
		return (int32_t)(sample_freq * 60.0f / highest_bpm + 0.5f);
	}

	static constexpr int32_t next_filter_period(int32_t filter_period) {
		int32_t decimation = calc_decimation(filter_period);
		return filter_period + decimation;
	}

	static constexpr int32_t count_required_filters() {
		int32_t count = 0;
		// Start with lowest period
		int32_t period = first_filter_period();
		int32_t last_distance = highest_bpm - lowest_bpm;
		if (!(last_distance > 0)) {
			return 0;
		}
		for (;;) {
			++count;
			int32_t decimation = calc_decimation(period);
			period += decimation;
			float distance = sample_freq * 60.0f / period - lowest_bpm;
			if (distance < 0) {
				distance = -distance;
			}
			if (distance > last_distance) {
				return count;
			}
			last_distance = distance;
		}
		// Loop exits via condition in body
	}

	// static int32_t count_required_filters_d() {
	// 	int32_t count = 1;
	// 	// Start with lowest period
	// 	int32_t period = first_filter_period();
	// 	std::cout << "count_required_filters_d" << std::endl;
	// 	int32_t last_distance = highest_bpm - lowest_bpm;
	// 	std::cout << "  last_distance=" << last_distance << std::endl;
	// 	if (!(last_distance > 0)) {
	// 		return 0;
	// 	}
	// 	for (;;) {
	// 		int32_t decimation = calc_decimation(period);
	// 		period += decimation;
	// 		float distance = sample_freq * 60.0f / period - lowest_bpm;
	// 		if (distance < 0) {
	// 			distance = -distance;
	// 		}
	// 		std::cout << "  p=" << period << ", d=" << distance << std::endl;
	// 		if (distance > last_distance) {
	// 			std::cout << "  done: count=" << count << std::endl;
	// 			return count;
	// 		}
	// 		last_distance = distance;
	// 		++count;
	// 	}
	// 	// Loop exits via condition in body
	// }
};


template<int32_t BufSize, int32_t ExtraBuf, int32_t SampleFreq, int32_t LowBpm, int32_t HighBpm>
class IirCombFilterRange {
private:
	typedef IirCombFilterRangeUtil<BufSize, ExtraBuf, SampleFreq, LowBpm, HighBpm> Util;

public:
	static constexpr int32_t buf_size = BufSize;
	static constexpr int32_t extra_buf = ExtraBuf;
	static constexpr float sample_freq = SampleFreq;
	static constexpr float lowest_bpm = LowBpm;
	static constexpr float highest_bpm = HighBpm;
	static constexpr int32_t num_filters = Util::count_required_filters();

	explicit IirCombFilterRange(float a_filter_q) {
		int32_t period = Util::first_filter_period();
		for(int32_t i = 0; i < num_filters; ++i) {
			auto & filter = _filters[i];
			int32_t decimation = Util::calc_decimation(period);
			filter.set_parameters(period / decimation, decimation, a_filter_q);

			auto & power_calculator = _power_calculators[i];
			power_calculator.set_parameters(period / decimation);

			period = Util::next_filter_period(period);
		}
	}

	template<class TPrevSource>
	void process(TPrevSource const * source, int32_t n) {
		float highest_power_val = -1.0f;
		int32_t highest_power_i = -1;
		for(int32_t i = 0; i < num_filters; ++i) {
			int32_t next_n = _filters[i].process(source, n);
			_power_calculators[i].process(&_filters[i], next_n);
			float power_val = _power_calculators[i].cur_power();
			assert(power_val >= 0.0f);
			if(power_val > highest_power_val) {
				highest_power_val = power_val;
				highest_power_i = i;
			}
		}
		assert(highest_power_i >= 0);
		_cur_highest_power = highest_power_i;
	}

	int32_t cur_highest_power() const { return _cur_highest_power; }
	IirCombFilter<BufSize> const * filter(int32_t i) const { return &_filters[i]; }
	IirCombFilter<BufSize> const * power_calculator(int32_t i) const { return &_power_calculators[i]; }

private:
	std::array<IirCombFilter<BufSize>, Util::count_required_filters()>
		_filters;
	std::array<WindowedPowerCalculator<BufSize>, Util::count_required_filters()>
		_power_calculators;
	int32_t _cur_highest_power;
};


int main(int argc, char *argv[])
{
	if(argc != 2) {
		printf("Usage: %s <DATAFILE>\n", argv[0]);
		return 2;
	}

	FileSource<8> fs(argv[1]);
	if(!fs.valid()) {
		printf("Error opening %s\n", argv[1]);
		return 2;
	}

	// IirCombFilterRangeUtil<64, 8, 200, 83, 200>::count_required_filters_d();

	IirFilter<8, 2> hpf(
		{ 0.998431665916719f, -0.998431665916719f },
		{ 1.0f, -0.996863331833438f }
	);
	IirCombFilter<128> comb((200 * 60) / 174, 1, 0.90f);

	IirCombFilterRange<64, 8, 200, 83, 200> comb_filters(0.90f);

	std::cout << comb_filters.num_filters << " filters:" << std::endl;
	for (int32_t i = 0; i < comb_filters.num_filters; ++i) {
		auto const & filter = *comb_filters.filter(i);
		std::cout << "  p=" << filter.filter_period() << " * "
			<< (filter.filter_decimation()) << ", bpm="
			<< (comb_filters.sample_freq * 60.0f / (filter.filter_period() * filter.filter_decimation()))
			<< std::endl;
	}

	std::ofstream hpf_out("tmp/hpf.txt");
	int32_t n = 1;
	for(int32_t i = 0; i < 3000 / n; ++i) {
		fs.process(n);
		hpf.process(&fs, n);
		comb.process(&hpf, n);

		auto p = hpf.range(n);
		for(int32_t j = 0; j < n; ++j) {
			float val = *--p;
			float g = (int32_t)roundf(val * (34.0f / 10.0f)) + 34;
			hpf_out << std::showpos << std::fixed << std::setw(8) << std::setprecision(4) << val << ':';
			if (g < 0) {
				hpf_out << '<';
			} else if (g > 68) {
				hpf_out << std::string(68, ' ') << '>';
			} else {
				hpf_out << std::string(g, ' ') << '|';
			}
			hpf_out << std::endl;
		}
	}

	return 0;
}