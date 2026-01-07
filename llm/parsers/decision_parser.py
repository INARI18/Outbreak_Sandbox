import json

class DecisionParseError(Exception):
    pass


class DecisionParser:
    @staticmethod
    def _extract_json(raw_response: str) -> dict:
        try:
            return json.loads(raw_response)
        except Exception:
            start = raw_response.find('{')
            end = raw_response.rfind('}')
            if start == -1 or end == -1 or end <= start:
                raise DecisionParseError("Invalid JSON from LLM")
            snippet = raw_response[start:end+1]
            try:
                return json.loads(snippet)
            except Exception:
                raise DecisionParseError("Invalid JSON from LLM")

    @staticmethod
    def parse(raw_response: str) -> dict:
        data = DecisionParser._extract_json(raw_response)

        # Support multiple possible key names returned by different clients/mocks
        source = data.get('source_node') or data.get('source_node_id') or data.get('source') or data.get('src')
        target = data.get('target_node') or data.get('target_node_id') or data.get('target') or data.get('dst')

        missing = []
        if source is None:
            missing.append('source')
        if target is None:
            missing.append('target')

        if missing:
            raise DecisionParseError(f"Missing fields: {set(missing)}")

        return {
            "source_node_id": None if source is None else str(source),
            "target_node_id": None if target is None else str(target),
            "reasoning": data.get("reasoning", "")
        }
