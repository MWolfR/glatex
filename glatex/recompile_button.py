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

    def run_figures(self):
        self.run_recompile(included_files=True)

    def run_recompile(self, included_files=False):
        from glatex import main, read_latest
        out_name, doc_id, out_dir = read_latest()
        main(out_name, doc_id, out_dir, self.config, self.translators,
             do_refresh=True, do_open=False, make_button=False,
             included_files=included_files, write_to=self)

    def create(self):

        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.label_compile = tk.Label(self.root, text="Recompile")
        self.label_compile.grid(row=0, column=0)
        self.label_figs = tk.Label(self.root, text="Get figures")
        self.label_figs.grid(row=0, column=1)
        self.img = tk.PhotoImage(file=os.path.join(os.path.split(__file__)[0], 'img', 'refresh.gif'))

        self.button1 = tk.Button(self.root, image=self.img, command=self.run_recompile)
        self.button1.grid(row=1, column=0)
        self.button2 = tk.Button(self.root, image=self.img, command=self.run_figures)
        self.button2.grid(row=1, column=1)

        self.text = tk.Text(self.root)
        self.text.grid(row=2, column=0, columnspan=2)

        self.root.mainloop()

    def write(self, a_string):
        self.text.insert(tk.END, a_string)
        self.text.see(tk.END)

    def error(self, retcode):
        msg = "ERROR--ERROR--ERROR\nProcess returned %s. Log above." % str(retcode)
        self.text.insert(tk.END, msg)
        raise Exception()

    def clear(self):
        self.text.delete('1.0', tk.END)
