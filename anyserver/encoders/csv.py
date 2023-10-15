
import io
import csv

from anyserver.encoders.core import Encoder


class CsvEncoder(Encoder):
    mime = "text/csv"
    ext = [".csv"]

    def encode(self, data):
        data = [data] if not type(data) == list else data
        fields = data[0].keys() if len(data) else []
        with io.StringIO() as buffer:
            writer = csv.DictWriter(buffer, fieldnames=fields)
            writer.writeheader()
            writer.writerows(data)
            return buffer.getvalue()

    def decode(self, data):
        list = []
        with io.StringIO(initial_value=data) as buffer:
            reader = csv.DictReader(buffer)
            for row in reader:
                list.append(row)
        if len(list) < 2:
            return None if len(list) == 0 else list[0]
        return list
