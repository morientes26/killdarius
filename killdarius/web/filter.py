def count_done_task(progress_list):
    count = 0
    for p in progress_list:
        if p.done:
            count = count + 1
    return count


def count_fail_task(progress_list):
    count = 0
    for p in progress_list:
        if not p.done:
            count = count + 1
    return count

