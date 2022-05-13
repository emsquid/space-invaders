def get_config():
    """get the configuration from the .config.txt file if it exists"""
    try:
        with open(".config.txt", "r") as config_file:
            name = config_file.readline().strip()
            style = int(config_file.readline().strip())
            controls = eval(config_file.readline().strip())
    except:
        name = None
        style = None
        controls = None
    return name, style, controls


def save_config(name, style, controls):
    """save the configuration to the .config.txt file"""
    with open(".config.txt", "w") as config_file:
        config_file.write(name + "\n")
        config_file.write(str(style) + "\n")
        config_file.write(str(controls) + "\n")
