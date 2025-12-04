# Abstract

Thanks for interviewing [me](https://www.linkedin.com/in/justinzollars/), and reviewing my code. To get started just type `make`

This is a simple Django API that converts numbers to English words. It Handles integers, decimals, and negatives up to decillions.

The algorithm chunks the integer into 3-digit groups, converts each chunk, and appends the proper scale words (thousand, million, etc.). Decimals are read digit-by-digit after "point". Uses Python's `Decimal` to avoid float precision issues.

**Complexity:** O(log n + d) time and space, where n is the integer value and d is the number of decimal digits.

## Getting Started

```bash
make run
make test
make help
```

## Usage

```bash
curl "http://localhost:8000/num_to_english?number=12345678"
curl -X POST -H "Content-Type: application/json" -d '{"number": "12345678"}' http://localhost:8000/num_to_english
```

POST works too—send `{"number": 42}` to the same endpoint.

## Development

Run `make start-server` for local dev, `make curl-tests` to hit it with 100+ test cases, or `make integration-test` to do both automatically. Override the port with `PORT=8001 make start-server`.

API docs live at `/api/docs/` (Swagger) and `/api/redoc/`.

## License

MIT
