from collections import deque


class PeakStack:
    def __init__(self, arr, queue=False):
        self.que = deque(arr)
        self.top = arr[len(arr)-1]
        self.__queue = queue

    def push(self, value):
        self.que.append(value)
        self.top = value

    def pop(self):
        value = self.que.pop() if not self.__queue else self.que.popleft()
        if len(self.que)-1 >= 0:
            self.top = self.que[len(self.que)-1]
        return value

    def __iter__(self):
        for v in self.que:
            yield v

    def __len__(self):
        return len(self.que)
