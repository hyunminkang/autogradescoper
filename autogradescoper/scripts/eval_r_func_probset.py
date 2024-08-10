import sys, os, gzip, argparse, logging, warnings, shutil, subprocess, ast, json, time

from autogradescoper.utils.utils import get_func, create_custom_logger, load_file_to_dict, write_dict_to_file, write_r_eval_func_script, run_r_eval_script

def parse_arguments(_args):
    repo_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    parser = argparse.ArgumentParser(prog=f"autogradescoper eval_r_func_probset", description="Automatic grading of multiple problem sets implementing R functions")

    inout_params = parser.add_argument_group("Required Input/Output Parameters", "Input/output directory/files.")
    inout_params.add_argument('--config', type=str, required=True, help='JSON/YAML files containing "func", "config", "digits", "preload" for each problem')

    key_params = parser.add_argument_group("Key Parameters with default values", "Key parameters frequently used by users")
    key_params.add_argument('--solution-dir', type=str, default="/autograder/source/solution", help='R script containing the correct solution')
    key_params.add_argument('--submission-dir', type=str, default="/autograder/submission", help='R script containing the submitted solution')
    key_params.add_argument('--out-prefix', type=str, default="/autograder/results/autogradescoper", help='Prefix of output files')
    key_params.add_argument('--log', action='store_true', default=False, help='Write log to file')

    if len(_args) == 0:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args(_args)

def eval_r_func_probset(_args):
    # parse argument
    args=parse_arguments(_args)

    log_path = f"{args.out_prefix}.log"
    logger = create_custom_logger(__name__, log_path if args.log else None)
    logger.info("Analysis Started")

    ## read the config file
    logger.info(f"Reading the config file: {args.config}")
    config = load_file_to_dict(args.config)

    n_config = len(config)
    jsons = []
    for i, v in enumerate(config):
        func = v["func"]
        conf = v["config"]
        digits = v["digits"]
        preload = v.get("preload", None)

        out_prefix = f"{args.out_prefix}.{func}"
        get_func("eval_r_func_problem")(  
                        ["--r-func", func] +
                        ["--solution", f"{args.solution_dir}/{func}.R"] +
                        ["--submission", f"{args.submission_dir}/{func}.R"] +
                        ["--config", conf] +
                        ["--out-prefix", out_prefix] +
                        ["--digits", str(digits)] +
                        (["--preload-script", preload] if preload else []) +
                        (["--log"] if args.log else []))                
        logger.info(f"Analysis for config {i+1}/{n_config} finished")
        logger.info(f"----------------------------------------------")

        ## loading the json output
        jsons.append(load_file_to_dict(f"{out_prefix}.json"))

    ## write the final output
    total_score = 0
    total_time = 0
    total_max_score = 0
    for j in jsons:
        total_score += j["score"]
        total_time += j["elapsed"]
        total_max_score += j["max_score"]

    outdict = {
        "score":total_score,
        "execution_time": total_time,
        "output": f"Total Score: {total_score}/{total_max_score}\nTotal Elapsed Time: " + ("%.3f" % (total_time)) + " seconds",
        "stdout_visibility": "hidden", # Optional stdout visibility setting
        "tests": jsons,
    }
    
    ## write the output to a file
    logger.info(f"Writing the evaluation output to {args.out_prefix}.json")
    write_dict_to_file(outdict, f"{args.out_prefix}.json")
    logger.info(f"Analysis finished")

if __name__ == "__main__":
    # Get the base file name without extension
    script_name = os.path.splitext(os.path.basename(__file__))[0]

    # Dynamically get the function based on the script name
    func = getattr(sys.modules[__name__], script_name)

    # Call the function with command line arguments
    func(sys.argv[1:])