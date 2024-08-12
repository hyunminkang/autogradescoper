import sys, os, gzip, argparse, logging, warnings, shutil, subprocess, ast, json, time

from autogradescoper.utils.utils import create_custom_logger, load_file_to_dict, write_dict_to_file, write_r_eval_func_script, run_r_eval_script, params2str

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
    key_params.add_argument('--preload-script', type=str, help='R script to load before the R function')

    if len(_args) == 0:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args(_args)

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
    logger.info(str_args)

#    logger.info(f"Writing the R scripts to evaluate the function {args.r_func}")
    write_r_eval_func_script(args.r_func, out_usr_prefix, args.submission, args.args, args.digits, args.preload_script, True)
    write_r_eval_func_script(args.r_func, out_sol_prefix, args.solution, args.args, args.digits, args.preload_script, False)

    ## run the R script
#    logger.info(f"Running the R scripts and storing the outputs")
    (sol_elapsed_time, sol_exit_code) = run_r_eval_script(out_sol_prefix, None)
    (usr_elapsed_time, usr_exit_code) = run_r_eval_script(out_usr_prefix, args.max_time)

    ## calculate score
#    logger.info(f"Evaluating the outputs and calculating the score")
    str_details = ""
    if usr_exit_code != 0:
        score = "error"
        #logger.info(f"ERROR: The code returned an error, with exit code {usr_exit_code}.")
        str_details = f"ERROR: The code returned an error, with exit code {usr_exit_code}."
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
                else:
                    score = "incorrect"
                    #logger.info(f"INCORRECT: The code returned an incorrect output")
                    #logger.info(f"Expected output: {solout}")
                    #logger.info(f"Observed output: {usrout}")
                    str_details = f"INCORRECT: The code returned an incorrect output\nExpected output: {solout}\nObserved output: {usrout}"
    else:
        score = "timeout"
        #logger.info(f"TIMEOUT: The code took {usr_elapsed_time}s, which exceeds the limit {args.max_time}s.")
        str_details = f"TIMEOUT: The code took {usr_elapsed_time}s, which exceeds the limit {args.max_time}s."

    logger.info(str_details)

    with open(f"{args.out_prefix}.score", 'w') as fscore:
        fscore.write(f"{score}\n")
    
    ## write the input arguments to the output file
    with open(f"{args.out_prefix}.args", 'w') as fargs:
        fargs.write(str_args)
        fargs.write("\n")
    
    ## write the detailed output to the output file
    with open(f"{args.out_prefix}.details", 'w') as fdetails
        fdetails.write(str_details)
        fdetails.write("\n")


#    logger.info(f"Analysis finished with the final score: {score} and elapsed time: {usr_elapsed_time:.3f}s")

if __name__ == "__main__":
    # Get the base file name without extension
    script_name = os.path.splitext(os.path.basename(__file__))[0]

    # Dynamically get the function based on the script name
    func = getattr(sys.modules[__name__], script_name)

    # Call the function with command line arguments
    func(sys.argv[1:])