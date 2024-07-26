from os.path import dirname, join
def path(filename):
    '''This gets a file associated in the working directory no matter where you run it.
        Useful for VSCode where the terminal doesn't always reside in the directory you are working out of.
        REQUIRES --- 
        from os.path import dirname, join

    '''
    current_dir = dirname(__file__)  # get current working directory
    file_path = join(current_dir, f"{filename}")  # set file path
    return(file_path)