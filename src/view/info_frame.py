import customtkinter
import pathlib
from PIL import Image, ImageTk
import tkinter


class InfoFrame(customtkinter.CTkFrame):
    def __init__(self, parent, title, info):  # sourcery skip: merge-nested-ifs
        '''
        Creates a 5x2 frame with the following widgets:
            - script title (label)
            - script description (label)
            - script progress bar (progressbar)
            - right-side controls title (label)
            - right-side control buttons (buttons)
        '''
        super().__init__(parent)

        PATH = pathlib.Path(__file__).parent.parent.resolve()

        self.rowconfigure((0, 2, 4, 5), weight=0)  # rows will not resize
        self.rowconfigure((1, 3), weight=1)  # rows will resize
        self.columnconfigure(0, weight=1, minsize=200)
        self.columnconfigure(1, weight=0)

        # -- script title
        self.lbl_script_title = customtkinter.CTkLabel(master=self,
                                                       text=title,
                                                       justify=tkinter.LEFT,
                                                       text_font=("default_theme", 12))
        self.lbl_script_title.grid(column=0, row=0, sticky="wns", padx=15, pady=15)

        # -- script description
        self.lbl_script_desc = customtkinter.CTkLabel(master=self,
                                                      text=info,
                                                      justify=tkinter.CENTER)
        self.lbl_script_desc.grid(column=0, row=2, sticky="nwes", padx=15)
        self.lbl_script_desc.bind('<Configure>', lambda e: self.lbl_script_desc.configure(wraplength=self.lbl_script_desc.winfo_width()-10))

        # -- script progress bar
        self.lbl_progress = customtkinter.CTkLabel(master=self,
                                                   text="Progress: 0%",
                                                   justify=tkinter.CENTER)
        self.lbl_progress.grid(row=4, column=0, pady=(15, 0), sticky="ew")

        self.progressbar = customtkinter.CTkProgressBar(master=self)
        self.progressbar.grid(row=5, column=0, sticky="ew", padx=15, pady=(0, 15))
        self.progressbar.set(0)

        # -- right-side control buttons
        # -- images
        img_size = 18
        self.img_play = ImageTk.PhotoImage(Image.open(f"{PATH}/images/ui/play.png").resize((img_size, img_size)), Image.ANTIALIAS)
        self.img_pause = ImageTk.PhotoImage(Image.open(f"{PATH}/images/ui/pause.png").resize((img_size, img_size)), Image.ANTIALIAS)
        self.img_stop = ImageTk.PhotoImage(Image.open(f"{PATH}/images/ui/stop2.png").resize((img_size, img_size)), Image.ANTIALIAS)
        self.img_options = ImageTk.PhotoImage(Image.open(f"{PATH}/images/ui/options2.png").resize((img_size, img_size)), Image.ANTIALIAS)

        self.lbl_controls_title = customtkinter.CTkLabel(master=self,
                                                         text="Controls",
                                                         justify=tkinter.LEFT,
                                                         text_font=("default_theme", 12))
        self.lbl_controls_title.grid(row=0, column=1, sticky="wns")

        # Button frame
        self.btn_frame = customtkinter.CTkFrame(master=self,
                                                fg_color=self.fg_color)
        self.btn_frame.rowconfigure((1, 2, 3), weight=0)
        self.btn_frame.rowconfigure((0, 4), weight=1)
        self.btn_frame.grid(row=1, rowspan=4, column=1, padx=15, sticky="wns")

        self.btn_play = customtkinter.CTkButton(master=self.btn_frame,
                                                text="Play",
                                                text_color="white",
                                                image=self.img_play,
                                                command=self.play_btn_clicked)
        self.btn_play.grid(row=1, column=0, pady=(0, 15), sticky="nsew")

        self.btn_abort = customtkinter.CTkButton(master=self.btn_frame,
                                                 text="Stop [ESC]",
                                                 text_color="white",
                                                 fg_color="#910101",
                                                 hover_color="#690101",
                                                 image=self.img_stop,
                                                 command=self.stop_btn_clicked)
        self.btn_abort.grid(row=2, column=0, pady=0, sticky="nsew")

        self.btn_options = customtkinter.CTkButton(master=self.btn_frame,
                                                   text="Options",
                                                   text_color="white",
                                                   fg_color="#d97b00",
                                                   hover_color="#b36602",
                                                   image=self.img_options,
                                                   command=self.options_btn_clicked)
        self.btn_options.grid(row=3, column=0, pady=15, sticky="nsew")

        self.lbl_status = customtkinter.CTkLabel(master=self,
                                                 text="Status: Idle",
                                                 justify=tkinter.CENTER)
        self.lbl_status.grid(row=5, column=1, pady=(0, 15), sticky="we")

        self.controller = None
        self.options_class = None

    # ---- Setup ----
    def set_controller(self, controller):
        self.controller = controller

    def setup(self, title, description):
        self.lbl_script_title.configure(text=title)
        self.lbl_script_desc.configure(text=description)

    # ---- Control Button Handlers ----
    def play_btn_clicked(self):
        self.controller.play_pause()

    def stop_btn_clicked(self):
        self.controller.stop()

    # ---- Options Handlers ----
    def on_options_closing(self, window):
        self.controller.abort_options()
        window.destroy()

    def options_btn_clicked(self):
        '''
        Creates a new TopLevel view to display bot options.
        '''
        window = customtkinter.CTkToplevel(master=self)
        window.title("Options")
        window.protocol("WM_DELETE_WINDOW", lambda arg=window: self.on_options_closing(arg))

        view = self.controller.get_options_view(parent=window)
        view.pack(side="top", fill="both", expand=True, padx=20, pady=20)

    # ---- Status Handlers ----
    def update_status_running(self):
        self.__toggle_buttons(True)
        self.btn_options.configure(state=tkinter.DISABLED)
        self.btn_play.configure(image=self.img_pause)
        self.btn_play.configure(text="Pause [ - ]")
        self.lbl_status.configure(text="Status: Running")

    def update_status_paused(self):
        self.__toggle_buttons(True)
        self.btn_options.configure(state=tkinter.DISABLED)
        self.btn_play.configure(image=self.img_play)
        self.btn_play.configure(text="Resume [ = ]")
        self.lbl_status.configure(text="Status: Paused")

    def update_status_stopped(self):
        self.__toggle_buttons(True)
        self.btn_play.configure(image=self.img_play)
        self.btn_play.configure(text="Play")
        self.lbl_status.configure(text="Status: Stopped")

    def update_status_configuring(self):
        self.__toggle_buttons(False)
        self.lbl_status.configure(text="Status: Configuring")

    def __toggle_buttons(self, enabled: bool):
        if enabled:
            self.btn_play.configure(state=tkinter.NORMAL)
            self.btn_abort.configure(state=tkinter.NORMAL)
            self.btn_options.configure(state=tkinter.NORMAL)
        else:
            self.btn_play.configure(state=tkinter.DISABLED)
            self.btn_abort.configure(state=tkinter.DISABLED)
            self.btn_options.configure(state=tkinter.DISABLED)

    # ---- Progress Bar Handlers ----
    def update_progress(self, progress: float):
        '''
        Called from controller. Updates the progress bar and percentage.
        Args:
            progress: The progress of the script, a float between 0 and 1.
        '''
        self.progressbar.set(progress)
        self.lbl_progress.configure(text=f"Progress: {progress*100:.0f}%")
