from abc import ABCMeta, abstractmethod
from collections import Iterable
from os import path as opath

import cv2
import numpy as np

_dir = 'inst/scene/img'


class FeatureRule:
    """
    場景特徵
    """
    # shared resources
    _res = dict()

    def __init__(self, filename: str, threshold: float = 0.8, debug: bool = False):
        self._file_name = filename
        self._threshold = threshold
        self._loc_last_result: tuple = None
        self._debug = debug
        if filename not in FeatureRule._res:
            file_path = opath.join(_dir, filename)
            file_path = opath.abspath(file_path)
            img = cv2.imread(file_path)
            FeatureRule._res[filename] = img

    def get_loc_1st(self, img) -> tuple:
        """取得符合特徵的位置(第 1 個點), 沒符合則回傳 None

        Arguments:
            img {array or image} -- 來源圖(screen)

        Returns:
            tuple[int, int]
        """
        screen_image: Iterable
        if isinstance(img, Iterable):
            screen_image = img
        else:
            screen_image = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
        find_image = self.image

        result = cv2.matchTemplate(
            screen_image, find_image, cv2.TM_CCOEFF_NORMED)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if self._debug:
            print('max_val', max_val, 'max_loc', max_loc)
        if max_val >= self._threshold and len(max_loc) > 0:
            self._loc_last_result = max_loc
            return max_loc
        else:
            return None

    def get_loc_center(self, img) -> tuple:
        """取得符合特徵的位置(中心點), 沒符合則回傳 None

        Arguments:
            img {array or image} -- 來源圖(screen)

        Returns:
            tuple[int, int]
        """
        loc = self.get_loc_1st(img)
        loc_center = None

        if loc and len(self.image) > 0:
            height, width, channels = self.image.shape
            loc_center = (loc[0] + width // 2, loc[1] + height // 2)

        self._loc_last_result = loc_center
        return loc_center

    def match(self, img) -> bool:
        """符合特徵

        Arguments:
            img {array or image} -- 來源圖(screen)

        Returns:
            bool
        """
        loc = self.get_loc_center(img)
        self._loc_last_result = loc
        if loc:
            return True
        else:
            return False

    @property
    def file_name(self):
        return self._file_name

    @property
    def image(self) -> np.ndarray:
        """特徵圖

        Returns:
            numpy.ndarray
        """
        return FeatureRule._res[self._file_name]

    @property
    def loc_last_result(self) -> tuple:
        return self._loc_last_result


class SceneBase(metaclass=ABCMeta):
    @abstractmethod
    def feature_rules(self) -> [FeatureRule]:
        return NotImplemented

    def fetch_scene_paths(self, cls: 'SceneBase') -> [FeatureRule]:
        """定義要至目標場景可走的路徑

        Arguments:
            cls {SceneBase} -- 目標場景

        Returns:
            [FeatureRule] -- 路徑特徵
        """
        return
        yield

    @classmethod
    def all_subclasses(cls):
        subclasses: [SceneBase] = []
        for c in cls.__subclasses__():
            c_subclasses = c.all_subclasses()
            if len(c_subclasses) == 0:
                subclasses.append(c)
            else:
                subclasses.extend(c_subclasses)
        return subclasses
