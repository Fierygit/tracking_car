'''
@Author: Firefly
@Date: 2020-02-20 14:39:48
@Descripttion: 

@LastEditTime: 2020-02-23 20:51:10

'''

import get_image
import time
import threading
import identify
import multiprocessing

image = bytes()
img_cnt = 0
lock = multiprocessing.Lock()

process_list = list();
#  现在处理的图片, bytes 类型

class TrackingProcess(threading.Thread):
    # 数据格式：  [[img_cnt, [x1,y1,x2,y2]],  ....]
    info = list()
    fir_img = bytes()
    
    def __init__(self, *args, **kwargs):
        super(TrackingProcess, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()     # 用于暂停线程的标识
        self.__flag.set()       # 设置为True
        self.__running = threading.Event()      # 用于停止线程的标识
        self.__running.set()      # 将running设置为True

    def setFirst(self,i):
        self.fir_img = i

    def addInfo(self, info):
        self.info.append(info)

    def getInfo(self, info):
        return self.info

    def run(self):
        
        fir_img_cnt = info[0]
        fir_loc = info[1]
        frame = cv2.imread( fir_img_cnt, cv2.IMREAD_ANYCOLOR)
        # 初始化第一张图片
        #bbox = (52, 28, 184, 189)#这里四个参数分别为 起始坐标xy 和 宽 高
        ok = tracker.init(frame, (fir_loc[0],fir_loc[1], (fir_loc[2] - fir_loc[0]),(fir_loc[3] - fir_loc[1])))  
        track_cnt = 0 # 统计 track 的次数
        print("tracking process: " + self.name + " x: " fir_loc[0] + " y: "+fir_loc[1] + "] is running!")
        while self.__running.isSet():
            self.__flag.wait()      # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回            
            # 调用真正的  里面不要再用  while 循环， 最后一行的 sleep 控制速率
            # 处理一张， 就重新获取一张图片
            # tracking(self.getImage())        
            lock.acquire()
            # 
            frame = cv2.imread(image,cv2.IMREAD_ANYCOLOR)# 不断获取图片并更新
            temp_cnt = img_cnt
            lock.release()
            ok, bbox = tracker.update(frame)
            if ok:
            # Tracking success
                p1 = (int(bbox[0]), int(bbox[1]))
                p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                print("[tracking process: " + self.name + " x: " fir_loc[0] + " y: "+fir_loc[1] + "] ",end="")
                print("track_num: " + track_cnt + ", x: " + p1[0] + ", y: " + p1[1])
                # cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
            else:
                # 失败了， 要把自己从list中移除
                print("[tracking process: "+ self.name + " x: " fir_loc[0] + " y: "+fir_loc[1] + "] over")
                list.remove(self)         
            time.sleep(1)

    def pause(self):
        self.__flag.clear()     # 设置为False, 让线程阻塞

    def resume(self):
        self.__flag.set()    # 设置为True, 让线程停止阻塞

    def stop(self):
        self.__flag.set()       # 将线程从暂停状态恢复, 如何已经暂停的话
        self.__running.clear()        # 设置为False 




def update_image():
    sock, conn = get_image.init_rec()
    while True:
        
        # 确保 返回的一定是一张可行的图片
        # 接受图片的时候不占用锁
        image_temp = get_image.get_img(sock, conn)  # 用锁来保护， 赋值的时候
        # 防止 更新了一个数据后， 切换到另一个线程， 倒置数据不统一
        lock.acquire()
        image = image_temp
        img_cnt = img_cnt + 1;
        lock.release()
        
        print(len(image), img_cnt)
        time.sleep(1)
        # 控制速率



def tracking(fir_img, locations, fir_img_cnt):
    
    visited = list()
    cnt_loc = 0
    for loc in locations:    # 对于每一个识别出来的车的位置
        print("width: " + str(loc[2] - loc[0]) + " height: " + str(loc[3] - loc[1]))
        flag = False # 判断有没有找到
        for li in process_list: # 查找有没有进程在处理这辆车
            if flag: break;
            process_info = li.getInfo() 
            # 不判空一定有
            if process_info[0][0] <= img_cnt: # 第一张必须要比之前的小
                for p : process_info: # 对于每一张 img_cnt
                    if(p[0] == img_cnt): # 同时时间上的图片
                        mid_cur = [(loc[2] - loc[0]), (loc[3]- loc[1])] # 当前图片中点
                        mid_p = [(p[1][2]-p[1][0]),(p[1][3] - p[1][1])] # p的中点
                        len_2 = (mid_p[0] - mid_cur[0])^2 + (mid_p[1] - mid_cur[1])^2 # 距离平方
                        if(len_2 < ((loc[2] - loc[0])/ 2)^2 ):
                             flag = True
                             break;
        
        if flag: 
            visited.append(1)
        else:
            visited.append(0)      
        cnt_loc = cnt_loc + 1; # 处理下一辆车

    cnt_loc = 0
    for flag in visited:
        if flag == 0:
            temp_thread = TrackingProcess()       
            temp_thread.setFirst(fir_img)  # 把 img cnt 和 车位置 加入
            temp_thread.add_info([img_cnt, locations[cnt_loc]])
            process_list.append(temp_thread) # 将进程加入列表， 然后 开始， 防止  
            temp_thread.start() # 线程里面跟踪不到了就去自动停止， 内部实现         
        cnt_loc = cnt_loc + 1;

def main():
    # 不可控， 会一直接受图片
    thread1 = threading.Thread(target=update_image, args=())
    thread1.start()

    while True:
        lock.acquire()
        temp_cnt = img_cnt
        temp_image = image
        lock.release()
        
        # 处理图片, 返回图片上车的信息， 用一个list保存
        locations = identify.idnt_img(temp_image) # 1.2 
        # 创建新的线程去跟踪新的车
        tracking(temp_image, locations, temp_cnt)
        


if __name__ == "__main__":
    # a = TrackingProcess()
    # a.setName("A")
    # a.start()
    # b = TrackingProcess()
    # b.setName("B")
    # b.start()
    # a.pause()
    # time.sleep(1)
    # b.stop()
    # a.resume()
    # time.sleep(1)
    # a.stop()
    # 以上测试线程
    main()




