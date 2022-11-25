""" funktion to flatten a list with lists inside """
import itertools


def flatten_list(list_of_lists) -> list[str]:
    """ flattens a list with lists inside """
    new_list = []
    for item in list_of_lists:
        if isinstance(item, list):
            new_list.extend(flatten_list(item))
        else:
            new_list.append(item)

    return list(set(new_list))


if __name__ == '__main__':
    print(flatten_list([["test"], ["test1", "test3"], ["test21", ["test51", "test34"]]]))
    print(flatten_list(["test23333", ["test"], ["test1", "test3"], ["test21", ["test", "test34"]]]))
