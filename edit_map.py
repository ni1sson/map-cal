import cv2
import numpy
from matplotlib import pyplot as plt
from sympy import symbols, solve
from pdf2image import convert_from_path

map_name = "out.jpg"
res = 600
img_type = 'JPEG'
cals = []
consts = {}


def main_menu():
    choice = '0'
    while choice == '0':
        print("Main menu:")
        print("Choose 1 to add calibration point")
        print("Choose 2 to add map")
        print("Choose 3 to print coordinates and constants")
        print("Choose 4 to calibrate map")
        print("Choose 5 to get map coordinate")
        print("Choose 100 to add demo points, for debug purpose only...")

        choice = input("Please make a choice: ")

        if choice == "1":
            add_calibration_point(map_name)
        elif choice == "2":
            add_map()
        elif choice == "3":
            print_coordinates()
        elif choice == "4":
            calibrate_map()
        elif choice == "5":
            get_map_coordinate(map_name)
        elif choice == "100":
            cals.append({"x_map": 1301.9693276827265, "y_map": 2148.995359383637,
                         "y_real": 63.1956050, "x_real": 14.6676817})  # bom
            cals.append({"x_map": 2897.459428, "y_map": 6758.269936,
                         "y_real": 63.182453, "x_real": 14.677883})  # sten
            cals.append({"x_map": 3594.270359848485, "y_map": 668.4705956246136,
                         "y_real": 63.1995500, "x_real": 14.6865717})  # vägkors 63.1995500°, 014.6865717°
            cals.append({"x_map": 3065.132882, "y_map": 6052.153161,
                         "y_real": 63.184740, "x_real": 14.678717})  # stigkors
            main_menu()
        else:
            print("don't understand your choice")
            main_menu()


def onclick_add(event):
    if event.button == 3:
        # print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %('double' if event.dblclick else 'single', event.button,event.x, event.y, event.xdata, event.ydata))*/
        plt.close('all')
        y = input("Please enter lat coordinate (in format: 63.42423): ")
        x = input("Please enter lon coordinate  (in format: 15.34535): ")
        c = {"x_map": event.xdata, "y_map": event.ydata, "x_real": x, "y_real": y}
        cals.append(c)
        main_menu()
    else:
        print('only right click')


def onclick_get(event):
    if event.button == 3:
        plt.close('all')
        x = consts["k_x"]*event.xdata+consts["m_x"]
        y = consts["k_y"]*event.ydata+consts["m_y"]
        print("Lat: " + str(y) + " Lon: " + str(x))
        print(str(y) + ", " + str(x))
        main_menu()
    else:
        print('only right click')


def add_calibration_point(map_name):
    img = cv2.imread(map_name)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    fig, ax = plt.subplots()
    ax.imshow(img)
    ax.axis('off')  # clear x-axis and y-axis
    fig.canvas.mpl_connect('button_press_event', onclick_add)
    plt.show()


def get_map_coordinate(map_name):
    if len(consts.values()) == 4:
        img = cv2.imread(map_name)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        fig, ax = plt.subplots()
        ax.imshow(img)
        ax.axis('off')  # clear x-axis and y-axis
        fig.canvas.mpl_connect('button_press_event', onclick_get)
        plt.show()
    else:
        print("not yet calibrated")
        main_menu()


def print_coordinates():
    # for c in cals:
    # print("map x=%f, map y=%f, real x=%f, real y=%f" % (float(c["x_map"]), float(c["y_map"]), float(c["x_real"]), float(c["y_real"])))
    # print(c)
    print(cals)
    print(consts)
    main_menu()


def calibrate_map():
    if len(cals) > 1:

        # y=kx+m
        k_xs = []
        k_ys = []
        m_xs = []
        m_ys = []
        for c in range(3):
            i = c+1
            # x=map pixel
            # y=coordinate
            # Lon, x:
            x1 = cals[0]["x_map"]
            x2 = cals[i]["x_map"]
            y1 = cals[0]["x_real"]
            y2 = cals[i]["x_real"]
            # k const
            k = symbols('k')
            expr = (y2-y1+k*x1)/x2-k
            sol = solve(expr)
            # print(sol)
            #consts["k_x"] = sol[0]
            k_xs.append(sol[0])
            # m konst
            m = symbols('m')
            expr = y1-(y2-m)*x1/x2-m
            sol = solve(expr)
            # print(sol)
            #consts["m_x"] = sol[0]
            m_xs.append(sol[0])

            # Lat, y:
            x1 = cals[0]["y_map"]
            x2 = cals[i]["y_map"]
            y1 = cals[0]["y_real"]
            y2 = cals[i]["y_real"]
            # k const
            k = symbols('k')
            expr = (y2-y1+k*x1)/x2-k
            sol = solve(expr)
            # print(sol)
            #consts["k_y"] = sol[0]
            k_ys.append(sol[0])
            # m const
            m = symbols('m')
            expr = y1-(y2-m)*x1/x2-m
            sol = solve(expr)
            # print(sol)
            #consts["m_y"] = sol[0]
            m_ys.append(sol[0])
        consts["k_x"] = numpy.mean(k_xs)
        consts["m_x"] = numpy.mean(m_xs)
        consts["k_y"] = numpy.mean(k_ys)
        consts["m_y"] = numpy.mean(m_ys)
    else:
        print("need two or more cal points")
    main_menu()


def add_map():
    pdf = input("enter PDF file name with file extension: ")
    try:
        pages = convert_from_path(pdf, res)
        pages[0].save(map_name, img_type)
    except:
        print("bad name")
    main_menu()


main_menu()


# 1:{'k_x': 6.39383472073672e-6, 'm_x': 14.6593571233073, 'k_y': -2.85337742010866e-6, 'm_y': 63.2017368948343}
# 2:{'k_x': 6.25880677545792e-6, 'm_x': 14.6595329255504, 'k_y': -2.78364353998272e-6, 'm_y': 63.2015870370497}
# 1,2: {'k_x': 6.32632074809732e-6, 'm_x': 14.6594450244289, 'k_y': -2.81851048004569e-6, 'm_y': 63.2016619659420}
# ... {'k_x': 6.96442315520564e-6, 'm_x': 14.6586142346669, 'k_y': -2.76720557154335e-6, 'm_y': 63.2015517119317}
