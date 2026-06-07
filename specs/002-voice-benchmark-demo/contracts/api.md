# Optional Demo API Contract

The API is optional and local-demo oriented. It must not become a complex UI requirement or introduce cloud-service requirements for MVP validation.

## POST /demo/text

Request:

```json
{
  "text": "Convert 2 kilometers to meters",
  "language": "en",
  "execute_tool": true
}
```

Response:

```json
{
  "raw_output": "...",
  "parsed_output": {
    "needs_tool": true,
    "tool_call": {
      "tool": "units.convert",
      "arguments": {
        "value": 2,
        "from_unit": "kilometer",
        "to_unit": "meter"
      }
    },
    "final_answer": "2 kilometers is 2000 meters."
  },
  "validation_error": null,
  "structured_failures": [],
  "tool_execution_result": {
    "tool": "units.convert",
    "result_value": 2000,
    "result_unit": "meter"
  },
  "final_answer": "2 kilometers is 2000 meters."
}
```

## POST /demo/audio

Request:

```json
{
  "audio_path": "data/fixtures/example.wav",
  "language": "en",
  "pipeline": "C",
  "execute_tool": true
}
```

Response:

```json
{
  "transcript": "Convert 2 kilometers to meters",
  "raw_output": "...",
  "parsed_output": {
    "needs_tool": true,
    "tool_call": {
      "tool": "units.convert",
      "arguments": {
        "value": 2,
        "from_unit": "kilometer",
        "to_unit": "meter"
      }
    },
    "final_answer": "2 kilometers is 2000 meters.",
    "transcript": "Convert 2 kilometers to meters"
  },
  "validation_error": null,
  "structured_failures": [],
  "tool_execution_result": {
    "tool": "units.convert",
    "result_value": 2000,
    "result_unit": "meter"
  },
  "final_answer": "2 kilometers is 2000 meters."
}
```

## Error Response

```json
{
  "error": {
    "code": "tool_failure",
    "message": "Tool call could not be completed.",
    "details": {
      "structured_failures": [
        {
          "failure_type": "unknown_tool",
          "tool": "weather.lookup",
          "message": "Tool is not registered.",
          "details": {
            "available_tools": ["units.convert"]
          },
          "stage": "registry"
        }
      ]
    }
  }
}
```
