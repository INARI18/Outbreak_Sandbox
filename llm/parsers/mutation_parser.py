import json

class MutationParseError(Exception):
    pass

class MutationParser:
    @staticmethod
    def parse(text: str) -> dict:
        try:
            data = json.loads(text)
        except Exception:
            raise MutationParseError("Invalid JSON")

        if "mutate" not in data:
            raise MutationParseError("Missing 'mutate' field")

        return data
