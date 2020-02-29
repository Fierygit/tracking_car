import get_image
import time
import threading
import identify
import multiprocessing
import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np
from tracking import getTracker
from io import BytesIO
import tracking

image = bytes()
img_cnt = 0
all_img = dict()

fir_img_flag = 0
rec_v = 1
lock = multiprocessing.Lock()
# 图片更新速率大于tracking速率

process_list = list()
#  现在处理的图片, bytes 类型
(major_ver, minor_ver, subminor_ver) = (cv.__version__).split('.')


class TrackingProcess(threading.Thread):
    # 数据格式：  (  [img_cnt, [x,y,width_x,width_y]],  [ ]  ....)
    info = tuple()
    fir_img = bytes()
    def __init__(self, fir_img, *args, **kwargs):
        super(TrackingProcess, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()  # 用于暂停线程的标识
        self.__flag.set()  # 设置为True
        self.__running = threading.Event()  # 用于停止线程的标识
        self.__running.set()  # 将running设置为True
        print(len(fir_img))

    def setFirst(self, i):
        self.fir_img = i

    def addInfo(self, info):
        self.info += info

    def getInfo(self):
        return self.info

    def run(self):
        global lock, image, img_cnt, all_img
        tracker_type = 'KCF'  # 直接选取
        tracker = cv.Tracker_create(tracker_type)
        image_cnt_flag = -1
        cur_cnt = fir_img_cnt
        lose_cnt = 0
        fir_img_cnt = self.info[0][0]
        fir_loc = self.info[0][1]
        track_cnt = 0  # 统计 track 的次数

        # jpg 的 注意
        frame = plt.imread(BytesIO(self.fir_img),
                           "jpg")  # Bytes类型转为numpy.array类型
        frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)  # opencv中图片像素是以BGR方式排列
        #bbox = (52, 28, 184, 189)#这里四个参数分别为 起始坐标xy 和 宽 高         # 初始化第一张图片
        ok = tracker.init(frame,
                          (fir_loc[0], fir_loc[1], fir_loc[2], fir_loc[3]))
        print("[tracking process]: " + str(fir_img_cnt) + " x: " +
              str(fir_loc[0]) + " y: " + str(fir_loc[1]) +
              " started!***********************************************")

        while self.__running.isSet():
            self.__flag.wait()  # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
            # 调用真正的  里面不要再用  while 循环， 最后一行的 sleep 控制速率
            # 处理一张， 就重新获取一张图片
            cur_cnt += 1
            t_cnt = 1
            while cur_cnt not in all_img:
                time.sleep(0.1 * t_cnt)
                t_cnt += 1

            cur_image = all_img[cur_cnt]
            if image_cnt_flag != cur_cnt:
                image_cnt_flag = cur_cnt
            else:
                print("[tracking process]: " + str(fir_img_cnt) + " x: " +
                      str(fir_loc[0]) + " y: " + str(fir_loc[1]) +
                      " the car don't move")
                self.stop()
                # Bytes类型转为numpy.array类型
            frame = plt.imread(BytesIO(cur_image), "jpg")
            # opencv中图片像素是以BGR方式排列
            frame = cv.cvtColor(frame,  cv.COLOR_RGB2BGR)  
            ok, bbox = tracker.update(frame)
            # 设置阈值  #todo *******************
            if ok:
                # Tracking success
                p1 = (int(bbox[0]), int(bbox[1]))
                p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                print("[tracking process]: " + str(fir_img_cnt) + " x: " +
                      str(fir_loc[0]) + " y: " + str(fir_loc[1]) + "] ",
                      end="")
                print("track_num: " + str(track_cnt) + ", x: " + str(p1[0]) +
                      ", y: " + str(p1[1]))
                self.info += ([cur_cnt, bbox], )
                # 保存 信息！！
                # cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
            else:
                if lose_cnt < 4:     # 容忍四张图片
                    lose_cnt += 1
                    continue
                # 失败了， 要把自己从list中移除
                print("[tracking process]: " + str(fir_img_cnt) + " x: " +
                      str(fir_loc[0]) + " y: " + str(fir_loc[1]) +
                      "]  over******************************************")
                # 不一定移除成功
                process_list.remove(self)
                self.stop()

            # time.sleep(0.5)

    def pause(self):
        self.__flag.clear()  # 设置为False, 让线程阻塞

    def resume(self):
        self.__flag.set()  # 设置为True, 让线程停止阻塞

    def stop(self):
        self.__flag.set()  # 将线程从暂停状态恢复, 如何已经暂停的话
        self.__running.clear()  # 设置为False


def update_image():
    sock, conn = get_image.init_rec()
    global img_cnt
    global image
    global fir_img_flag
    global lock
    global all_img
    while True:
        # 确保 返回的一定是一张可行的图片
        # 接受图片的时候不占用锁
        image_temp = get_image.get_img(sock, conn)  # 用锁来保护， 赋值的时候
        # 防止 更新了一个数据后， 切换到另一个线程， 倒置数据不统一
        lock.acquire()
        image = image_temp
        if fir_img_flag == 0:
            fir_img_flag = 1
        img_cnt += 1
        lock.release()
        all_img[img_cnt] = image_temp
        time.sleep(1 / rec_v)
        # 控制速率


def main():
    global img_cnt, image, fir_img_flag, lock
    thread1 = threading.Thread(target=update_image, args=())  # 不可控， 会一直接受图片
    thread1.start()
    count = 0
    image_cnt_flag = -1
    while True:
        if fir_img_flag == 1:
            lock.acquire()
            temp_cnt = img_cnt
            temp_image = image
            lock.release()
            if image_cnt_flag != temp_cnt:
                image_cnt_flag = temp_cnt
            else:
                print("[main]: no image input !!!")
                time.sleep(1)
                continue
            # 处理图片, 返回图片上车的信息， 用一个list保存
            locations = identify.idnt_img(temp_image, temp_cnt)  # 1.2
            # 创建新的线程去跟踪新的车
            tracking.tracking(temp_image, locations, temp_cnt)
            del_not_use()
        else:
            time.sleep(0.5)


def del_not_use():
    global process_list
    min_cnt = -1
    for li in process_list:
        process_info = li.getInfo()
        if min_cnt == -1:
            min_cnt = process_info[0][0]
        elif min_cnt < process_info[0][0]:
            min_cnt = process_info[0][0]
    while min_cnt in all_img:
        all_img.pop(min_cnt)
        min_cnt -= 1


if __name__ == "__main__":
    main()