from tkinter.constants import END
import pyttsx3
import numpy as np
import textblob
from googletrans import Translator
import googletrans
import cv2
import os, sys
import operator
from string import ascii_uppercase
import tkinter as tk
from PIL import Image, ImageTk
from keras.models import model_from_json
from tkinter import ttk, messagebox

from speech import language_list

os.environ["THEANO_FLAGS"] = "device=cuda, assert_no_cpu_op=True"


class Application:


    def __init__(self):
        self.translator = Translator()
        self.cv = cv2.VideoCapture(0)
        self.current_image = None
        self.current_image2 = None
        self.json_file = open("Models\model_new.json", "r")
        self.model_json = self.json_file.read()
        self.json_file.close()

        self.loaded_model = model_from_json(self.model_json)
        self.loaded_model.load_weights("Models\model_new.h5")
        self.ct = {}
        self.ct['blank'] = 0
        self.blank_flag = 0

        for i in ascii_uppercase:
            self.ct[i] = 0

        print("Loaded model from disk")

        self.root = tk.Tk()
        self.root.title("Final Project - ASL")
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)
        self.root.geometry("1100x1100")

        self.panel = tk.Label(self.root)
        self.panel.place(x=150, y=0, width=580, height=500)

        self.panel2 = tk.Label(self.root)
        self.panel2.place(x=450, y=15, width=275, height=275)

        self.panel3 = tk.Label(self.root)  #Symbol
        self.panel3.place(x=500, y=500)

        self.T1 = tk.Label(self.root)
        self.T1.place(x=10, y=500)
        self.T1.config(text="Character :", font=("Courier", 30, "bold"))

        self.panel4 = tk.Label(self.root)  # Word
        self.panel4.place(x=220, y=540)

        self.T2 = tk.Label(self.root)
        self.T2.place(x=10, y=540)
        self.T2.config(text="Word :", font=("Courier", 30, "bold"))

        self.panel5 = tk.Label(self.root, height=5, width=40, background='#FFEC8B')
        self.panel5.grid(row=0, column=0, pady=600, padx=30)

        self.translate_button = tk.Button(self.root, text="Translate!", font=("Helvetica", 24), command=self.translate_it)
        self.translate_button.grid(row=0, column=1, padx=10)

        self.panel6 = tk.Text(self.root, height=5, width=40, background='#FFEC8B', font=30)
        self.panel6.grid(row=0, column=2, pady=600, padx=50)

        self.str = ""
        self.word = " "
        self.current_symbol = "Empty"
        self.photo = "Empty"
        self.video_loop()

    def translate_it(self):
        self.panel6.delete(1.0, END)
        try:
            words = textblob.TextBlob(self.str)
            words = words.translate(from_lang='en', to='ru')

            self.panel6.insert(1.0, words)
            engine = pyttsx3.init()

            voices = engine.getProperty('voices')

            engine.say(words)

            engine.runAndWait()

        except Exception as e:
            messagebox.showerror("Translator", e)

    def video_loop(self):
        ok, frame = self.cv.read()

        if ok:
            cv2image = cv2.flip(frame, 1)

            x1 = int(0.5 * frame.shape[1])
            y1 = 10
            x2 = frame.shape[1] - 10
            y2 = int(0.5 * frame.shape[1])

            cv2.rectangle(frame, (x1 - 1, y1 - 1), (x2 + 1, y2 + 1), (255, 0, 0), 1)
            cv2image = cv2.cvtColor(cv2image, cv2.COLOR_BGR2RGBA)

            self.current_image = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=self.current_image)

            self.panel.imgtk = imgtk
            self.panel.config(image=imgtk)

            cv2image = cv2image[y1: y2, x1: x2]
            gray = cv2.cvtColor(cv2image, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 2)
            th3 = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
            ret, res = cv2.threshold(th3, 70, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            self.predict(res)
            self.current_image2 = Image.fromarray(res)
            imgtk = ImageTk.PhotoImage(image=self.current_image2)

            self.panel2.imgtk = imgtk
            self.panel2.config(image=imgtk)
            self.panel3.config(text=self.current_symbol, font=("Courier", 30))
            self.panel4.config(text=self.word, font=("Courier", 30))
            self.panel5.config(text=self.str, font=30)

        self.root.after(15, self.video_loop)

    def predict(self, test_image):

        test_image = cv2.resize(test_image, (128, 128))

        result = self.loaded_model.predict(test_image.reshape(1, 128, 128, 1))

        prediction = {}

        prediction['blank'] = result[0][0]

        ad = 0

        for i in ascii_uppercase:
            prediction[i] = result[0][ad]

            ad += 1

        prediction = sorted(prediction.items(), key=operator.itemgetter(1), reverse=True)

        self.current_symbol = prediction[0][0]

        if self.current_symbol == 'blank':

            for i in ascii_uppercase:
                self.ct[i] = 0

        self.ct[self.current_symbol] += 1

        if self.ct[self.current_symbol] > 20:

            for i in ascii_uppercase:
                if i == self.current_symbol:
                    continue

                tmp = self.ct[self.current_symbol] - self.ct[i]

                if tmp < 0:
                    tmp *= -1

                if tmp <= 15:
                    self.ct['blank'] = 0

                    for i in ascii_uppercase:
                        self.ct[i] = 0
                    return

            self.ct['blank'] = 0

            for i in ascii_uppercase:
                self.ct[i] = 0

            if self.current_symbol == 'blank':

                if self.blank_flag == 0:
                    self.blank_flag = 1

                    if len(self.str) > 0:
                        self.str += " "

                    self.str += self.word

                    self.word = ""

            else:

                if len(self.str) > 16:
                    self.str = ""

                self.blank_flag = 0

                self.word += self.current_symbol

    def destructor(self):

        print("Closing Application...")

        self.root.destroy()
        self.cv.release()
        cv2.destroyAllWindows()


print("Starting Application...")

(Application()).root.mainloop()