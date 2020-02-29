'''
@Author: Firefly
@Date: 2020-02-29 22:03:44
@Descripttion: 
@LastEditTime: 2020-02-29 23:17:04
'''

from main import TrackingProcess


def tracking(fir_img, locations, fir_img_cnt, process_list):
    visited = list()
    cnt_loc = 0
    for loc in locations:  # 对于每一个识别出来的车的位置
        print("[prime tracking]: " + " width: " + str(loc[2]), end="")
        print(" height: " + str(loc[3]) + " pro_len " + str(len(process_list)))
        flag = 0  # 判断有没有找到
        for li in process_list:  # 查找有没有进程在处理这辆车
            # 一开始就固定  visited 的大小，# if visited[cnt] : break;   
            if flag == 1: break
            process_info = li.getInfo()
            print("[prime tracking]: " + str(process_info))       
            print("[prime tracking]: " + str(fir_img_cnt), end=' \t ')# 不判空一定有
            if process_info[0][0] <= fir_img_cnt :  # 第一张必须要比之前的小
                if len(process_info) + process_info[0][0] >= fir_img_cnt:      
                    flag = prime_one_car(loc, process_info[fir_img_cnt])
                    if flag == 1:
                        break                 
        visited.append(flag)
        cnt_loc = cnt_loc + 1  # 处理下一辆车
    cnt_loc = 0

    for flag in visited:
        if flag == 0:
            temp_thread = TrackingProcess(fir_img)
            temp_thread.setFirst(fir_img)  # 把 img cnt 和 车位置 加入
            temp_thread.addInfo(([fir_img_cnt, locations[cnt_loc]], ))
            process_list.append(temp_thread)  # 将进程加入列表， 然后 开始， 防止
            temp_thread.start()  # 线程里面跟踪不到了就去自动停止， 内部实现
        cnt_loc = cnt_loc + 1


def prime_one_car(loc, p):
    # 当前图片中点
    mid_cur = [loc[0] + loc[2] / 2, (loc[1] + loc[3] / 2)]
    mid_p = [(p[2] / 2 + p[0]), (p[3] / 2 + p[1])]  # p的中点
    len_2 = (mid_p[0] - mid_cur[0]) * (mid_p[0] - mid_cur[0]) + (
        mid_p[1] - mid_cur[1]) * (mid_p[1] - mid_cur[1])  # 距离平方
    print(str(len_2) + '\t' + str(((loc[2]) / 2) * ((loc[2]) / 2)))
    if (len_2 < ((loc[2]) / 2) * ((loc[2]) / 2)):
        return 1

    return 0