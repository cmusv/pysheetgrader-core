def get_headers(header_names, row_values):
    """
    Takes a pre-defined dictionary and list of values
    and returns a dictionary with index of those values
    : param header_names: Dictionary where each pair is of type 'internal header name': ["list of all usable header names in sheet"]
    : param row_values: string list of values of all cells in the first row of a sheet
    """
    headers = {}
    # extract all values from first row, ignoring blanks and unidentified values
    header_index = {}
    for header in row_values:
        if header:
            headers[header.lower()] = row_values.index(header)

    for key, names in header_names.items():
        for header in headers:
            if header in names:
                header_index[key] = headers.pop(header)
                break
    return header_index
