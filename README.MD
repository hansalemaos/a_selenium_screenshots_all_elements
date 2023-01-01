# Takes a screenshot of every element on a site

```python
# Tested with:
# https://github.com/ultrafunkamsterdam/undetected-chromedriver
# Python 3.9.13
# Windows 10


$pip install a-selenium-screenshots-all-elements

from auto_download_undetected_chromedriver import download_undetected_chromedriver
import undetected_chromedriver as uc
from a_selenium_screenshots_all_elements import get_screenshots_from_all_elements
if __name__ == "__main__":
    folderchromedriver = "f:\\seleniumdriver3"
    path = download_undetected_chromedriver(
        folder_path_for_exe=folderchromedriver, undetected=True
    )
    driver = uc.Chrome(driver_executable_path=path)
    driver.get(r"https://github.com/hansalemaos/a_cv2_easy_resize")

    get_screenshots_from_all_elements(driver, saveinfolder='f:\\testscreensht', cutinfos=80) # cutinfos = max letters in one line

    
```


<img src="https://github.com/hansalemaos/screenshots/raw/main/2023-01-01%2009_48_27-single_elements.png"/>

<img src="https://github.com/hansalemaos/screenshots/raw/main/144.png"/>

<img src="https://github.com/hansalemaos/screenshots/raw/main/146.png"/>




