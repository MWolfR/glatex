import os

try:
    # for Python2
    import Tkinter as tk
    import ScrolledText as tkst
except ImportError:
    # for Python3
    import tkinter as tk

# --- functions ---


# --- main ---
class Recompiler(object):
    def __init__(self, config, translators):
        self.config = config
        self.translators = translators
        self.create()

    def run_recompile(self):
        from glatex import main, read_latest
        out_name, doc_id, out_dir = read_latest()
        main(out_name, doc_id, out_dir, self.config, self.translators,
             do_refresh=True, do_open=False, make_button=False, write_to=self)

    def create(self):

        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.label = tk.Label(self.root, text="Recompile")
        self.label.grid(row=0, column=0)
        self.img = tk.PhotoImage(file=os.path.join(os.path.split(__file__)[0], 'img', 'refresh.gif'))

        self.button1 = tk.Button(self.root, image=self.img, command=self.run_recompile)
        self.button1.grid(row=1, column=0)

        self.text = tk.Text(self.root)
        self.text.grid(row=2, column=0)

        self.root.mainloop()

    def write(self, a_string):
        self.text.insert(tk.END, a_string)
        self.text.see(tk.END)

    def clear(self):
        self.text.delete('1.0', tk.END)
