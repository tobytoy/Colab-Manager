import cv2
import time
import json
import pickle
import numpy as np
import tensorflow as tf
import configparser
import subprocess
from pathlib import Path
from PIL import Image
from jsonschema import validate
from jsonschema.exceptions import SchemaError, ValidationError
from manager import tools
import hashlib
from Cryptodome.Cipher import AES
from base64 import b64encode, b64decode

config = configparser.ConfigParser()
config.read("manager/config/config.ini")

json_schema = {
    "description": "JSON Schema for labeler",
    "type": "object",
    "required": ["version", "label", "duration", "focusOnHumanKeypoint"],
    "properties": {
        "version": {
            "enum": ["v1.2.1"]
        },
        "label": {
            "enum": [[]]
        },
        "duration": {
            "type": "integer"
        },
        "focusOnHumanKeypoint": {
            "type": "array",
            "items": {
                "type": "object",
                "oneOf": [
                    {
                        "required": ["part", "type", "method", "k_index", "k_1", "k_2", "threshold", "move_type", "checkPoints"],
                        "properties": {
                            "part": {
                                "enum": ["left_arm", "right_arm", "left_leg", "right_leg"]
                            },
                            "type": {
                                "enum": ["angle", "vector"]
                            },
                            "method": {
                                "enum": [12, 23, 13, 123]
                            },
                            "k_index": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 16
                            },
                            "k_1": {
                                "enum": [0]
                            },
                            "k_2": {
                                "enum": [1]
                            },
                            "threshold": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1
                            },
                            "move_type": {
                                "enum": ["hold", "around"]
                            },
                            "checkPoints": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["label_index", "d"],
                                    "properties": {
                                        "label_index": {
                                            "type": "integer",
                                            "minimum": 0,
                                        },
                                        "d": {
                                            "type": "number",
                                            "minimum": 0,
                                            "maximum": 2
                                        }
                                    }

                                }
                            }

                        }
                    },
                    {
                        "required": ["part", "type", "method", "k_index", "k_1", "k_2", "threshold", "move_type", "checkPoints"],
                        "properties": {
                            "part": {
                                "enum": ["body"]
                            },
                            "type": {
                                "enum": ["angle", "vector"]
                            },
                            "method": {
                                "enum": [13, 31, 24, 42]
                            },
                            "k_index": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 16
                            },
                            "k_1": {
                                "enum": [0]
                            },
                            "k_2": {
                                "enum": [1]
                            },
                            "threshold": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1
                            },
                            "move_type": {
                                "enum": ["hold", "around"]
                            },
                            "checkPoints": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["label_index", "d"],
                                    "properties": {
                                        "label_index": {
                                            "type": "integer",
                                            "minimum": 0,
                                        },
                                        "d": {
                                            "type": "number",
                                            "minimum": 0,
                                            "maximum": 2
                                        }
                                    }

                                }
                            }

                        }
                    },
                    {
                        "required": ["part", "type", "method", "k_index", "k_1", "k_2", "threshold", "move_type", "checkPoints"],
                        "properties": {
                            "part": {
                                "enum": ["left_arm", "right_arm", "left_leg", "right_leg", "body"]
                            },
                            "type": {
                                "enum": ["slope"]
                            },
                            "method": {
                                "type": "integer",
                            },
                            "k_index": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 16
                            },
                            "k_1": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 16
                            },
                            "k_2": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 16
                            },
                            "threshold": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1
                            },
                            "move_type": {
                                "enum": ["hold", "around"]
                            },
                            "checkPoints": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["label_index", "d"],
                                    "properties": {
                                        "label_index": {
                                            "type": "integer",
                                            "minimum": 0,
                                        },
                                        "d": {
                                            "type": "number",
                                            "minimum": 0,
                                            "maximum": 2
                                        }
                                    }

                                }
                            }

                        }
                    },
                ]
            }
        }
    }
}


def focusOnHumanKeypoint_check(item):
    if item["type"] == "slpoe":
        item["part"] = "body"
        item["method"] = 11
        item["k_index"] = 0
    else:
        # item["type"] = vector or angle
        if item["part"] == "body":
            if item["method"] == 13:
                item["k_index"] = 11
            elif item["method"] == 31:
                item["k_index"] = 5
            elif item["method"] == 24:
                item["k_index"] = 12
            elif item["method"] == 42:
                item["k_index"] = 6
        else:
            # item["part"] = nonbody part
            if item["part"] == "left_arm":
                if item["method"] == 12:
                    item["k_index"] = 7
                elif item["method"] == 13:
                    item["k_index"] = 9
                elif item["method"] == 23:
                    item["k_index"] = 9
                elif item["method"] == 123:
                    item["k_index"] = 9
            elif item["part"] == "right_arm":
                if item["method"] == 12:
                    item["k_index"] = 8
                elif item["method"] == 13:
                    item["k_index"] = 10
                elif item["method"] == 23:
                    item["k_index"] = 10
                elif item["method"] == 123:
                    item["k_index"] = 10
            elif item["part"] == "left_leg":
                if item["method"] == 12:
                    item["k_index"] = 13
                elif item["method"] == 13:
                    item["k_index"] = 15
                elif item["method"] == 23:
                    item["k_index"] = 15
                elif item["method"] == 123:
                    item["k_index"] = 15
            elif item["part"] == "right_leg":
                if item["method"] == 12:
                    item["k_index"] = 14
                elif item["method"] == 13:
                    item["k_index"] = 16
                elif item["method"] == 23:
                    item["k_index"] = 16
                elif item["method"] == 123:
                    item["k_index"] = 16


class Cipher():
    def __init__(self, acc: str, pa: str) -> None:
        acc_n = sum([ord(_) for _ in acc])
        s_p_s = "".join([chr(i) for i in range(33, 127)])
        p_n = acc_n % (32 - len(pa))
        self._u8 = (pa[:32] if len(pa) >= 32 else acc[acc_n % len(
            acc)] * p_n + pa + s_p_s[acc_n % len(s_p_s)] * (32 - len(pa) - p_n)).encode('utf-8')

    def decrypt(self, eb: str, tb: str, nb: str) -> list[str]:
        e, t, n = map(lambda x: b64decode(x), [eb, tb, nb])
        return AES.new(self._u8, AES.MODE_EAX, nonce=n).decrypt_and_verify(e, t).decode('utf-8')

    def check(self, check_data: dict) -> bool:
        try:
            _flag = float(self.decrypt(*check_data['check']).split(
                '-')[1]) < time.time() if 'check' in check_data.keys() else False
            return _flag
        except Exception as err:
            if str(err) == 'MAC check failed':
                print('你帳號或密碼有問題')
            else:
                print(f"Unexpected {err=}, {type(err)=}")
            return False


class Fairy:
    def __init__(self, video_name='Kettlebells-Emily'):
        # deal with models
        self.model_path = Path(config["PATH"]["model_path"])
        self.model_url = config["URL"]["model_url"]
        self.model_download_path = Path(config["PATH"]["model_download_path"])
        if self.model_path.exists() == False:
            subprocess.check_output(["wget", self.model_url, "-O", str(self.model_download_path)],
                                    stderr=subprocess.STDOUT)
            subprocess.check_output(["mkdir", str(self.model_path)],
                                    stderr=subprocess.STDOUT)
            subprocess.check_output(["tar", "-C", str(self.model_path), "-zxvf", str(self.model_download_path)],
                                    stderr=subprocess.STDOUT)

        # default path
        self.video_root_path = Path(config["PATH"]["video_root_path"])
        if self.video_root_path.exists() == False:
            subprocess.check_output(["mkdir", self.video_root_path],
                                    stderr=subprocess.STDOUT)

        self.video_output_root_path = Path(
            config["PATH"]["video_output_root_path"])
        if self.video_output_root_path.exists() == False:
            subprocess.check_output(["mkdir", self.video_output_root_path],
                                    stderr=subprocess.STDOUT)

        self.data_output_root_path = Path(
            config["PATH"]["data_output_root_path"])
        if self.data_output_root_path.exists() == False:
            subprocess.check_output(["mkdir", self.data_output_root_path],
                                    stderr=subprocess.STDOUT)

        self.temp_root_path = Path(config["PATH"]["temp_root_path"])
        if self.temp_root_path.exists() == False:
            subprocess.check_output(["mkdir", self.temp_root_path],
                                    stderr=subprocess.STDOUT)

        # deal with account and password
        with open(config["PATH"]["config_pickle_path"], 'rb') as f:
            self.data_config = pickle.load(f)

        # deal with videos
        self.video_path = self.video_root_path / (video_name + ".mp4")

        if self.video_path.exists() == False and len(list(self.video_root_path.glob('*.mp4'))) > 0:
            self.video_path = list(self.video_root_path.glob('*.mp4'))[0]

        print(
            f"video path : {self.video_path}, model path : {self.model_path}")

    def set_video(self, video_name='Kettlebells-Emily'):
        # deal with videos
        self.video_path = self.video_root_path / (video_name + ".mp4")

        if self.video_path.exists() == False and len(list(self.video_root_path.glob('*.mp4'))) > 0:
            self.video_path = list(self.video_root_path.glob('*.mp4'))[0]

        print(
            f"video path : {self.video_path}, model path : {self.model_path}")

    def model_inference_video(self):
        self.model = tf.saved_model.load(self.model_path)
        self.movenet = self.model.signatures['serving_default']
        self.video_target_path = config["PATH"]["video_target_path"]
        cap = cv2.VideoCapture(self.video_target_path)
        count = 0
        self.body_keypoint_list = []
        start = time.time()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            height, width, _ = frame.shape
            x = 0
            y = 0
            w = height
            h = height
            crop_img = frame[y:y+h, x:x+w]
            image_rgb = cv2.cvtColor(crop_img, cv2.COLOR_BGR2RGB)
            width = height
            image_resize = cv2.resize(
                image_rgb, (256, 256), interpolation=cv2.INTER_AREA)
            image_r0 = tf.expand_dims(image_resize, axis=0)
            input_image = tf.cast(image_r0, dtype=tf.int32)
            outputs = self.movenet(input_image)
            body_keypoint = outputs['output_0'][0][0]
            self.body_keypoint_list.append(body_keypoint)
            if count % 100 == 0 and count > 0:
                end = time.time()
                print('Count: ', count, ' Inference Average Time: ', (end-start)/100)
                start = time.time()

            count += 1

        fps = cap.get(cv2.CAP_PROP_FPS)

        frame_size = (height, width)
        print(f"frame size : {frame_size}")
        cap.release()
        print(f"Model Inference Done with count : {count}")

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(
            config["PATH"]["output_inference_path"], fourcc, fps, frame_size)
        cap = cv2.VideoCapture(self.video_target_path)
        count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            height, width, _ = frame.shape

            if count == 10:
                print(f"frame shape : {frame.shape}")

            body_keypoint = self.body_keypoint_list[count]
            for keypoint in body_keypoint:
                y_coordinate = int(keypoint[0] * height)
                x_coordinate = int(keypoint[1] * width)
                score = keypoint[2]
                if score > 0.8:
                    cv2.circle(frame, (x_coordinate, y_coordinate),
                               1, (255, 0, 0), 5)
                elif score > 0.4:
                    cv2.circle(frame, (x_coordinate, y_coordinate),
                               1, (255, 255, 0), 5)
                else:
                    cv2.circle(frame, (x_coordinate, y_coordinate),
                               1, (0, 0, 255), 5)

            cv2.putText(frame, str(count), (30, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
            out.write(frame)

            if count % 100 == 0:
                print(f"Count : {count} Saving Video.")
            count += 1

        cap.release()
        out.release()

        print('Video Save Done!')
        self.pickle_path = Path(config["PATH"]["pickle_output_path"])
        with open(self.pickle_path, 'wb') as f:
            pickle.dump(self.body_keypoint_list, f)

    def modify_pickle(self,
                      frame_index=10,
                      body_index=10,
                      x_rate=0.5,
                      y_rate=0.5,
                      save_pickle_check=False):
        with open(self.pickle_path, 'rb') as f:
            body_keypoint_list = pickle.load(f)

        self.target_video_path = config["PATH"]["video_target_path"]
        cap = cv2.VideoCapture(self.target_video_path)
        count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Cannot receive frame")
                break
            if count == frame_index:
                break
            count += 1

        cap.release()

        height, width, _ = frame.shape
        for index, keypoint in enumerate(body_keypoint_list[frame_index]):
            y_coordinate = int(keypoint[0] * height)
            x_coordinate = int(keypoint[1] * width)
            score = keypoint[2]
            _l = 7 if index == body_index else 3
            if score > 0.8:
                cv2.circle(frame, (x_coordinate, y_coordinate),
                           1, (255, 0, 0), _l)
            elif score > 0.4:
                cv2.circle(frame, (x_coordinate, y_coordinate),
                           1, (255, 255, 0), _l)
            else:
                cv2.circle(frame, (x_coordinate, y_coordinate),
                           1, (0, 0, 255), _l)

        y_coordinate = int(y_rate * height)
        x_coordinate = int(x_rate * width)
        cv2.circle(frame, (x_coordinate, y_coordinate), 1, (255, 0, 255), 5)

        if save_pickle_check:
            _var = tf.Variable(body_keypoint_list[frame_index])
            _var[body_index, 0].assign(y_rate)
            _var[body_index, 1].assign(x_rate)
            body_keypoint_list[frame_index] = tf.convert_to_tensor(_var)

            with open(self.pickle_path, 'wb') as f:
                pickle.dump(body_keypoint_list, f)

        return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    def json_scheme_check(self, sample_json):
        try:
            validate(instance=sample_json, schema=json_schema)
        except SchemaError as e:
            print("Schema Error :")
            print("\tPath : ")
            print(e.path)
            print("\tHint : ")
            print(e.message)
        except ValidationError as e:
            print("Validation Error :")
            print("\tPath : ")
            print(e.path)
            print("\tHint : ")
            print(e.message)
        else:
            print("Pass Schema Modify your json.")

            for element in sample_json["focusOnHumanKeypoint"]:
                focusOnHumanKeypoint_check(element)

            print("Done")

    def write_json_file(self, sample_json):
        self.pickle_path = Path(config["PATH"]["pickle_output_path"])
        with open(self.pickle_path, 'rb') as f:
            coach_keypoint_list = pickle.load(f)

        for coach_keypoint in coach_keypoint_list:
            _ = tools.changeWholeBodyAngleLengthVectorDictionary(
                coach_keypoint.numpy())
            _['keypoints'] = _['keypoints'].tolist()
            sample_json["label"].append(_)

        self.json_path = Path(config["PATH"]["json_output_path"])
        with open(self.json_path, 'w') as f:
            json.dump(sample_json, f, indent=4)

    def simplify_json_file(self, json_path='datas_output/labels.json'):
        with open(json_path, 'r') as f:
            data = json.load(f)

        label_index_list = []

        for human_keypoint_label in data["focusOnHumanKeypoint"]:
            check_points = human_keypoint_label['checkPoints']
            for check_point in check_points:
                label_index_list.append(check_point['label_index'])

        label_index_list = sorted(list(set(label_index_list)))
        def label_inverse_map(x): return label_index_list.index(x)

        target_label = [data['label'][_] for _ in label_index_list]

        data["label"] = target_label

        for human_keypoint_label in data["focusOnHumanKeypoint"]:
            check_points = human_keypoint_label['checkPoints']
            for check_point in check_points:
                check_point['label_index'] = label_inverse_map(
                    check_point['label_index'])

        self.json_simple_path = Path(config["PATH"]["json_simple_output_path"])
        with open(self.json_simple_path, 'w') as f:
            json.dump(data, f)

    def hash_function(self, json_path='datas_output/labels.json', remove_version_check=True):
        with open(json_path, 'r') as f:
            data = json.load(f)

        if remove_version_check:
            del data["version"]

        md5 = hashlib.md5()
        md5.update(str(data).encode("utf-8"))
        hash = md5.hexdigest()

        print('Hash : ', hash)
