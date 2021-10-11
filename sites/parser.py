class Parser:
    buffer: str
    offset: int

    def __init__(self, buffer: str) -> None:
        self.buffer = buffer
        self.offset = 0

    def read(self, count: int = 1):
        if self.left() < count:
            return ""
        ret = self.buffer[self.offset:self.offset + count]
        self.offset += count
        return ret

    def peek(self, count: int = 1) -> str:
        if self.left() < count:
            return ""
        return self.buffer[self.offset:self.offset + count]

    def peek_while(self, f) -> str:
        offset = self.offset
        while offset < len(self.buffer):
            c = self.buffer[offset]
            if f(c):
                offset += 1
            else:
                break
        return self.buffer[self.offset:offset]

    def read_while(self, f) -> str:
        offset = self.offset
        while self.left() > 0:
            c = self.peek()
            if f(c):
                _ = self.read()
            else:
                break
        return self.buffer[offset:self.offset]

    def read_while_prev(self, f) -> str:
        offset = self.offset
        while self.left() > 0:
            c = self.peek()
            prev = self.buffer[self.offset-1]
            if f(c, prev):
                _ = self.read()
            else:
                break
        return self.buffer[offset:self.offset]

    def left(self) -> int:
        return len(self.buffer) - self.offset