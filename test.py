import cv2
import numpy as np


def template_image():
    target = cv2.imread("./image/bkBlock.png", 0)
    tpl = cv2.imread("./image/slideBlock.png", 0)
    target = cv2.imread("D:/Develop/PythonProject/python-selenium-/image/sunping.jpg", 0)
    tpl = cv2.imread("D:/Develop/PythonProject/python-selenium-/image/sunping_face.jpg", 0)
    cv2.imshow("modul", tpl)
    cv2.imshow("yuan", target)
    methods = [cv2.TM_SQDIFF_NORMED, cv2.TM_CCORR_NORMED, cv2.TM_CCOEFF_NORMED]
    methods = [cv2.TM_SQDIFF_NORMED]
    # print(tpl.shape)
    # print(tpl.shape[:2])
    # print(tpl.shape[::1])
    th, tw = tpl.shape[:2]
    for md in methods:
        result = cv2.matchTemplate(target, tpl, md)
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


template_image()
cv2.waitKey(0)
cv2.destroyAllWindows()