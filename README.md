# Lazy Testing

## Development

### Install Dependencies

```sh
pip install -r requirements.txt
```

### Decompile Codebase

Place ```jvm2json.exe``` in the utils directory.

```sh
python utils/java2json.py
```

Or watch for changes in Java files

```sh
python utils/java2json.py -w
```

### Run Unit Tests

```sh
python -m unittest tests/test.py
```
