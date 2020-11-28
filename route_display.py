import folium
from typing import List, Tuple


def print_trace(Location: List[List[float]]):
    """
    Save the map with route locally.
    :param Location: list of latitude and longtitude of all locations on the route.
                   List[float] : the length is 2, while the first element is latitude
                                                and the second element is longtitude.
    """

    m = folium.Map(zoom_start=10)
    for latitude, longtitude in Location:
        folium.Marker(
            [latitude, longtitude], popup='<i>Latitude:</i>'+str(latitude)+'<br><i>Longtitude:</i>'+str(longtitude)
        ).add_to(m)
    route = folium.PolyLine(
        Location,  # 要连接的坐标点
        weight=10,  # 线的大小
        color='orange',  # 线的颜色
        opacity=0.5,  # 线的透明度
    ).add_to(m)
    m.save('route_display.html')
