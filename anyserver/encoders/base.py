from abc import ABC, abstractmethod
from typing import Optional

REGISTERED = []


class Encoder(ABC):
    mime = None
    ext = []

    @abstractmethod
    def encode(self, data): ...

    @abstractmethod
    def decode(self, data): ...

    @staticmethod
    def all(): return REGISTERED  # Return all registered

    @staticmethod
    def register(*encoders):
        for enc in filter(lambda enc: not enc in REGISTERED, encoders):
            REGISTERED.append(enc)

    @staticmethod
    def remove(*encoders):
        for enc in filter(lambda enc: enc in REGISTERED, encoders):
            REGISTERED.remove(enc)

    @staticmethod
    def find(filename):
        # Determine file type from extension
        parts = filename.split('.')
        type = None if len(parts) < 2 else '.'+parts[-1]

        # Find the first registered encoder that can handle this file type
        encoder = next(filter(lambda enc: type in enc.ext, REGISTERED), None)

        if not encoder:
            raise Exception(f"Cannot decode '{filename}' (file type: {type}).")

        return encoder

    @staticmethod
    def loadFile(filename):
        # Read the file contents and decode with the specified encoding
        encoder = Encoder.find(filename)
        with open(filename, 'r') as f:
            return encoder.decode(f.read())

    @staticmethod
    def saveFile(filename):
        # Read the file contents and decode with the specified encoding
        encoder = Encoder.find(filename)
        with open(filename, 'r') as f:
            return encoder.decode(f.read())
