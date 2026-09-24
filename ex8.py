def extract_even(l):
    new_list = []
    for num in l:
        if num % 2 == 0:
            new_list.append(num)
    return new_list