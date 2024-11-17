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

### Run main

```sh
python src/main.py {codebase} [dynamic/[symbolic]]
```

Example:

```sh
python src/main.py constant_becomes_equal dynamic
# or
python src/main.py constant_becomes_equal
```

### Run performance test

```sh
python src/perf.py {codebase}
```

### Run Tests

```sh
pytest tests
```

#### Prepare Test Data

```sh
cd tests
git clone https://github.com/kalhauge/jpamb.git --no-checkout
cd jpamb
git sparse-checkout set decompiled/jpamb/cases stats/cases.txt --no-cone
git checkout 6746424
```

### CodeBases

Codebase are meant to test isolated scenarios and are meant to not change much over time so we can write unit test for them.
If you need to test how bytecode is generated consider using the scratch codebase.
