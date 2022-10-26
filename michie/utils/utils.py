

def rnb_filter_beacons(keys, neighbours):
    ret = []
    for neighbour in neighbours:
        ret.append(dict(
            distance=neighbour["distance"],
            angle=neighbour["angle"],
            point=neighbour["point"],
            beacon={key: neighbour["beacon"][key] for key in keys},
        ))
    return ret