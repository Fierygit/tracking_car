'''
@Author: Firefly
@Date: 2020-02-20 15:22:36
@Descripttion: 
@LastEditTime: 2020-02-23 21:16:24
'''

import time
from yolov3 import yolov3, getLocation
import get_image


def idnt_img(image, count):
    # time.sleep(1.2)

    # 实现识别代码
    # with open('../image/image.jpg', 'rb') as f:
    #     image = f.read()

    yolov3(image, count)
    
    # 二元 数组
    loc = getLocation()
    print("\tident cars: " + str(loc))
    return loc

def test():
    sock , conn = get_image.init_rec()
    image, ret = get_image.get_img(sock, conn)
    idnt_img(image, 1)

if __name__ == "__main__":
    test()
