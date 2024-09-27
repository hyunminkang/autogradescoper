## Read a binary matrix

read.binary.matrix = function(filename) {
    fh = file(filename,"rb")
    dims = readBin(fh,what="integer",n=2L,size=4L)
    n = dims[1]
    p = dims[2]
    X = matrix(readBin(fh,what="numeric",n=n*p,size=8L),nrow=n,ncol=p)
    close(fh)
    return(X)
}

## Write a simple list to a JSON file
write_list_to_json <- function(mylist, file_path) {
  # Helper function to handle different types of elements (vectors)
  convert_element_to_json <- function(element) {
    if (length(element) == 1) {
      # If there's only one element, print it directly (no array)
      if (is.character(element)) {
        # Escape newlines for multi-line strings
        element <- gsub("\n", "\\\\n", element)
        json <- paste0("\"", element, "\"")
      } else if (is.numeric(element) || is.logical(element)) {
        json <- as.character(element) # No need for extra formatting
      } else {
        stop("Unsupported data type in the list")
      }
    } else {
      # If there are multiple elements, treat it as an array
      if (is.character(element)) {
        # Escape newlines for multi-line strings
        element <- gsub("\n", "\\\\n", element)
        json <- paste0("[\"", paste(element, collapse = "\", \""), "\"]")
      } else if (is.numeric(element) || is.logical(element)) {
        json <- paste0("[", paste(element, collapse = ", "), "]")
      } else {
        stop("Unsupported data type in the list")
      }
    }
    return(json)
  }
  
  # Initialize a JSON string
  json_str <- "{"
  
  # Iterate over the list and convert each element to JSON
  for (name in names(mylist)) {
    element_json <- convert_element_to_json(mylist[[name]])
    json_str <- paste0(json_str, "\"", name, "\": ", element_json, ", ")
  }
  
  # Remove the trailing comma and space, and close the JSON string
  json_str <- sub(", $", "", json_str)
  json_str <- paste0(json_str, "}")
  
  # Write the JSON string to the file
  write(json_str, file = file_path)
  
  return(TRUE)
}