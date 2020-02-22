'''
@Author: Firefly
@Date: 2020-02-20 15:22:36
@Descripttion: 
@LastEditTime: 2020-02-20 16:37:49
'''

import time
from yolov3 import yolov3, getLocation
import get_image

def idnt_img(image):
    # time.sleep(1.2)

    # 实现识别代码
    yolov3(image)

    # 二元 元组
    loc = getLocation()
    print(loc)
    return loc

# idnt_img('../image/image1.jpg')

# sock , conn = get_image.init_rec()
# image, ret = get_image.get_img(sock, conn)
# idnt_img(image)
