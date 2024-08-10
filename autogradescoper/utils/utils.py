import logging, os, shutil, sys, importlib, csv, json, yaml, subprocess, time

def get_func(name):
    """
    Get the function object among the runnable scripts based on the script name
    """
    #print(f"get_func({name}) was called")
    module = importlib.import_module(f"autogradescoper.scripts.{name}")
    return getattr(module,name)

def create_custom_logger(name, logfile=None, level=logging.INFO):
    """
    Create a custom logger object
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False  # Prevent log messages from being propagated to parent loggers
    
    if logger.hasHandlers():
        logger.handlers.clear()
    
    log_console_handler = logging.StreamHandler()
    log_console_format = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    log_console_handler.setFormatter(log_console_format)
    logger.addHandler(log_console_handler)
    
    ## create a directory for the logger file if needed
    if logfile is not None:
        output_dir = os.path.dirname(logfile)
        if not os.path.exists(output_dir):
            logger.info(f"Creating directory {output_dir} for storing output")
            os.makedirs(output_dir)
        
        log_file_handler = logging.FileHandler(logfile)
        log_file_handler.setLevel(logging.INFO)
        log_file_format = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        log_file_handler.setFormatter(log_file_format)
        logger.addHandler(log_file_handler)
    
    return logger

## code suggested by ChatGPT
def load_file_to_dict(file_path, file_type=None):
    """
    Load a JSON or YAML file into a dictionary.

    Parameters:
    file_path (str): Path to the JSON or YAML file.
    file_type (str, optional): The type of the file ('json' or 'yaml'). If None, the type is inferred from the file extension.

    Returns:
    dict: Dictionary containing the file's data.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    if file_type is None:
        _, file_extension = os.path.splitext(file_path)
        file_type = file_extension.lower()[1:]  # Strip the dot and use the extension

    if file_type == 'json':
        with open(file_path, 'r') as file:
            return json.load(file)
    elif file_type in ['yaml', 'yml']:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    else:
        raise ValueError("Unsupported file type. Please provide 'json' or 'yaml'/'yml' as file_type.")

## code suggested by ChatGPT
def write_dict_to_file(data, file_path, file_type=None):
    """
    Write a dictionary to a JSON or YAML file.

    Parameters:
    data (dict): The dictionary to write to the file.
    file_path (str): Path to the output file.
    file_type (str, optional): The type of the file ('json' or 'yaml'). If None, the type is inferred from the file extension.

    Raises:
    ValueError: If the file type is unsupported.
    """
    if file_type is None:
        _, file_extension = os.path.splitext(file_path)
        file_type = file_extension.lower()[1:]  # Strip the dot and use the extension

    if file_type == 'json':
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    elif file_type in ['yaml', 'yml']:
        with open(file_path, 'w') as file:
            yaml.safe_dump(data, file, default_flow_style=False)
    else:
        raise ValueError("Unsupported file type. Please provide 'json' or 'yaml'/'yml' as file_type.")

def run_r_eval_script(out_prefix, timeout = None):
    start_time = time.time()
    with open(f"{out_prefix}.out", 'w') as fout:
        if timeout is None:
            cmd = f"Rscript {out_prefix}.R"
        else:
            cmd = f"timeout {timeout}s Rscript {out_prefix}.R"
        proc = subprocess.run(cmd, shell=True, stdout=fout)
    end_time = time.time()
    elapsed_time = end_time - start_time
    with open(f"{out_prefix}.time", 'w') as ftime:
        ftime.write(f"{elapsed_time:.2f}\n")
    exit_code = proc.returncode
    with open(f"{out_prefix}.exitcode", 'w') as fexit:
        fexit.write(f"{exit_code}\n")
    return (elapsed_time, exit_code)


# write an R script based on the R function, input parameters, and output prefix
def write_r_eval_func_script(func_name, out_prefix, in_func_path, in_params, out_digits):
    n_args = 0
    with open(f"{out_prefix}.R", 'w') as fout:
        fout.write(f"source('{in_func_path}')\n")
        out_cmds = []
        include_read_binary_matrix = False
        with open(in_params, 'r') as fparams:
            for line in fparams:
                n_args += 1
                (type, value) = line.split(":", maxsplit=1)
                value = value.strip()
                if type == "int":
                    values = value.split()
                    cmd = f"arg{n_args} <- c(" #+ "L, ".join(value.split()) + "L)"
                    for v in values:
                        try:
                            iv = int(v)
                            if -2147483648 <= iv <= 2147483647:
                                cmd += f"{iv}L, "
                            else:
                                cmd += f"{iv}, "
                        except ValueError:
                            cmd += f"{v}, "
                    cmd = cmd[:-2] + ")"
                elif type == "numeric":
                    cmd = f"arg{n_args} <- c(" + ",".join(value.split()) + ")"
                elif type == "str":
                    values = value.split()
                    cmd = f"arg{n_args} <- c(" + ",".join([f"'{v}'" for v in values]) + ")"
                elif type == "df":
                    cmd = f"arg{n_args} <- read.table('{value}', header=TRUE)"
                elif type == "rds":
                    cmd = f"arg{n_args} <- readRDS('{value}')"
                elif type == "mat":
                    cmd = f"arg{n_args} <- as.matrix(read.table('{value}', header=FALSE)"
                elif type == "bin":
                    cmd = f"arg{n_args} <- read_binary_matrix('{value}')"
                    include_read_binary_matrix = True
                else:
                    raise ValueError(f"Unknown type {type}")
                out_cmds.append(cmd)
        
        if len(out_cmds) == 0:
            raise ValueError("No input parameters found")
        
        if include_read_binary_matrix:
            cmd = """read.binary.matrix = function(filename) {
    fh = file(filename,"rb")
    dims = readBin(fh,what="integer",n=2L,size=4L)
    n = dims[1]
    p = dims[2]
    X = matrix(readBin(fh,what="numeric",n=n*p,size=8L),nrow=n,ncol=p)
    close(fh)
    return(X)
}
"""
            fout.write(cmd)
        fout.write("\n".join(out_cmds))
        fout.write("\n")    

        ## execute the R function
        cmd = f"rst <- {func_name}("
        for i in range(n_args):
            if i > 0:
                cmd += ", "
            cmd += f"arg{i+1}"
        cmd += ")\n"
        cmd += "if ( is.null(rst) || is.na(rst) || is.nan(rst) ) {\n"
        cmd += f"    cat('NA',sep='\\n',file='{out_prefix}.out')\n"
        cmd += "} else {\n"
        cmd += f"    cat(formatC(rst, digits={out_digits}, flag='-'), sep='\\n', file='{out_prefix}.out')\n"
        cmd += "}\n"
        fout.write(cmd)