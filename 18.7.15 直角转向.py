# 直角追踪 - By: Jack Zhang - 周日 7月 15 2018

# if 找到直角:
#     if 范围外:
#         飞过去
#     else:
#         转角度:
#转角度：
    #if

enable_lens_corr = False # turn on for straighter lines...

import sensor, image, time

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE) # grayscale is faster
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 2000)
clock = time.clock()

# 判断是否为直角的阈值
right_angle_threshold = (70, 90)
binary_threshold = [(145,0)]
forget_ratio = 0.3
move_threshold = 5
angle_XY = []   # (x,y,distance)存放每一帧图像中直角顶点的坐标值,距离上一个点的距离
old_cross_x = 0 # 上一个点（经forget处理过）
old_cross_y = 0
old_theta_1 = 0
old_theta_2 = 0
a = 0           # 记等待直角次数


def calculate_angle(line1, line2):
    # 利用四边形的角公式， 计算出直线夹角
    angle  = (180 - abs(line1.theta() - line2.theta()))
    if angle > 90:
        angle = 180 - angle
    return angle
def is_right_angle(line1, line2):
    global right_angle_threshold
    # 判断两个直线之间的夹角是否为直角
    angle = calculate_angle(line1, line2)
    if angle >= right_angle_threshold[0] and angle <=  right_angle_threshold[1]:
    # 判断在阈值范围内
        return True
    return False
def calculate_intersection(l1, l2):
    area_abc = (l1.x1() - l2.x1()) * (l1.y2() - l2.y1()) - (l1.y1() - l2.y1()) * (l1.x2() - l2.x1())
    area_abd = (l1.x1() - l2.x2()) * (l1.y2() - l2.y2()) - (l1.y1() - l2.y2()) * (l1.x2() - l2.x2())
    if area_abc * area_abd > 0:
    #c,d在ab同侧，无交点
        return (-1,-1)
    area_cda = (l2.x1() - l1.x1()) * (l2.y2() - l1.y1()) - (l2.y1() - l1.y1()) * (l2.x2() - l1.x1())
    area_cdb = area_cda - area_abd + area_abc
    if area_cda * area_cdb > 0:
    #a,b在cd同侧，无交点
        return (-1,-1)
    k = area_cda/(area_abd - area_abc)
    cross_x = (int)(k * (l1.x2() - l1.x1()) + l1.x1())
    cross_y = (int)(k * (l1.y2() - l1.y1()) + l1.y1())
    return (cross_x,cross_y)
def find_verticle_lines(lines):
    #遍历所有直线
    line_num = len(lines)
    global angle_XY
    global old_cross_x
    global old_cross_y
    angle_XY = []
    for i in range(line_num -1):
        for j in range(i, line_num):
            if is_right_angle(lines[i], lines[j]):
            # 有直角，存储(x,y,到上一个的距离)
                (cross_x,cross_y) = calculate_intersection(lines[i], lines[j])
                if cross_x != -1 and cross_y != -1:
                    angle_XY.append([cross_x,cross_y,dis_to_old(cross_x,cross_y,old_cross_x,old_cross_y),lines[i],lines[j]])
                    img.draw_cross(cross_x,cross_y)
    return len(angle_XY)
    #失败，无直角点，返回值为0
def draw_cross_point(cross_x, cross_y):
    img.draw_cross(cross_x, cross_y)
    img.draw_circle(cross_x, cross_y, 5)
    img.draw_circle(cross_x, cross_y, 10)
def dis_to_old(x1,y1,x0,y0):
    return (x1 - x0)*(x1 - x0) + (y1 - y0)*(y1 - y0)

while(True):
    clock.tick()
    img = sensor.snapshot()
    #img.binary(binary_threshold)
    #img.gaussian(5)
    #img.gaussian(5)

    # 去除摄像头畸变， 这里我们采用的是13.8mm的，近距离没有畸变效果
    if enable_lens_corr: img.lens_corr(1.8) # for 2.8mm lens...

    # `threshold` controls how many lines in the image are found. Only lines with
    # edge difference magnitude sums greater than `threshold` are detected...

    # More about `threshold` - each pixel in the image contributes a magnitude value
    # to a line. The sum of all contributions is the magintude for that line. Then
    # when lines are merged their magnitudes are added togheter. Note that `threshold`
    # filters out lines with low magnitudes before merging. To see the magnitude of
    # un-merged lines set `theta_margin` and `rho_margin` to 0...

    # `theta_margin` and `rho_margin` control merging similar lines. If two lines
    # theta and rho value differences are less than the margins then they are merged.

    lines =  img.find_lines(threshold = 2000, theta_margin = 70, rho_margin = 30, roi=(5, 5, 150,110))
    #lines = img.find_line_segments(merge_distance = 10, max_theta_diff = 15)

    if len(lines) >= 2:
    # 找直角
        if find_verticle_lines(lines):
        # 找最靠近上一个的目标直角，记为t
            t = 0
            if old_cross_x == 0 and old_cross_y == 0:
                old_cross_x = angle_XY[t][0]
                old_cross_y = angle_XY[t][1]
                print(angle_XY[t][3][6],angle_XY[t][4][6])
                if (0<=angle_XY[t][3][6]<45) or (180>angle_XY[t][3][6]>135):
                    # 使3为目标线，4为航向线
                    angle_XY[t][3],angle_XY[t][4] = angle_XY[t][4],angle_XY[t][3]
                    old_theta_1 = angle_XY[t][3][6]
                    old_theta_2 = angle_XY[t][4][6]
                    print(1 )
                    print(old_theta_1,old_theta_2)
            else:
                for i in range(1,len(angle_XY)):
                    if angle_XY[t][2] > angle_XY[i][2]: t = i
                if angle_XY[t][2] > 2000:
                    a+=1
                    if a<20:
                        continue
                    else:
                        print("new!!!")
                        a = 0
                        old_cross_x = 0
                        old_cross_y = 0
                        continue
                # 如果目标直角t和上一次相差过大，认为这一图像没拍到这个点，再重拍，直到10次

                # 已确定角，为angle_XY[t],(x,y,dis,line[i],line[j])

                # 1.稳定点
                (cross_x,cross_y) = angle_XY[t][0:2]
                if abs(cross_x - old_cross_x) < move_threshold and abs(cross_y - old_cross_y) < move_threshold:
                    # 小于移动阈值， 不移动
                    pass
                else:
                    old_cross_x = int(old_cross_x * (1 - forget_ratio) + cross_x * forget_ratio)
                    old_cross_y = int(old_cross_y * (1 - forget_ratio) + cross_y * forget_ratio)

                # 2.稳定直线偏角,先固定，再稳定
                if abs(angle_XY[t][3][6] - old_theta_1) <20 or 160<abs(angle_XY[t][3][6] - old_theta_1)<180:
                    pass
                else:
                    angle_XY[t][3],angle_XY[t][4] = angle_XY[t][4],angle_XY[t][3]
                old_theta_1 = angle_XY[t][3][6]
                old_theta_2 = angle_XY[t][4][6]

            #print(old_cross_x,old_cross_y)
            print(old_theta_1,old_theta_2)
            draw_cross_point(old_cross_x, old_cross_y)
            img.draw_line(angle_XY[t][3][0:4],[255,0,0])
            img.draw_line(angle_XY[t][4][0:4],[0,255,0])

    #print("FPS %f" % clock.fps())
