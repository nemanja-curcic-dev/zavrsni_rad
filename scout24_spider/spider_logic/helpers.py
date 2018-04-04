# -*- coding: utf-8 -*-


def convert_seconds_to_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)


def make_slice(count):
    i = 2
    slices = [0]

    if count >= 100000:
        sl = count // i
        while sl > 100000:
            i += 1
            sl = count // i
    else:
        return [0, count]

    for k in range(i):
        slices.append(sl)
        sl += sl

    slices[len(slices) - 1] = count

    return slices
