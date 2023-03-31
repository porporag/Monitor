import numpy as np
import cv2
import pyautogui
import time
import os
import wave
import threading
import tkinter as tk
import pyaudio
import ffmpeg

class Recorder:
    def __init__(self):
        self.font = ("Arial",30,"bold")
        self.index_name = 0
        self.root = tk.Tk()
        # self.root.geometry("300x150")
        self.root.resizable(False,False)
        self.root.title('Monitor')
        self.button = tk.Button(text = "🎙",font = self.font,
                                command = self.click_handler_audio)
        self.button.grid(column=0,row=0)
        self.button_video = tk.Button(text = "⏺", font = self.font,
                                command = self.click_handler_video)
        self.button_video.grid(column=1,row=0,sticky = tk.E)
        self.label = tk.Label(text="00:00:00")
        self.label.grid(column =0,row = 1,columnspan = 2, sticky = tk.W+tk.E)
        self.recording = False
        self.recording_audio = False
        self.root.mainloop()

    def click_handler_audio(self):
        if self.recording_audio:
            self.recording_audio = False
            self.button.config(fg="black")
        
        else:
            self.recording_audio = True
            self.button.config(fg='red')
    
    def click_handler_video(self):
        if self.recording:
            self.recording = False
            self.button_video.config(fg="black")
            time.sleep(0.1)
            self.merge()
        
        else:
            self.recording = True
            self.button_video.config(fg='red')
            threading.Thread(target = self.record_video).start()
            threading.Thread(target = self.record_audio).start()
            
    def record_video(self):
        SCREEN_SIZE = (1920,1080)

        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        exists_video = True

        while exists_video:
            if os.path.exists(f"video_recording{self.index_name}.avi"):
                self.index_name +=1
            else:
                exists_video = False
        
        start = time.time()
        frames_list = []

        while self.recording:
            elapsed = time.time() - start
            
            secs = elapsed % 60
            mins = elapsed // 60
            hours = mins // 60
            self.label.config(text=f"{int(hours):02d}:{int(mins):02d}:{int(secs):02d}")
            
            img = pyautogui.screenshot()

            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            frames_list.append(frame)
        duration = time.time()-start
        frame_count = len(frames_list) + 1

        actualFps_avg = np.ceil(frame_count/duration)
        video_real_fps = cv2.VideoWriter(f"video_recording{self.index_name}.avi", fourcc, actualFps_avg, (SCREEN_SIZE))
        for i in frames_list:
            video_real_fps.write(i)
        video_real_fps.release()
        cv2.destroyAllWindows()
        return video_real_fps    
    
    def record_audio(self):
        if self.recording_audio:
            frames = []
            audio = pyaudio.PyAudio()
            stream = audio.open(format = pyaudio.paInt16,channels = 1, rate = 44100,
                                input = True, frames_per_buffer=1024)
            
            while self.recording:
                data = stream.read(1024)
                frames.append(data)
            stream.stop_stream()
            stream.close()
            audio.terminate()
            soundfile = wave.open(f"audio_recording{self.index_name}.wav", "wb")
            soundfile.setnchannels(1)
            soundfile.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            soundfile.setframerate(44100)
            soundfile.writeframes(b"".join(frames))
            soundfile.close()
            return audio
    
    def merge(self):
        if os.path.exists(f"audio_recording{self.index_name}.wav"):
            audio = ffmpeg.input(f"audio_recording{self.index_name}.wav")
            video_real_fps = ffmpeg.input(f"video_recording{self.index_name}.avi")

            out,err = ffmpeg.concat(video_real_fps, audio, v=1, a=1).output(f"video_audio_{self.index_name}.mp4").run()

        else:
            None
        
    
if __name__ == "__main__":
    Recorder()