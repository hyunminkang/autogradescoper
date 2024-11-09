# Test Caase for Autogradscoper

## Overview

The `args/` directory typically contains the input arguments for each test case.
For each test case. `test.i.args` file contains the input arguments for the test case `i`.
Each line of the file should contain the input arguments for the test case, in the format of
`{type}:{value}` as follows:

```plaintext linenums="1"
numeric:1 
numeric:10
numeric:TRUE
numeric:FALSE
```

The number of arguments in the file must match the number of arguments in the function to be evaluated.

## Types of Input Arguments

### `numeric` type

The `numeric` type is used to specify the numeric input arguments. `int` is treated as same as  `numeric`. logical values should also be treated as `numeric` type with `TRUE` as 1 and `FALSE` as 0.

### `str` type

The `str` type is used to specify the string input arguments as shown in the example below:

```plaintext linenums="1"
str:hello
str:world
```

You need specify the string input argument WITHOUT quote as shown in the example above

### `df` type 

If you want to pass a TSV file as an input to load as a dataframe, use `df` type as follows:

```plaintext linenums="1"
df:/autograder/source/args/test.1.tsv
``` 

Note that the path should be specified with '/autograder/source/' prefix, as the input files are located at `/autograder/source/` in the autograder container.

### `mat` type

If you want to pass a TSV file as a matrix, use `mat` type as follows:

```plaintext linenums="1"
mat:/autograder/source/args/test.1.tsv
``` 

This will load the TSV file with `as.matrix(read.table(...),header=FALSE)` in R. Make sure that the TSV file is formatted correctly without headers.

Note that the path should be specified with '/autograder/source/' prefix, as the input files are located at `/autograder/source/` in the autograder container.

### `rds` type

If you want to pass an arbitrary R object as an input, use `rds` type as follows:

```plaintext linenums="1"
rds:/autograder/source/args/test.1.rds
```

The `rds` type is used to load the R object saved in the `.rds` file format. These files can be created using the `saveRDS()` function in R. 

The autograder will load these arguments using the `readRDS()` function in R when evaluating the function with the input arguments.

Note that the path should be specified with '/autograder/source/' prefix, as the input files are located at `/autograder/source/` in the autograder container.

### `eval` type

If you want to pass a function as an argument, use `eval` type as follows:

```plaintext linenums="1"
eval:sum
```

This will pass the `sum()` function as an argument to the function to be evaluated.
