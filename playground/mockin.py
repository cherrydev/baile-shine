import itertools


class InputMock:
    sample_freq: int
    data: list
    loop_beg: int
    loop_end: int
    loop_count: int
    cur_loop_count: int
    cur: int

    def __init__(self, filename: str, sample_freq: int = 200, loop_count: int = -1):
        with open(filename) as inFile:
            self.data = list(map(float, inFile))
        loop_beg, loop_end = 0, len(self.data)
        peak = -10
        post_peak = 0
        for i in range(len(self.data)):
            d = self.data[i]
            if d > -15:
                continue
            if d < peak:
                peak = d
                loop_beg = i
                post_peak = 0
            else:
                post_peak += 1
                if post_peak > 10:
                    break
        peak = -10
        post_peak = 0
        for i in range(len(self.data) - 1, 0, -1):
            d = self.data[i]
            if d > -15:
                continue
            if d < peak:
                peak = d
                loop_end = i
                post_peak = 0
            else:
                post_peak += 1
                if post_peak > 10:
                    break

        self.sample_freq = sample_freq
        self.loop_beg = loop_beg
        self.loop_end = loop_end
        self.loop_count = loop_count
        self.cur_loop_count = loop_count
        self.cur = 0

    def read_samples(self, n: int):
        beg = self.cur
        end = self.cur + n

        if (end >= self.loop_end) and (self.cur_loop_count != 0):
            result = self.data[beg:self.loop_end]
            beg = self.loop_beg
            end -= self.loop_end - self.loop_beg
            if self.cur_loop_count > 0:
                self.cur_loop_count -= 1
            while (end >= self.loop_end) and (self.cur_loop_count != 0):
                result.extend(self.data[self.loop_beg:self.loop_end])
                end -= self.loop_end - self.loop_beg
                if self.cur_loop_count > 0:
                    self.cur_loop_count -= 1
            result.extend(self.data[beg:min(end, len(self.data))])
        else:
            result = self.data[beg:min(end, len(self.data))]

        self.cur = end

        assert (len(result) == n) or (self.cur_loop_count == 0)

        if len(result) < n:
            result.extend(itertools.repeat(-9.8, n - len(result)))

        assert (len(result) == n)

        return result

    def reset(self):
        self.cur_loop_count = self.loop_count
        self.cur = 0
