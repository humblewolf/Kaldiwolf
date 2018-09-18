"""
Author: humblewolf
Description: <write description here...>
"""

import math
import itertools

def clockwiseangle_and_distance(point):
    vector = [point[0]-origin[0], point[1]-origin[1]]
    lenvector = math.hypot(vector[0], vector[1])
    if lenvector == 0:
        return -math.pi, 0
    normalized = [vector[0]/lenvector, vector[1]/lenvector]
    dotprod  = normalized[0]*refvec[0] + normalized[1]*refvec[1]
    diffprod = refvec[1]*normalized[0] - refvec[0]*normalized[1]
    angle = math.atan2(diffprod, dotprod)
    if angle < 0:
        return 2*math.pi+angle, lenvector
    return angle, lenvector

def PolygonArea(corners):
    n = len(corners)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += corners[i][0] * corners[j][1]
        area -= corners[j][0] * corners[i][1]
    area = abs(area) / 2.0
    return area

# idea is to find the area of biggest polygon in the given set of points

pts = [(10, 10), (0, 0), (0, 10), (5,5), (10,0)]
#pts = [(6, 39), (28, 25), (28,13),(31,3),(11,19),(31,17),(26,19),(18,13),(30,11),(25,20)]

origin = pts[0]
refvec = [0, 1]
init_set_size = 3
max_set_size = len(pts)+1
#print(max_set_size)
area_list = []

for i in range(init_set_size, max_set_size, 1):
    #print(i)
    comb = list(itertools.combinations(pts, i))
    for n in comb:
        corners = sorted(n, key=clockwiseangle_and_distance)
        area_list.append(PolygonArea(corners))

area_list.sort(reverse=True)
print(area_list[0])