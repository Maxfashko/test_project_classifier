from .sampler import BatchSampler, SequentialSampler


class DataLoader(object):
    def __init__(self, data, batch_size=1, drop_last=False) -> None:
        self.data = data
        self.batch_sampler = BatchSampler(SequentialSampler(self.data), batch_size, drop_last)
        self.batch_size = batch_size
        self.drop_last = drop_last

    def __iter__(self):
        return Iterator(sampler=self.batch_sampler, data=self.data)

    @property
    def __len__(self):
        return len(list(self.batch_sampler))


class Iterator:
    def __init__(self, sampler, data):
        self.data = data
        self._sampler = list(sampler)
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index < len(self._sampler):
            sampler_idx = self._sampler[self._index]
            result = list(map(self.data.__getitem__, sampler_idx))
            self._index += 1
            return result
        else:
            raise StopIteration
