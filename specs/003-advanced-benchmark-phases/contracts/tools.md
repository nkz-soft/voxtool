# Tool Contract: Advanced Benchmark Phases

All tools are registered through `ToolRegistry`, exported in tool manifests, validated before execution, and executed only through `ToolExecutor`.

Required registry components:

- `ToolDefinition`
- `ToolRegistry`
- `ToolExecutor`
- `ToolSchemaValidator`

Each tool must have:

- Pydantic args model
- JSON schema
- deterministic executor
- tests
- examples
- metrics grouping

## units.convert

Arguments:

```json
{
  "value": 2,
  "from_unit": "kilometer",
  "to_unit": "meter"
}
```

Required behavior:

- Converts deterministic length, mass, and temperature values.
- Rejects unsupported units and incompatible unit families.
- Remains the primary benchmark tool.

## text.stress_ru

Arguments:

```json
{
  "text": "замок",
  "mode": "mark_primary"
}
```

Required behavior:

- Accepts Russian text or a Russian word.
- Returns text with the requested stress marking.
- Rejects unsupported modes and empty text.
- Reports deterministic execution results for benchmark examples.

## calculator.simple

Arguments:

```json
{
  "expression": "2 + 2 * 3"
}
```

Required behavior:

- Evaluates deterministic simple arithmetic.
- Supports bounded numeric operations needed by fixture examples.
- Rejects unsafe, non-arithmetic, or unsupported expressions.

## Unsupported Tools

Unsupported tool calls produce structured failures:

```json
{
  "failure_type": "unknown_tool",
  "tool": "weather.lookup",
  "message": "Tool is not registered.",
  "details": {
    "available_tools": ["units.convert", "text.stress_ru", "calculator.simple"]
  },
  "stage": "registry"
}
```

Required behavior:

- Unsupported tools never execute.
- Failures are included in per-example artifacts and aggregate metrics.
- Weather remains out of scope.
