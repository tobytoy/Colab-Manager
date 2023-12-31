import os
import cv2
import time
import json
import pickle
import github
import atexit
import shutil
import zipfile
import tempfile
import requests
import configparser
import subprocess
import hashlib
from PIL import Image
import numpy as np
import tensorflow as tf
from pathlib import Path
from jsonschema import validate
from jsonschema.exceptions import SchemaError, ValidationError
from manager import tools
from Cryptodome.Cipher import AES
from base64 import b64encode, b64decode
from threading import Timer


config = configparser.ConfigParser()
config.read("manager/config/config.ini")

json_schema = {
    "description": "JSON Schema for labeler",
    "type": "object",
    "required": ["version", "label", "duration", "rateMethod", "notholdPunish", "focusOnHumanKeypoint"],
    "properties": {
        "version": {
            "enum": ["v1.3.1"]
        },
        "label": {
            "enum": [[]]
        },
        "duration": {
            "type": "integer"
        },
        "rateMethod": {
            "enum": ["real", "real_1_0_0", "one"]
        },
        "notholdPunish": {
            "type": "number",
            "minimum": 0,
        },
        "focusOnHumanKeypoint": {
            "type": "array",
            "items": {
                "type": "object",
                "oneOf": [
                    {
                        "required": ["part", "type", "method", "kIndex", "k1", "k2", "threshold", "moveType", "indexRange", "checkPoints"],
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
                            "kIndex": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 16
                            },
                            "k1": {
                                "enum": [0]
                            },
                            "k2": {
                                "enum": [1]
                            },
                            "threshold": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1
                            },
                            "moveType": {
                                "enum": ["hold", "around"]
                            },
                            "indexRange": {
                                "type": "integer",
                                "minimum": 1,
                            },
                            "checkPoints": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["labelIndex", "d"],
                                    "properties": {
                                        "labelIndex": {
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
                        "required": ["part", "type", "method", "kIndex", "k1", "k2", "threshold", "moveType", "indexRange", "checkPoints"],
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
                            "kIndex": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 16
                            },
                            "k1": {
                                "enum": [0]
                            },
                            "k2": {
                                "enum": [1]
                            },
                            "threshold": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1
                            },
                            "moveType": {
                                "enum": ["hold", "around"]
                            },
                            "indexRange": {
                                "type": "integer",
                                "minimum": 1,
                            },
                            "checkPoints": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["labelIndex", "d"],
                                    "properties": {
                                        "labelIndex": {
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
                        "required": ["part", "type", "method", "kIndex", "k1", "k2", "threshold", "moveType", "indexRange", "checkPoints"],
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
                            "kIndex": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 16
                            },
                            "k1": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 16
                            },
                            "k2": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 16
                            },
                            "threshold": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1
                            },
                            "moveType": {
                                "enum": ["hold", "around"]
                            },
                            "indexRange": {
                                "type": "integer",
                                "minimum": 1,
                            },
                            "checkPoints": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["labelIndex", "d"],
                                    "properties": {
                                        "labelIndex": {
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
                        "required": ["part", "type", "method", "kIndex", "k1", "k2", "k3", "k4", "threshold", "moveType", "checkPoints"],
                        "properties": {
                            "part": {
                                "enum": ["x", "y", "xy", "yx"]
                            },
                            "type": {
                                "enum": ["keypoints"]
                            },
                            "method": {
                                "type": "integer",
                            },
                            "kIndex": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 16
                            },
                            "k1": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 16
                            },
                            "k2": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 16
                            },
                            "k3": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 16
                            },
                            "k4": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 16
                            },
                            "threshold": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1
                            },
                            "moveType": {
                                "enum": ["hold"]
                            },
                            "checkPoints": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["d"],
                                    "properties": {
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
                        "required": ["part", "type", "method", "kIndex", "k1", "k2", "threshold", "moveType", "indexRange", "checkPoints"],
                        "properties": {
                            "part": {
                                "enum": ["left_arm", "right_arm", "left_leg", "right_leg", "body"]
                            },
                            "type": {
                                "enum": ["angle", "vector"]
                            },
                            "method": {
                                "enum": [0]
                            },
                            "kIndex": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 16
                            },
                            "k1": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 16
                            },
                            "k2": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 16
                            },
                            "threshold": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1
                            },
                            "moveType": {
                                "enum": ["hold", "around"]
                            },
                            "indexRange": {
                                "type": "integer",
                                "minimum": 1,
                            },
                            "checkPoints": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["labelIndex", "d"],
                                    "properties": {
                                        "labelIndex": {
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
    def __init__(self) -> None:
        self._flag = False

    def u8(self, acc: str, pa: str) -> None:
        if len(acc) > 0 and len(pa) > 0:
            acc_n = sum([ord(_) for _ in acc])
            s_p_s = "".join([chr(i) for i in range(33, 127)])
            p_n = acc_n % (32 - len(pa))
            self._u8 = (pa[:32] if len(pa) >= 32 else acc[acc_n % len(
                acc)] * p_n + pa + s_p_s[acc_n % len(s_p_s)] * (32 - len(pa) - p_n)).encode('utf-8')
        else:
            self._u8 = ("u8"*16).encode('utf-8')

    def decrypt(self, eb: str, tb: str, nb: str) -> list[str]:
        e, t, n = map(lambda x: b64decode(x), [eb, tb, nb])
        return AES.new(self._u8, AES.MODE_EAX, nonce=n).decrypt_and_verify(e, t).decode('utf-8')

    def check(self, check_data: dict) -> bool:
        try:
            self._flag = float(self.decrypt(*check_data['check']).split(
                '-')[1]) < time.time() if 'check' in check_data.keys() else False
            return self._flag
        except Exception as err:
            if str(err) == 'MAC check failed':
                print('你帳號或密碼有問題')
            else:
                print(f"Unexpected {err=}, {type(err)=}")
            return False


class WebMaster:
    def __init__(self, cipher, user, check_list, check_dict):
        self.cipher = cipher
        self.user = user
        self.check_list = check_list
        self.check_dict = check_dict
        self.git_init(self.check_list, [1, 2])

    def git_init(self, check_list, indexs):
        cipher_list = list(
            map(lambda x: self.cipher.decrypt(*self.check_dict[x]), check_list))
        self.g_obj = (lambda x: github.Github(
            auth=github.Auth.Token(x)))(cipher_list[indexs[0]])
        self.g_repo = self.g_obj.get_repo(cipher_list[indexs[1]])

    def git_check(self, check_list, index):
        cipher_list = list(
            map(lambda x: self.cipher.decrypt(*self.check_dict[x]), check_list))
        try:
            self.g_repo.get_contents(cipher_list[index])
            return True, cipher_list[index]
        except Exception as err:
            if err.data['message'] == 'Not Found':
                return False, None
            else:
                print(f"Unexpected {err=}, {type(err)=}")
                return False, None

    def git_get_contents(self, check_list, index):
        _check = self.git_check(check_list, index)
        if _check[0]:
            return self.g_repo.get_contents(_check[1]).decoded_content.decode()

    def git_create_update_contents(self, check_list, index, contents):
        _check = self.git_check(check_list=check_list, index=index)
        repo = self.g_repo
        if _check[0]:
            repo.update_file(_check[1], "update message", contents, repo.get_contents(
                _check[1]).sha, branch="main")
        else:
            repo.create_file(_check[1], "init message",
                             contents, branch="main")

    def start_ngrok(self):
        ngrok_address = self._run_ngrok()
        if self.user == 'master':
            cipher_list = list(
                map(lambda x: self.cipher.decrypt(*self.check_dict[x]), ['ngrok_t']))
        else:
            cipher_list = list(
                map(lambda x: self.cipher.decrypt(*self.check_dict[x]), ['ngrok']))
        subprocess.check_output(
            ['ngrok', 'authtoken', cipher_list[0]], stderr=subprocess.STDOUT)
        time.sleep(1)
        message = eval(self.git_get_contents(['cont_p'], 0))
        message['colab']['ngrok'] = ngrok_address.split('.', 1)[
            0].split('://')[1]
        self.git_create_update_contents(['cont_p'], 0, json.dumps(message))
        print(f" * Running on {ngrok_address}")
        print(f" * Traffic stats available on http://127.0.0.1:4040")

    def _download_ngrok(self, ngrok_path):
        if Path(ngrok_path).exists():
            return
        url = "https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip"
        with zipfile.ZipFile(self._download_file(url), "r") as zip_ref:
            zip_ref.extractall(ngrok_path)

    def _download_file(self, url):
        local_filename = url.split('/')[-1]
        r = requests.get(url, stream=True)
        download_path = str(Path(tempfile.gettempdir(), local_filename))
        with open(download_path, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
        return download_path

    def _run_ngrok(self):
        ngrok_path = str(Path(tempfile.gettempdir(), "ngrok"))
        self._download_ngrok(ngrok_path)
        executable = str(Path(ngrok_path, "ngrok"))
        os.chmod(executable, 777)
        ngrok = subprocess.Popen([executable, 'http', '5000'])
        atexit.register(ngrok.terminate)
        localhost_url = "http://localhost:4040/api/tunnels"  # Url with tunnel details
        time.sleep(1)
        return json.loads(requests.get(localhost_url).text)['tunnels'][0]['public_url'].replace("https", "http")

    def run_with_ngrok(self, app):
        old_run = app.run

        def new_run():
            thread = Timer(1, self.start_ngrok)
            thread.setDaemon(True)
            thread.start()
            old_run()
        app.run = new_run


class Fairy:
    def __init__(self, video_name='Kettlebells-Emily'):
        # deal with models
        self.model_path = Path(config["PATH"]["model_path"])
        self.model_url = config["URL"]["model_url"]
        self.demo_video_url = config["URL"]["demo_video_url"]

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

        self.data_root_path = Path(config["PATH"]["data_root_path"])
        if self.data_root_path.exists() == False:
            subprocess.check_output(["mkdir", self.data_root_path],
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
        size = os.path.getsize(json_path)

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

        size_simple = os.path.getsize(self.json_simple_path)
        print(f"壓縮率 {round(size_simple/size*100, 2)} %")
        


    def hash_function(self, json_path='datas_output/labels.json', remove_version_check=True):
        with open(json_path, 'r') as f:
            data = json.load(f)

        if remove_version_check:
            del data["version"]

        md5 = hashlib.md5()
        md5.update(str(data).encode("utf-8"))
        hash = md5.hexdigest()

        print('Hash : ', hash)
