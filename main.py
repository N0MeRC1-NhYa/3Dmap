import sys

import matplotlib as matplotlib
import matplotlib.pyplot as plt
from pylab import *
from mpl_toolkits.mplot3d import Axes3D, proj3d
import numpy as np
from bs4 import BeautifulSoup
import requests
import pandas as pd
from matplotlib import cm
from matplotlib.cbook import get_sample_data

log = ""
start_lat, start_lng = 53.44998655159218, 49.916351065118064
end_lat, end_lng = 53.34324196267707, 50.131362024076665
accuracy = 5

problematic_coordinates = list(tuple())

maxlat = 0
maxlng = 0
maxelv = 0

minlat = 0
minlng = 0
minelv = 10000

lat = [0.0] * accuracy ** 2
lng = [0.0] * accuracy ** 2

for i in range(accuracy):
    for j in range(accuracy):
        lat[i * accuracy + j] = start_lat - (start_lat - end_lat) * i / accuracy

for i in range(accuracy):
    for j in range(accuracy):
        lng[i * accuracy + j] = start_lng + (end_lng - start_lng) * j / accuracy

elevation = [0] * accuracy ** 2
cnt = 0
procent_cnt = 0
download_progress = "[____________________]"
print("Getting info from API ... " + download_progress + ' - {}%'.format(cnt / accuracy * 100), end="", flush=True)
for i in range(accuracy):
    for j in range(accuracy):
        try:
            r = requests.get(f"https://maps.googleapis.com/maps/api/elevation/json?locations={lat[i * accuracy + j]},{lng[j]}&key=AIzaSyA3433BXtsJ0nes00HOD7V0qPZDyDzIrOo")
            elev = r.json().get("results")[0].get("elevation")
            elevation[i * accuracy + j] = elev
            if elev > maxelv:
                maxelv = elev
                maxlat = i
                maxlng = j
            if elev < minelv:
                minelv = elev
                minlat = i
                minlng = j
        except Exception as e:
            problematic_coordinates.append((i, j))
            log = log + f"Getting problems with current cooredinates: {lat[i * accuracy + j]}, {lng[j]} in main field\n"
    cnt = cnt + 1
    print("", end="\r")
    if int(cnt / accuracy * 100) / 5 > procent_cnt:
        download_progress = download_progress.replace("_", "+", int(int(cnt / accuracy * 100 / 5) - procent_cnt))
        procent_cnt = int(int(cnt / accuracy * 100) / 5)
    print(f"Getting info from API ... {download_progress} - {cnt / accuracy * 100} %", end="", flush=True)
print()
print("Dealing with problematic coordinates... Current count: " + str(len(problematic_coordinates)))

total_problems = len(problematic_coordinates)

while len(problematic_coordinates) > 0:
    print("", end="\r")
    print(f"Percentage of the problematic coordinates fixed: { int((1 - (len(problematic_coordinates) / total_problems)) * 100)} %", end="", flush=True)
    first, second = problematic_coordinates[0]
    try:
        r = requests.get(f"https://maps.googleapis.com/maps/api/elevation/json?locations={lat[first * accuracy + second]},{lng[second]}&key=AIzaSyA3433BXtsJ0nes00HOD7V0qPZDyDzIrOo")
        elev = r.json().get("results")[0].get("elevation")
        if elev > maxelv:
            maxelv = elev
            maxlat = first
            maxlng = second
        if elev < minelv:
            minelv = elev
            minlat = first
            minlng = second
        elevation[first * accuracy + second] = elev
        problematic_coordinates.pop(0)
    except Exception as e:
        log = log + f"Getting problems with current cooredinates: {lat[first * accuracy + second]}, {lng[second]} in problematic field field\n"

with open("./log.txt", "w") as file:
    file.write(log)

# ans = pd.DataFrame({"Latitude": lat, "Longitude": lng, "Elevation": elevation})
# ans.to_excel("./data/Khvalinsk_15_meter.xlsx")

fig = plt.figure()
ax = Axes3D(fig, auto_add_to_figure=False)
fig.add_axes(ax)

surf = ax.plot_trisurf(lat, lng, elevation, cmap=cm.jet, linewidth=0.1)
ax.scatter(lat[maxlat * accuracy + maxlng], lng[maxlat * accuracy + maxlng], maxelv, color="blue", marker="o", s=75)
ax.scatter(lat[minlat * accuracy + minlng], lng[minlat * accuracy + minlng], minelv, color="red", marker="o", s=75)
#ax.view_init(40, -200)
fig.colorbar(surf, shrink=0.5, aspect=5)
ax.set_zbound(0, maxelv * 1.5)
plt.show()


#plt.savefig('Khvalinsk_15_meter.pdf',bbox_inches='tight')

# r = requests.get("https://maps.googleapis.com/maps/api/elevation/json?locations=53.448919105703034,50.08513466790057&key=AIzaSyA3433BXtsJ0nes00HOD7V0qPZDyDzIrOo")
# print(r.json())
