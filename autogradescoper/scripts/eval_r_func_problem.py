import sys, os, gzip, argparse, logging, warnings, shutil, subprocess, ast, json, time

from autogradescoper.utils.utils import get_func, create_custom_logger, load_file_to_dict, write_dict_to_file, write_r_eval_func_script, run_r_eval_script

def parse_arguments(_args):
    repo_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    parser = argparse.ArgumentParser(prog=f"autogradescoper eval_r_func_problem", description="Automatic grading of a single R function for a set of parameters")

    inout_params = parser.add_argument_group("Required Input/Output Parameters", "Input/output directory/files.")
    inout_params.add_argument('--r-func', type=str, required=True, help='Name of the R function to evaluate. R script should be found at /autograder/submission/{r_func}.R')
    inout_params.add_argument('--solution', type=str, required=True, help='R script containing the correct solution')
    inout_params.add_argument('--submission', type=str, required=True, help='R script containing the submitted solution')
    inout_params.add_argument('--config', type=str, required=True, help='JSON/YAML files containing the input arguments and other parameter values')
    inout_params.add_argument('--out-prefix', type=str, required=True, help='Prefix output files')
    inout_params.add_argument('--skip-solution', action='store_true', default=False, help='Ignore the solution, and parse the output as a JSON file. "score" and "details" are key attributes')

    key_params = parser.add_argument_group("Key Parameters with default values", "Key parameters frequently used by users")
    key_params.add_argument('--log', action='store_true', default=False, help='Write log to file')
    key_params.add_argument('--digits', type=int, default=8, help='Number of digits to to write the output')
    key_params.add_argument('--format', type=str, default="g", help='C-style format out output ("d", "f", "g", "e", "s", ..) to write the output')
    key_params.add_argument('--preload-usr', type=str, help='User R script to load before the R function')
    key_params.add_argument('--preload-sol', type=str, help='Solution R script to load before the R function')
    key_params.add_argument('--preload-all', type=str, default=f"{repo_dir}/assets/autogradescoper_utils.R", help='For all cases, load this R script before the R function')
    key_params.add_argument('--default-maxtime', type=int, default=10, help='Maximum time in seconds to run the R function')
    key_params.add_argument('--show-args', action='store_true', default=False, help='Show the arguments to user output')
    key_params.add_argument('--show-details', action='store_true', default=False, help='Show the correct and incorrect output to user output')
    key_params.add_argument('--show-diffs', action='store_true', default=False, help='Show the difference between correct and incorrect output')
    key_params.add_argument('--show-errors', action='store_true', default=False, help='Show the detailed errors to user output')

    if len(_args) == 0:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args(_args)

def eval_r_func_problem(_args):
    # parse argument
    args=parse_arguments(_args)

    log_path = f"{args.out_prefix}.log"
    logger = create_custom_logger(__name__, log_path if args.log else None)
#    logger.info("Analysis Started")

    ## read the config file
#    logger.info(f"Reading the config file: {args.config}")
    config = load_file_to_dict(args.config)

    n_config = len(config)
    for i, v in enumerate(config):
        argval= v["args"]
        maxtime = v.get("maxtime", args.default_maxtime)

        logger.info("====================================================================")
        logger.info(f"Evaluating the test case {i+1}/{n_config}:")
        logger.info("====================================================================")

        get_func("eval_r_func_args")(  
                        ["--r-func", args.r_func] +
                        ["--solution", args.solution] +
                        ["--args", argval] +
                        ["--out-prefix", f"{args.out_prefix}.{i}"] +
                        ["--max-time", str(maxtime)] +
                        ["--digits", str(args.digits)] +
                        ["--format", args.format] +
                        ["--submission", args.submission] +
                        (["--preload-usr", args.preload_usr] if args.preload_usr is not None else []) +
                        (["--preload-sol", args.preload_sol] if args.preload_sol is not None else []) +
                        (["--preload-all", args.preload_all] if args.preload_all is not None else []) +
                        (["--skip-solution"] if args.skip_solution else []))
                        (["--log"] if args.log else []))                

    ## collect the results and store into a single output file
    outdict = {}
    sum_scores = 0
    sum_elapsed = 0
    out_strs = []
    for i, v in enumerate(config):
        with open(f"{args.out_prefix}.{i}.usr.time", 'r') as ftime:
            elapsed = ftime.read().strip()
            sum_elapsed += float(elapsed)

        with open(f"{args.out_prefix}.{i}.score", 'r') as fscore:
            score = fscore.read().strip()
            if score == "pass":
                sum_scores += 1
        #out_strs.append(f"Case {i+1}: {score} in {elapsed}s")
        out_str = f"Case {i+1}: {score} in {elapsed}s\n"
        if args.show_args:
            with open(f"{args.out_prefix}.{i}.args", 'r') as fargs:
                out_str += f"-----------------------------\n{fargs.read()}"
        if args.show_details:
            with open(f"{args.out_prefix}.{i}.details", 'r') as fdetails:
                out_str += f"-----------------------------\n{fdetails.read()}"
        if args.show_diffs:
            with open(f"{args.out_prefix}.{i}.diffs", 'r') as fdiffs:
                out_str += f"-----------------------------\n{fdiffs.read()}"
        if args.show_errors:
            with open(f"{args.out_prefix}.{i}.errors", 'r') as ferrors:
                out_str += f"-----------------------------\n{ferrors.read()}"
        out_strs.append(out_str)
    outdict["score"] = sum_scores
    outdict["elapsed"] = sum_elapsed
    outdict["max_score"] = n_config
    outdict["name"] = args.r_func
    outdict["name_format"] = "text"
    outdict["output"] = f"Score: {sum_scores}/{n_config}\nTotal elapsed time: {sum_elapsed:.3f}s\n================================\nTest Cases:\n================================\n" + "================================\n".join(out_strs) + "\n"

    ## write the output to a file
#    logger.info(f"Writing the evaluation output to {args.out_prefix}.json")
    write_dict_to_file(outdict, f"{args.out_prefix}.json")
        
#    logger.info(f"Analysis finished")

if __name__ == "__main__":
    # Get the base file name without extension
    script_name = os.path.splitext(os.path.basename(__file__))[0]

    # Dynamically get the function based on the script name
    func = getattr(sys.modules[__name__], script_name)

    # Call the function with command line arguments
    func(sys.argv[1:])