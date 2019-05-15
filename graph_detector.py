
MIDDLE_LEFT = 0.3
MIDDLE_RIGHT = 0.7

GRAPH_TYPE_UNKNOWN = 0
GRAPH_TYPE_INCREASING = 1
GRAPH_TYPE_DECREASING = 2
GRAPH_TYPE_UP_AND_DOWN = 3
GRAPH_TYPE_DOWN_AND_UP = 4


def detect_graph(y_line):
    return detect_graph_ext(y_line, False)


def detect_graph_ext(y_line, recursive_call):
    y_line = clean_endings(y_line)

    if not validate_graph(y_line):
        return GRAPH_TYPE_UNKNOWN

    last_index = len(y_line) - 1

    first_value = y_line[0]
    last_value = y_line[last_index]

    diffs = [y_line[index] - y_line[index-1] for index in range(1, len(y_line))]

    ascend_sum = sum_by_condition(diffs, lambda x: x if x > 0 else 0.0)
    abs_ascend_sum = abs(ascend_sum)

    descend_sum = sum_by_condition(diffs, lambda x: x if x < 0 else 0.0)
    abs_descend_sum = abs(descend_sum)

    min_index = get_min_index(y_line)
    max_index = get_max_index(y_line)

    if (first_value < last_value) \
        and (abs_ascend_sum * 0.2 >= abs_descend_sum) \
        and index_in_left(min_index, len(y_line)) \
        and index_in_right(max_index, len(y_line)):
        return GRAPH_TYPE_INCREASING

    if (first_value > last_value) \
        and (abs_ascend_sum <= abs_descend_sum * 0.2) \
        and index_in_left(max_index, len(y_line)) \
        and index_in_right(min_index, len(y_line)):
        return GRAPH_TYPE_DECREASING

    if recursive_call:
        return GRAPH_TYPE_UNKNOWN

    if index_in_middle(max_index, len(y_line)) \
        and detect_graph_ext(y_line[0: max_index], True) == GRAPH_TYPE_INCREASING \
        and detect_graph_ext(y_line[max_index: len(y_line)], True) == GRAPH_TYPE_DECREASING:
        return GRAPH_TYPE_UP_AND_DOWN

    if index_in_middle(min_index, len(y_line)) \
        and detect_graph_ext(y_line[0: min_index+1], True) == GRAPH_TYPE_DECREASING \
        and detect_graph_ext(y_line[min_index: len(y_line)], True) == GRAPH_TYPE_INCREASING:
        return GRAPH_TYPE_DOWN_AND_UP

    return GRAPH_TYPE_UNKNOWN


def index_in_left(index, length):
    return index < length * MIDDLE_LEFT


def index_in_middle(index, length):
    return (index > 0) and (index < length-1)


def index_in_right(index, length):
    return index > (length-1) * MIDDLE_RIGHT


def validate_graph(y_line):
    y_line_length = len(y_line)
    if y_line_length == 0 or y_line_length == 1:
        return False
    else:
        return True


def sum_by_condition(list_x, condition):
    result = 0.0
    for x in list_x:
        result += x if condition(x) else 0.0

    return result


def get_min_index(list_x):
    min_index = 0
    min_value = list_x[0]
    for index in range(1, len(list_x)):
        if list_x[index] < min_value:
            min_value = list_x[index]
            min_index = index

    return min_index


def get_max_index(list_x):
    max_index = 0
    max_value = list_x[0]
    for index in range(1, len(list_x)):
        if list_x[index] >= max_value:
            max_value = list_x[index]
            max_index = index

    return max_index


def clean_endings(y_line):
    y_line = clean_begin_ending(y_line)
    y_line = reverse_line(y_line)
    y_line = clean_begin_ending(y_line)
    return reverse_line(y_line)


def reverse_line(y_line):
    result = []
    length = len(y_line)
    for idx in range(0, length):
        result.append(y_line[length - 1 - idx])

    return result


def clean_begin_ending(y_line):
    length = len(y_line)

    result = [y_line[0]]
    begin_ending = True
    for idx in range(1, length-1):
        if begin_ending and y_line[idx] == y_line[0]:
            continue
        else:
            begin_ending = False
        result.append(y_line[idx])

    result.append(y_line[length - 1])
    return result


def generate_graph(index):
    if index == 0:
        return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    if index == 1:
        return [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    if index == 2:
        return [0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0]
    if index == 3:
        return [0.0, 0.1, 0.2, 0.3, 0.2, 0.1, 0.0]
    if index == 4:
        return [0.6, 0.5, 0.4, 0.3, 0.4, 0.5, 0.6]
    if index == 5:
        return [0.1, 0.0, 0.2, 0.3, 0.4, 0.5, 0.6]
    if index == 6:
        return [0.5, 0.6, 0.4, 0.3, 0.2, 0.1, 0.0]
    if index == 7:
        return [0.0, 0.0, 0.0, 0.9, 0.9, 0.9, 0.9]
    if index == 8:
        return [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9747292418772564,
                0.9747292418772564, 0.9891696750902528, 0.9891696750902528, 0.9891696750902528, 0.9891696750902528,
                0.9891696750902528, 0.9927797833935018, 0.9927797833935018, 0.9927797833935018, 0.9927797833935018,
                0.9927797833935018, 0.9927797833935018, 0.9927797833935018]

    return [0.0, 0.6]


if __name__ == "__main__":
    # Some kind of test
    for index in range(0, 9):
        y_line = generate_graph(index)
        graph_type = detect_graph(y_line)
        print "Graph type: {}".format(graph_type)
