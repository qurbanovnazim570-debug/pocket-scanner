import cv2
import numpy as np
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label


class CameraScanner(BoxLayout):

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.orientation = 'vertical'

    self.img_widget = Image()
    self.add_widget(self.img_widget)

    self.label = Label(
        text='Kameranı qrafikə tutun\nvə SKAN ET basıb gözləyin',
        size_hint_y=0.2,
        font_size='16sp',
        bold=True,
    )
    self.add_widget(self.label)

    self.scan_btn = Button(
        text='🎯 KAMERA İLƏ SKAN ET',
        size_hint_y=0.15,
        background_color=(0, 0.7, 1, 1),
    )
    self.scan_btn.bind(on_press=self.scan_frame)
    self.add_widget(self.scan_btn)

    self.capture = cv2.VideoCapture(0)
    Clock.schedule_interval(self.update_frame, 1.0 / 30.0)
    self.latest_frame = None

  def update_frame(self, dt):
    ret, frame = self.capture.read()
    if ret:
      self.latest_frame = frame.copy()

      h, w, _ = frame.shape
      cv2.rectangle(
          frame,
          (int(w * 0.3), int(h * 0.3)),
          (int(w * 0.7), int(h * 0.7)),
          (0, 255, 0),
          2,
      )

      buf = cv2.flip(frame, 0).tobytes()
      texture = Texture.create(
          size=(frame.shape[1], frame.shape[0]), colorfmt='bgr'
      )
      texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
      self.img_widget.texture = texture

  def scan_frame(self, instance):
    if self.latest_frame is None:
      return

    frame = self.latest_frame
    h, w, _ = frame.shape

    crop = frame[int(h * 0.3) : int(h * 0.7), int(w * 0.3) : int(w * 0.7)]
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)

    # Yeşil mumlar için hassas HSV aralığı
    lower_green = np.array([35, 50, 50])
    upper_green = np.array([85, 255, 255])
    green_mask = cv2.inRange(hsv, lower_green, upper_green)

    # Kırmızı mumlar için hassas HSV aralığı
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)

    green_pixels = cv2.countNonZero(green_mask)
    red_pixels = cv2.countNonZero(red_mask)

    total = green_pixels + red_pixels
    if total < 50:
      self.label.text = '⚠️ Şam rəngi tapılmadı!\nKameranı yaxınlaşdırın.'
      return

    green_ratio = (green_pixels / total) * 100

    if green_ratio > 55:
      self.label.text = (
          f'🚀 SİQNAL: YÜKSƏLİŞ (CALL)\n🟢 Dəqiqlik Gücü: {green_ratio:.1f}%'
      )
    elif green_ratio < 45:
      self.label.text = (
          f'🔻 SİQNAL: DÜŞÜŞ (PUT)\n🔴 Dəqiqlik Gücü: {100-green_ratio:.1f}%'
      )
    else:
      self.label.text = '⚠️ SİQNAL: GÖZLƏ\n(Qeyri-müəyyən bazar trendi)'


class PocketCamApp(App):

  def build(self):
    return CameraScanner()


if __name__ == '__main__':
  PocketCamApp().run()
