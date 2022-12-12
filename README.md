# idgrep
Tool for finding identifiers in files. Supports recursive globbing and boolean arbitrary complex queries.

# Usage
```
usage: idgrep [-p FILE_PATTERN] [-l LIMIT_SIZE] [-i LIMIT_IDENTIFIERS] [--help | --file-id-count]
              [--group-by-id] [--sort-by-name | --sort-by-count | --sort-by-size] [--ascending | --descending]
              [paths ...] -- query

positional arguments:
  paths

options:
  -p FILE_PATTERN, --file-pattern FILE_PATTERN
  -l LIMIT_SIZE, --limit-size LIMIT_SIZE
  -i LIMIT_IDENTIFIERS, --limit-identifiers LIMIT_IDENTIFIERS
  --help
  --file-id-count
  --group-by-id
  --sort-by-name
  --sort-by-count
  --sort-by-size
  --ascending, --asc
  --descending, --desc
```


# Details

## -p | --file-pattern

  The file pattern is processed using the glob[^glob] function of pathlib.
  
## -l | --limit-size

  Sets a maximum size limit for files to prevent processing large files. This is enabled by default and set to one megabyte (1M).

  The following suffixes are recognized:

  suffix |  size
  ------ |  -----
  k      |  2¹⁰ bytes
  m      |  2²⁰ bytes
  g      |  2³⁰ bytes
  t      |  2⁴⁰ bytes

## -i | --limit-size

  Sets the maximum identifier count limit for files to prevent processing files with too many identifiers. This is enabled by default and set to 1k.

  The following suffixes are recognized:

  suffix |  count
  ------ |  -----
  k      |  10³ identifiers
  m      |  10⁶ identifiers

## --help
  
  Shows the output shown above under [Usage](#usage).

## --file-id-count

  Counts number of identifiers in all matching files. Any query entered will be ignored.

## --group-by-id

  Group output by identifier. If a file is matching multiple identifiers it will be listed multiple times.

## --sort-by-name | --sort-by-count | --sort-by-size

  Select sort key for output.

## --ascending | --asc | --descending | --desc

  Select sort order.

## query

  The query is added last after a double dash. This double dash is used to separate file arguments from the query. If you wish to specify a file named double dash, use `./--` for it.

### Query Format

+ `~identifier`
  
  Do not match this identifier (logical not)

+ `!identifier`
  
  Do not match this identifier (logical not)

+ `expr_1 & expr_2`
  
  Match both expr_1 and expr_2 (and)

+ `expr_1 | expr_2`
  
  Match either expr_1 or expr_2 or both together (inclusive or)

+ `expr_1 ^ expr_2`
  
  Match either expr_1 or expr_2 but not both together (exclusive or)

+ `(subexpression)`
  
  Use parenthesis to define subexpressions. This is useful for queries such as:

  `(fish | birds) & (chips | bees)`






[^glob]:
    See https://docs.python.org/3/library/pathlib.html?highlight=path#pathlib.Path.glob for more information.
