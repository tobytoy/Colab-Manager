import cv2
import configparser
from PIL import Image
import moviepy as mvp
from manager import colab_tool
from moviepy.editor import VideoFileClip
from matplotlib import pyplot as plt


config = configparser.ConfigParser()
config.read("manager/config/config.ini")

class Video:
    def __init__(self, video_path = "Kettlebells-Emily.mp4", frame_index = 50):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(str(self.video_path))
        if not self.cap.isOpened():
            print("could not open : ", self.video_path)

        self.video_length = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.video_width  = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.video_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.video_fps    = self.cap.get(cv2.CAP_PROP_FPS)

        self.label_indexs = [i for i in range(0, (self.video_length+1), int(self.video_length/10))]
        self.label_frames = []

        print(f"影片寬:{self.video_width}, 影片高:{self.video_height}, 影片長:{self.video_length}, fps:{self.video_fps}")
        
        # get frame by index
        self.frame_index = max(min(frame_index, self.video_length - 1), 0)
        count = 0
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Cannot receive frame")
                break
            if count == self.frame_index:
                self.frame = frame
                
            if count in self.label_indexs:
                self.label_frames.append(frame[:,:,::-1].copy())
            count += 1
        self.cap.release()

    def annotate_square_one(self) -> None:
        self.annotate_boxes = []
        colab_tool.annotate_square_one(self.label_frames, box_storage_pointer=self.annotate_boxes)
        
    def draw_rectangle(self, video_hw = 530, start_x = 350, start_y = 120, reload = False, show = False):
        if reload and len(self.annotate_boxes) > 0:
            one_box = self.annotate_boxes[0][0]
            _y = one_box[0]
            _x = one_box[1]
            _h = one_box[2] - one_box[0]
            _w = one_box[3] - one_box[1]

            self.start_x = int(self.video_width * _x)
            self.start_y = int(self.video_height * _y)
            self.video_hw = int(max(self.video_width * _w, self.video_height * _h))
        else:
            self.start_x  = start_x
            self.start_y  = start_y
            self.video_hw = video_hw

        cv2.rectangle(self.frame,
                (start_x, start_y),
                (start_x+video_hw, start_y+video_hw),
                (0,0,255),
                2,
                cv2.LINE_AA)
        if show:
            plt.figure(figsize=(15,15))
            plt.imshow(self.frame[:,:,::-1])
            plt.show()
            
        return Image.fromarray(cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB))

    def video_cutting(self, flip_flag = False, show = False):
        video_mv = VideoFileClip(str(self.video_path))
        output = mvp.video.fx.all.crop(video_mv,
                                        x1=self.start_x,
                                        y1=self.start_y,
                                        width=self.video_hw,
                                        height=self.video_hw)
        if flip_flag:
            output = mvp.video.fx.all.mirror_x(output)

        video_target_path = config["PATH"]["video_target_path"]
        temp_path = config["PATH"]["temp_root_path"] + "/temp.mp4"
        output.write_videofile(video_target_path, 
                            temp_audiofile = temp_path,
                            remove_temp=True, 
                            codec="libx264", audio_codec="aac")
        # temp_audiofile
        if show:
            clip = VideoFileClip(video_target_path)
            clip.ipython_display(width="60%")

        

