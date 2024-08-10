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

    key_params = parser.add_argument_group("Key Parameters with default values", "Key parameters frequently used by users")
    key_params.add_argument('--log', action='store_true', default=False, help='Write log to file')
    key_params.add_argument('--digits', type=int, default=8, help='Number of digits to to write the output')
    key_params.add_argument('--preload-script', type=str, help='R script to load before the R function')

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
        maxtime = v["maxtime"]

        logger.info("--------------------------------------------------------------------")
        logger.info(f"Evaluating the test case {i+1}/{n_config}:")
        logger.info("--------------------------------------------------------------------")

        get_func("eval_r_func_args")(  
                        ["--r-func", args.r_func] +
                        ["--solution", args.solution] +
                        ["--args", argval] +
                        ["--out-prefix", f"{args.out_prefix}.{i}"] +
                        ["--max-time", str(maxtime)] +
                        ["--digits", str(args.digits)] +
                        ["--submission", args.submission] +
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
        out_strs.append(f"  Case {i+1}: {score} in {elapsed}s")
    outdict["score"] = sum_scores
    outdict["elapsed"] = sum_elapsed
    outdict["max_score"] = n_config
    outdict["name"] = args.r_func
    outdict["name_format"] = "text"
    outdict["output"] = f"Score: {sum_scores}/{n_config}\nTotal elapsed time: {sum_elapsed:.3f}s\nTest Cases:\n" + "\n".join(out_strs) + "\n"

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