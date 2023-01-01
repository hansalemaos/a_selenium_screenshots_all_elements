import os
from random import randrange
from time import sleep
import numpy as np
import cv2
import regex
import pandas as pd
from a_selenium_screenshot_whole_page import get_screenshot_whole_page_with_scroll
from check_if_nan import is_nan
from a_cv_imwrite_imread_plus import open_image_in_cv, save_cv_image
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

import PILasOPENCV
from a_selenium2df import get_df


def cropimage(img, coords):
    return img[coords[1] : coords[3], coords[0] : coords[2]].copy()


def get_screenshots_from_all_elements(driver, saveinfolder, cutinfos=80):
    schot = get_screenshot_whole_page_with_scroll(driver)
    driver.execute_script(f"window.scrollTo(0, 0);")
    sleep(1)
    df = get_df(
        driver,
        By,
        WebDriverWait,
        expected_conditions,
        queryselector="*",
        with_methods=False,
    )
    allimageresults = []
    possibleelements = df.loc[
        (~df.aa_offsetTop.isna())
        & (~df.aa_offsetWidth.isna())
        & (~df.aa_clientWidth.isna())
        & (~df.aa_clientHeight.isna())
    ].copy()
    saveinfoldercomplete = os.path.join(saveinfolder, "complete")
    saveinfoldercut = os.path.join(saveinfolder, "single_elements")

    if not os.path.exists(saveinfolder):
        os.makedirs(saveinfolder)
    if not os.path.exists(saveinfoldercomplete):
        os.makedirs(saveinfoldercomplete)
    if not os.path.exists(saveinfoldercut):
        os.makedirs(saveinfoldercut)
    for key, item in possibleelements.iterrows():
        try:
            offset_x = int(item.aa_offsetLeft)
            offset_y = int(item.aa_offsetTop)  # - _
            width = int(item.aa_scrollWidth)
            height = int(item.aa_scrollHeight)
            start_x = int(offset_x)
            start_y = int(offset_y)
            end_x = start_x + width
            end_y = int(start_y + (height))
            print(start_x, start_y, end_x, end_y, end="\r")

            cutim = cropimage(img=schot, coords=(start_x, start_y, end_x, end_y)).copy()
            bi = PILasOPENCV.fromarray(schot.copy())
            ba = PILasOPENCV.ImageDraw(bi)
            r_, g_, b_ = (
                randrange(50, 255),
                randrange(50, 255),
                randrange(50, 255),
            )
            ba.rectangle(
                xy=(
                    (start_x, start_y),
                    (end_x, end_y),
                ),
                outline="black",
                width=4,
            )
            ba.rectangle(
                xy=(
                    (start_x, start_y),
                    (end_x, end_y),
                ),
                outline=(r_, g_, b_),
                width=2,
            )
            texttoput = "\n".join(
                [
                    regex.sub("^aa_", "", str(x)[:24].ljust(24))
                    + " "
                    + str(y)
                    .strip()
                    .replace("\n", "\\n")
                    .replace("\r", "\\r")[:cutinfos]
                    for x, y in zip(item.index, item.to_list())
                    if (str(x).startswith("aa_") or str(x) == "frame") and not is_nan(y)
                ]
            )
            ba.text(
                xy=((5, 5)),
                text=texttoput,
                fill="black",
                font=cv2.FONT_HERSHEY_DUPLEX,
                scale=0.50,
                thickness=2,
            )
            ba.text(
                xy=((5, 5)),
                text=texttoput,
                fill=(r_, g_, b_),
                font=cv2.FONT_HERSHEY_DUPLEX,
                scale=0.50,
                thickness=1,
            )
            # allimages_screen.append(rgb_bgr(bi.getim().copy()))
            if np.any(cutim):
                allimageresults.append(
                    (
                        item.copy(),
                        texttoput,
                        cutim.copy(),
                        open_image_in_cv(
                            bi.getim().copy(), channels_in_output=3, bgr_to_rgb=True
                        ),
                    )
                )

        except Exception as Fe:
            pass

    allimageresultsnew = []
    for a, b, c, d in allimageresults:
        allimageresultsnew.append(
            a.to_frame()
            .T.assign(
                aa_string_explanation=b,
                aa_cutimage=[c.copy()],
                aa_numpysize=c.shape[0] * c.shape[1],
                aa_fullimage=[d.copy()],
            )
            .copy()
        )
    dfbibi = pd.concat(allimageresultsnew).copy().reset_index(drop=True)
    allwrittenfiles = []
    for key, item in dfbibi.iterrows():
        fullim = os.path.join(saveinfoldercomplete, f"{key}.png")
        eleimim = os.path.join(saveinfoldercut, f"{key}.png")
        eleimimxlsx = os.path.join(saveinfoldercut, f"{key}.xlsx")

        save_cv_image(fullim, item.aa_fullimage)
        save_cv_image(eleimim, item.aa_cutimage)
        item.to_frame().T[
            [
                x
                for x in dfbibi.columns
                if str(x) not in ["aa_fullimage", "aa_cutimage"]
                and (regex.search("^aa_", str(x)) or regex.search("^frame$", str(x)))
            ]
        ].to_excel(eleimimxlsx)
        print(fullim, eleimim, end="\r")
        allwrittenfiles.append((fullim, eleimim))
    return allwrittenfiles
