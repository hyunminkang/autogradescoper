import sys, os, gzip, argparse, logging, warnings, shutil, subprocess, ast, json, time, difflib

from autogradescoper.utils.utils import create_custom_logger, load_file_to_dict, write_dict_to_file, write_r_eval_func_script, run_r_eval_script, params2str, diff_files

def parse_arguments(_args):
    repo_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    parser = argparse.ArgumentParser(prog=f"autogradescoper eval_r_func_args", description="Automatic grading of a single R function for a single example input/output")

    inout_params = parser.add_argument_group("Required Input/Output Parameters", "Input/output directory/files.")
    inout_params.add_argument('--r-func', type=str, required=True, help='Name of the R function to evaluate')
    inout_params.add_argument('--solution', type=str, required=True, help='R script containing the correct solution')
    inout_params.add_argument('--submission', type=str, required=True, help='R script containing the submitted solution')
    inout_params.add_argument('--args', type=str, required=True, help='File containing the input arguments of the R function. Each argument is a separate line in the format of [type]:[value] (e.g. int:5, str:"hello", df:/path/to/df.csv)')
    inout_params.add_argument('--out-prefix', type=str, required=True, help='Prefix output files -- .diff, .out, .err')

    key_params = parser.add_argument_group("Key Parameters with default values", "Key parameters frequently used by users")
    key_params.add_argument('--log', action='store_true', default=False, help='Write log to file')
    key_params.add_argument('--log-path', type=str, help='The suffix for the log file. Default: {out_prefix}.log')
    key_params.add_argument('--max-time', type=int, default=10, help='Maximum time in seconds to run the R function')
    key_params.add_argument('--digits', type=int, default=8, help='Number of digits to to write the output')
    key_params.add_argument('--format', type=str, default="g", help='C-style format out output ("d", "f", "g", "e", "s", ..) to write the output')
    key_params.add_argument('--preload-usr', type=str, help='User R script to load before the R function')
    key_params.add_argument('--preload-sol', type=str, help='Solution R script to load before the R function')
    key_params.add_argument('--max-show-chars', type=int, default=500, help='Maximum number of characters to show in the output')
    key_params.add_argument('--log-show-chars', type=int, default=500, help='Maximum number of characters to show in the log')

    if len(_args) == 0:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args(_args)

# def show_diff_with_line_numbers(string1, string2):
#     diff = difflib.ndiff(string1.splitlines(), string2.splitlines())
#     result = []
    
#     # Variables to track line numbers
#     line_num1 = 0
#     line_num2 = 0

#     for line in diff:
#         if line.startswith(' '):
#             # If the line is the same, increment both line numbers
#             line_num1 += 1
#             line_num2 += 1
#         elif line.startswith('-'):
#             # If the line is in string1 but not in string2, increment line number for string1
#             result.append(f"Line {line_num1 + 1} [Solution Only]: {line[1:]}")
#             line_num1 += 1
#         elif line.startswith('+'):
#             # If the line is in string2 but not in string1, increment line number for string2
#             result.append(f"Line {line_num2 + 1} [Submission Only]: {line[1:]}")
#             line_num2 += 1
#         if ( len(result) > 50 ): ## show only the first 50 differences if too many
#             break
#     return '\n'.join(result)

def eval_r_func_args(_args):
    # parse argument
    args=parse_arguments(_args)

    log_path = args.log_path if args.log_path is not None else f"{args.out_prefix}.log"
    logger = create_custom_logger(__name__, log_path if args.log else None)
#    logger.info("Analysis Started")

    # write an R script to run the test
    out_usr_prefix = f"{args.out_prefix}.usr"
    out_sol_prefix = f"{args.out_prefix}.sol"

    str_args = params2str(args.args)
    if len(str_args) > args.log_show_chars:
        logger.info(str_args[0:args.log_show_chars] + "\n... (truncated)")
    else:
        logger.info(str_args)

#    logger.info(f"Writing the R scripts to evaluate the function {args.r_func}")
    write_r_eval_func_script(args.r_func, out_usr_prefix, args.submission, args.args, args.digits, args.format, args.preload_usr)
    write_r_eval_func_script(args.r_func, out_sol_prefix, args.solution, args.args, args.digits, args.format, args.preload_sol)

    # Run the R scripts and store the outputs
    (sol_elapsed_time, sol_exit_code, sol_error_message) = run_r_eval_script(out_sol_prefix, None)
    (usr_elapsed_time, usr_exit_code, usr_error_message) = run_r_eval_script(out_usr_prefix, args.max_time)

    # Calculate score and handle errors
    str_details = ""
    str_errors = ""
    str_diffs = ""
    if usr_exit_code != 0:
        if usr_exit_code == 124: ## timeout
            score = "timeout"
            #logger.info(f"TIMEOUT: The code took {usr_elapsed_time}s, which exceeds the limit {args.max_time}s.")
            str_details = f"TIMEOUT: The code returned a timeout error, terminated at {usr_elapsed_time}s, because it exceeded the limit {args.max_time}s."
            str_diffs = f"TIMEOUT: The code returned a timeout error, terminated at {usr_elapsed_time}s, because it exceeded the limit {args.max_time}s."
        else: ## other errors
            score = "error"
            # Print or log the error message
            str_details = f"ERROR: The code returned an error, with exit code {usr_exit_code}.\n"
            str_errors = f"Error message: {usr_error_message}"
    elif usr_elapsed_time < args.max_time:
        ## compare if the output if identical
        with open(f"{args.out_prefix}.sol.out", 'r') as fsolout:
            with open(f"{args.out_prefix}.usr.out", 'r') as fusrout:
                solout = fsolout.read().strip()
                usrout = fusrout.read().strip()
                if solout == usrout:
                    score = "pass"
                    #logger.info(f"PASS: The code returned a correct output: {usrout}.")
                    str_details = f"PASS: The code returned a correct output: {usrout}."
                    str_diffs = f"PASS: The code returned the same output to the expected output."
                else:
                    score = "incorrect"
                    #logger.info(f"INCORRECT: The code returned an incorrect output")
                    #logger.info(f"Expected output: {solout}")
                    #logger.info(f"Observed output: {usrout}")

                    str_details = f"INCORRECT: The code returned an incorrect output\nExpected output: {solout}\nObserved output: {usrout}"
                    #str_diffs = f"INCORRECT: The code an incorrect output with the following diff\n" + show_diff_with_line_numbers(solout, usrout)
                    str_diffs = f"INCORRECT: The code an incorrect output with the following diff\n" + diff_files(f"{args.out_prefix}.sol.out", f"{args.out_prefix}.usr.out")
    else: ## undetected timeout without error code.. does this ever happen?
        score = "timeout"
        #logger.info(f"TIMEOUT: The code took {usr_elapsed_time}s, which exceeds the limit {args.max_time}s.")
        str_details = f"TIMEOUT: The code took {usr_elapsed_time}s, which exceeds the limit {args.max_time}s."
        str_diffs = f"TIMEOUT: The code took {usr_elapsed_time}s, which exceeds the limit {args.max_time}s."

    ## print log messages to the autograder output (hidden from students)
    if len(str_details) > 0:
        if len(str_details) > args.log_show_chars:
            logger.info("Output details are too long.. showing diffs only:")
            if len(str_diffs) > args.log_show_chars:
                logger.info(str_diffs[0:args.log_show_chars] + "\n... (truncated)")
            else:
                logger.info(str_diffs)
        else:
            logger.info(str_details)
    
    if len(str_errors) > 0:
        if len(str_errors) > args.log_show_chars:
            logger.info(str_errors[0:args.log_show_chars] + "\n... (truncated)")
        else:
            logger.info(str_errors)

    with open(f"{args.out_prefix}.score", 'w') as fscore:
        fscore.write(f"{score}\n")
    
    ## write the input arguments to the output file
    with open(f"{args.out_prefix}.args", 'w') as fargs:
        if ( len(str_args) > args.max_show_chars ):
            fargs.write(str_args[0:args.max_show_chars])
            fargs.write("\n")
            fargs.write("... (truncated)\n")
        else:
            fargs.write(str_args)
            fargs.write("\n")
    
    ## write the detailed output to the output file
    with open(f"{args.out_prefix}.details", 'w') as fdetails:
        if ( len(str_details) > args.max_show_chars ):
            fdetails.write(str_details[0:args.max_show_chars])
            fdetails.write("\n")
            fdetails.write("... (truncated)\n")
        else:
            fdetails.write(str_details)
            fdetails.write("\n")

    with open(f"{args.out_prefix}.diffs", 'w') as fdiffs:
        if ( len(str_diffs) > args.max_show_chars ):
            fdiffs.write(str_diffs[0:args.max_show_chars])
            fdiffs.write("\n")
            fdiffs.write("... (truncated)\n")
        else:
            fdiffs.write(str_diffs)
            fdiffs.write("\n")

    ## write the detailed errors to the output file
    with open(f"{args.out_prefix}.errors", 'w') as ferrors:
        if ( len(str_errors) > args.max_show_chars ):
            ferrors.write(str_errors[0:args.max_show_chars])
            ferrors.write("\n")
            ferrors.write("... (truncated)\n")
        else:
            ferrors.write(str_errors)
            ferrors.write("\n")


#    logger.info(f"Analysis finished with the final score: {score} and elapsed time: {usr_elapsed_time:.3f}s")

if __name__ == "__main__":
    # Get the base file name without extension
    script_name = os.path.splitext(os.path.basename(__file__))[0]

    # Dynamically get the function based on the script name
    func = getattr(sys.modules[__name__], script_name)

    # Call the function with command line arguments
    func(sys.argv[1:])