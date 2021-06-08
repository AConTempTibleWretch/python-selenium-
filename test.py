import cv2
import numpy as np


def template_image():

    """
    干扰较多的图片 简单的灰度处理 无法完成匹配。
    需要去燥及一系列其他
    参考：
        https://blog.csdn.net/sinat_36458870/article/details/78825571?utm_medium=distribute.pc_relevant.none-task-blog-2%7Edefault%7EBlogCommendFromMachineLearnPai2%7Edefault-1.control&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2%7Edefault%7EBlogCommendFromMachineLearnPai2%7Edefault-1.control
    """
    target = cv2.imread("./image/bkBlock.png")
    tpl = cv2.imread("./image/slideBlock.png")

    target_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
    tpl_gray = cv2.cvtColor(tpl, cv2.COLOR_BGR2GRAY)
    cv2.imshow("target_gray", target_gray)
    cv2.imshow("tpl_gray", tpl_gray)
    target_blurred = cv2.GaussianBlur(target_gray, (9, 9), 0)
    tpl_blurred = cv2.GaussianBlur(tpl_gray, (9, 9), 0)
    cv2.imshow("target_blurred", target_blurred)
    cv2.imshow("tpl_blurred", tpl_blurred)
    target_gradX = cv2.Sobel(target_blurred, ddepth=cv2.CV_32F, dx=1, dy=0)
    target_graY = cv2.Sobel(target_blurred, ddepth=cv2.CV_32F, dx=0, dy=1)
    tpl_gradX = cv2.Sobel(tpl_blurred, ddepth=cv2.CV_32F, dx=1, dy=0)
    tpl_graY = cv2.Sobel(tpl_blurred, ddepth=cv2.CV_32F, dx=0, dy=1)

    target_gradient = cv2.subtract(target_gradX, target_graY)
    target_gradient = cv2.convertScaleAbs(target_gradient)
    tpl_gradient = cv2.subtract(tpl_gradX, tpl_graY)
    tpl_gradient = cv2.convertScaleAbs(tpl_gradient)
    cv2.imshow('target_final', target_gradient)
    cv2.imshow('tpl_final', tpl_gradient)

    methods = [cv2.TM_SQDIFF_NORMED, cv2.TM_CCORR_NORMED, cv2.TM_CCOEFF_NORMED]
    th, tw = tpl_gradient.shape[:2]
    for md in methods:
        result = cv2.matchTemplate(target_gradient, tpl_gradient, md)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if md == cv2.TM_SQDIFF_NORMED:
            tl = min_loc
        else:
            tl = max_loc
        br = (tl[0] + tw, tl[1] + th)
        print(tl)
        print(br)
        cv2.rectangle(target, tl, br, [0, 0, 0])
        cv2.imshow("pipei" + np.str(md), target)
        print(result.shape)
        print(result.argmax())
        y, x = np.unravel_index(result.argmax(), result.shape)

        print(x,y)

    """
        干扰比较少的图片 只需要做灰度处理，即可完成匹配
    """
    # target = cv2.imread("D:/Develop/PythonProject/python-selenium-/image/sunping.jpg", 0)
    # tpl = cv2.imread("D:/Develop/PythonProject/python-selenium-/image/sunping_face.jpg", 0)
    # cv2.imshow("yuan", target)
    # cv2.imshow("modul", tpl)
    # tpl = tpl[tpl.any(1)]
    # cv2.imshow("modul2", tpl)
    # methods = [cv2.TM_SQDIFF_NORMED, cv2.TM_CCORR_NORMED, cv2.TM_CCOEFF_NORMED]
    # # methods = [cv2.TM_SQDIFF_NORMED]
    # # print(tpl.shape)
    # # print(tpl.shape[:2])
    # # print(tpl.shape[::1])
    # th, tw = tpl.shape[:2]
    # for md in methods:
    #     result = cv2.matchTemplate(target, tpl, md)
    #     min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    #     if md == cv2.TM_SQDIFF_NORMED:
    #         tl = min_loc
    #     else:
    #         tl = max_loc
    #     br = (tl[0] + tw, tl[1] + th)
    #     print(tl)
    #     print(br)
    #     cv2.rectangle(target, tl, br, [0, 0, 0])
    #     cv2.imshow("pipei" + np.str(md), target)
    #     print(result.shape)
    #     print(result.argmax())
    #     y, x = np.unravel_index(result.argmax(), result.shape)
    #
    #     print(x,y)


template_image()
cv2.waitKey(0)
cv2.destroyAllWindows()