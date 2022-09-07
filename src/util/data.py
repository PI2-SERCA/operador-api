def filter_data(data: list):
    """Filter data to remove any unnecessary values"""
    unnecessary_keys = ["gcode"]

    new_data = []
    for cut in data:
        new_cut = {k: v for k, v in cut.items() if k not in unnecessary_keys}
        new_data.append(new_cut)

    return new_data
