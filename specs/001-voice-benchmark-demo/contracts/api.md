# API Contract

The API is optional and supports demo/backend execution. It must not bypass tool
schema validation.

## `POST /tool/execute`

Executes a validated `units.convert` invocation.

Request body:

```json
{
  "tool_name": "units.convert",
  "arguments": {
    "value": 2,
    "from_unit": "kilometers",
    "to_unit": "meters"
  }
}
```

Successful response:

```json
{
  "ok": true,
  "result": {
    "value": 2000,
    "unit": "meters"
  }
}
```

Validation failure response:

```json
{
  "ok": false,
  "error": {
    "code": "schema_validation_failed",
    "message": "Tool invocation did not match schema",
    "details": []
  }
}
```

## `POST /demo/text`

Processes a text request through the configured demo pipeline.

Required behavior:
- Decide whether a tool is required.
- Emit machine-readable JSON for tool decisions.
- Validate before optional execution.
- Return concise answer and diagnostic metadata.

## `POST /demo/audio`

Processes an audio request through the configured demo pipeline.

Required behavior:
- Accept audio input or an audio fixture reference.
- Produce transcript when applicable.
- Validate tool invocation before optional execution.
- Return concise answer and diagnostic metadata.
