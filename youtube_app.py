from moviepy.editor import VideoFileClip,AudioFileClip
from pytubefix import YouTube
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


    def download_(self,itag_,path_):
        # burda itag_ değeri youtube her dosyayı itag numarası ile tanımlar
        # giridğimiz itag hangi dosyanın (ses,video) indirileceğini belirler
        self.stream = self.youtube_.streams.get_by_itag(itag_)
        self.stream.download(output_path=path_)

        
    def audio_video_join(self):
        # indirme işlemi sonrasında kullanıcı mp4(video) seçeneğini seçti ise
        # ses ve video (webm formatındaki) dosyalarının birleştirilme işlemi ↓
        try:
            # ses ve video dosyalarının adresi alınır path bilgisi alınır
            self.video_file_path = f"{os.getcwd()}\\Video\\{os.listdir("Video")[0]}"
            self.audio_file_path = f"{os.getcwd()}\\Audio\\{os.listdir("Audio")[0]}"
            self.output_filename = "".join(os.listdir("Video")[0].split(".")[0:-1:1])+".mp4"

            # dosya okuma işlemi işlemi sonrası video dosyasını ses dosyası ile birleştirip kayıt ediyoruz
            self.video_clip = VideoFileClip(self.video_file_path)
            self.audio_clip = AudioFileClip(self.audio_file_path)
        
            self.final_clip = self.video_clip.set_audio(self.audio_clip)
            self.final_clip.write_videofile(
                self.output_filename,        # dosya kayıt adresi
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


    def audio_to_mp3(self):
        # indirilmek istenilen dosya ses(mp3) ise bunu webm formatından mp3 formatına çevirip kayıt ediyoruz 
        self.audio_file_path = f"{os.getcwd()}\\Audio\\{os.listdir("Audio")[0]}"
        self.audio_clip = AudioFileClip(self.audio_file_path)
        self.audio_clip.write_audiofile(F"{self.youtube_.title}.mp3")
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
        # video url giriş alanı oluşturuluyor ve girilen değer bir youtube adresi ise 
        # bir youtube objesi oluşturulup kullanıcıya indirme seçenekleri sunuluyor
        Url = st.text_input("Video Adresini Giriniz ↓")
        if self.is_youtube_url(Url):
            self.youtube_object(Url)
            self.download_options()
            st.video(Url)
        
        # girilen değer bir youtube adresi değil ise kullanıcıya uyarı gösteriliyor
        elif Url and (not self.is_youtube_url(Url)):
            st.markdown('<p style="color:red;">girilen adres bir youtube linki değil!!</p>', unsafe_allow_html=True)


    def audio_options(self):
        self.audio_choice = st.selectbox("Ses Kalite Ayarı",
                                         self.audio_quality_options().keys())
        return self.audio_choice


    def video_options(self):
        self.video_choice = st.selectbox("Video Kalite Ayarı",
                                         self.video_quality_options().keys())
        return self.video_choice


    def download_options(self): 
            """indirilecek dosya türünün,kalite ayarlarının ve dosyanın indirileceği dizinin seçimi"""

            self.selection = st.selectbox("Dosya İndirme Seçenekleri", ('mp4(video)', 'mp3(ses)'))

            if self.selection == "mp4(video)":
                self.video_options()
                self.audio_options()
                
                self.video_itag_choice = self.stream_video_options.get(self.video_choice)
                self.audio_itag_choice = self.stream_audio_options.get(self.audio_choice)
                downloadButton = st.button('indir', type='secondary', icon=":material/download:")
                
                if downloadButton:
                    self.download_(self.video_itag_choice,F"{os.getcwd()}/Video")
                    self.download_(self.audio_itag_choice,F"{os.getcwd()}/Audio")

                    self.audio_video_join()
            
            elif self.selection == "mp3(ses)":
                self.audio_options()
                self.audio_itag_choice = self.stream_audio_options.get(self.audio_choice)
                downloadButton = st.button('indir', type='secondary', icon=":material/download:")
                    
                if downloadButton:
                    self.download_(self.audio_itag_choice, F"{os.getcwd()}/Audio")
                    self.audio_to_mp3()
                    
                
uygulama = Application()
uygulama.url_input()