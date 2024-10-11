from moviepy.editor import VideoFileClip,AudioFileClip
from pytubefix import YouTube
from time import time
import streamlit as st
import os
import re

class youtube():
    def __init__(self) -> None:
        try:
            # İndieilecek ses ve görüntü dosyaları için çalışma dizininde klasör oluşturma
            os.mkdir(Fr"{os.getcwd()}\Video")
            os.mkdir(Fr"{os.getcwd()}\Audio")

        # Klasörler daha önce oluşturulmuş ise programın hata vermesi önlenir. ↓
        except FileExistsError:
            pass
        except Exception as err:
            print("Bir hata oluştu!!", err)

    def youtube_object(self,_url):
        # YouTube nesnesi oluşturuyoruz ve bu nesneye indireceğimiz videonun adresini yazıyoruz
        self.youtube_ = YouTube(_url)

    def video_quality_options(self):
        "Video çözünürlük seçeneklerini tespit ediyoruz (webm formatı)"

        # Video akış seçenekleri video itag ile kullanıcıya 
        # listelenmesi için bir sözlük oluşturulur . ↓
        self.stream_video_options = dict()

        # youtube_ nesnesinde webm formatındaki video akışları filitrelenir.
        self.vqo = self.youtube_.streams.filter(mime_type="video/webm")

        # video akış(kalite) seçenekleri görüntü kalitesi ve itag değeri ile
        # stream_video_options isimli sözlüğe kayıt edilir ve değer olarak döndürülür.
        for item in self.vqo:
            self.stream_video_options.update({item.resolution:item.itag})
        else:
            return self.stream_video_options

    def audio_quality_options(self):
        "Ses akış seçeneklerinin tespiti (webm formatı)"

        # Ses akış seçenekleri ses itag ile kullanıcıya 
        # listelenmesi için bir sözlük oluşturulur . ↓
        self.stream_audio_options = dict()

        # youtube_ nesnesinde webm formatındaki ses akışları filtrelenir
        self.aqo = self.youtube_.streams.filter(mime_type="audio/webm")
        
        # Ses akış seçenekleri 'abr' (average bitrate) ve itag değeri ile 
        # stream_audio_options isimli sözlüğe kayıt edilir ve değer olarak döndürülür
        for item in self.aqo:
            self.stream_audio_options.update({item.abr:item.itag})
        else:
            return self.stream_audio_options

    def download(self,itag_,path_):
        self.stream = self.youtube_.streams.get_by_itag(itag_)
        self.stream.download(output_path=path_)

    def audio_video_join(self):
        try:
            self.video_file_path = f"{os.getcwd()}\\Video\\{os.listdir("Video")[0]}"
            self.audio_file_path = f"{os.getcwd()}\\Audio\\{os.listdir("Audio")[0]}"
            self.output_filename = "".join(os.listdir("Video")[0].split(".")[0:-1:1])+".mp4"

            self.video_clip = VideoFileClip(self.video_file_path)
            self.audio_clip = AudioFileClip(self.audio_file_path)
        
            self.final_clip = self.video_clip.set_audio(self.audio_clip)
            self.final_clip.write_videofile(
                self.output_filename,
                codec="libx264",             # MP4 formatı için uygun video codec
                audio_codec="aac",           # MP4 formatı için uygun ses codec
                bitrate="5000k",             # Video bit hızı, daha yüksek değer daha yüksek kalite demektir
                fps=self.video_clip.fps,     # Orijinal videonun kare hızını kullanın
                preset="medium",             # Video kalitesi ve hız dengesi, "ultrafast" ile "veryslow" arasında değişir
                ffmpeg_params=["-crf", "18"]
            )

        except Exception as err:
            print("Bir hata ouştu!!", err)
        else:
            os.remove(self.video_file_path)
            os.remove(self.audio_file_path)

        

class Application(youtube):
    def __init__(self) -> None:
        super().__init__()
        st.title("YouTube Video İndirici")

    
    def is_youtube_url(self,url):
        # YouTube URL'lerini eşleştirmek için regex deseni
        youtube_regex = re.compile(r'^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+$')
        # URL'nin desene uyup uymadığını kontrol et
        return bool(youtube_regex.match(url))

    def url_input(self):
        Url = st.text_input("Video Adresini Giriniz ↓")
        if self.is_youtube_url(Url):
            self.youtube_object(Url)
            self.download_options()         
        elif Url and (not self.is_youtube_url):
            st.markdown('<p style="color:red;">girilen adres bir youtube linki değil!!</p>', unsafe_allow_html=True)


    def audio_options(self): 
        self.audio_choice = st.selectbox("Ses Kalite ayarını seçin:",
                                         self.audio_quality_options().keys())
        return self.audio_choice

    def video_options(self):
        self.video_choice = st.selectbox("Video Kalite Ayarı",
                                         self.video_quality_options().keys())
        return self.video_choice

    def download_options(self): 
            "indirilecek dosya türünün ve kalite ayarlarının seçimi"

            self.selection = st.selectbox("Dosya İndirme Seçenekleri", ('mp4(video)', 'mp3(ses)'))
            if self.selection == "mp4(video)":
                self.video_options()
                self.audio_options()
                
                if self.stream_audio_options.get(self.audio_choice) != None and \
                    self.stream_video_options.get(self.video_choice) != None:
                    
                    self.video_choice = self.stream_video_options.get(self.video_choice)
                    self.audio_choice = self.stream_audio_options.get(self.audio_choice)

                    # self.download(self.video_choice,F"{os.getcwd()}/Video")
                    # self.download(self.audio_choice,F"{os.getcwd()}/Audio")

                    # self.audio_video_join()

            
            elif self.selection == "'mp3(ses)'":
                self.audio_options()
                if self.stream_audio_options.get(self.audio_choice) != None:
                    self.download(self.audio_choice,F"{os.getcwd()}/Audio")
            else:
                print("Yanlış Seçim")

uygulama = Application()
uygulama.url_input()


# st.title("Youtube Video İndirici")
# st_text_url = st.text_input("Video Adresini Giriniz ↓")
# st.markdown('<p style="color:red;">girilen adres bir youtube linki değil!!</p>', unsafe_allow_html=True)
# st_button = st.button("İNDİR" , key="indir")
# secim = st.selectbox("Dosya İndirme Seçenekleri", ('mp4(video)', 'mp3(ses)'))



# yout = YouTube("https://www.youtube.com/watch?v=2OPVViV-GQk")
# st_video = yout.streams.filter(only_video=True)
# print("Video Seçenekleri")
# print(*st_video,sep="\n")

# print("Ses Seçenekleri")
# st_audio = yout.streams.filter(only_audio=True)
# print(*st_audio, sep="\n")

