import tkinter as tk

import nbformat.v4 as nb
import PIL.Image as Image
import py.test

from arlunio.lib.image import encode
from arlunio.tk.notebook import CodeCell, MarkdownCell


@py.test.fixture(scope="function")
def tk_root():
    """Fixture that handles setup/teardown of tk test cases."""

    root = tk.Tk()
    root.deiconify()

    yield root

    root.update()

    for w in root.winfo_children():
        w.destroy()

    root.destroy()


class TestCodeCell:
    """Test cases for the code cell ui component"""

    @py.test.mark.tk
    @py.test.mark.parametrize(
        "txt,height",
        [
            ("", 1),
            ("print('Hello, World!')", 1),
            ("def f(a,b):\n    '''A docstring.'''\n    return a + b", 3),
        ],
    )
    def test_init_existing_cell_source(self, tk_root, txt, height):
        """Ensure that the cell handles being given an existing cell containing source
        code."""

        cell = nb.new_code_cell()
        cell.source = txt

        code_cell = CodeCell(cell, parent=tk_root)
        code_cell.grid(row=1)

        tk_root.update()
        assert code_cell.textbox.get("1.0", "end-1c") == txt
        assert code_cell.textbox.cget("height") == height

    @py.test.mark.tk
    @py.test.mark.parametrize(
        "count,label", [(None, "[ ]: "), (4, "[4]: "), (128, "[128]: ")]
    )
    def test_init_existing_cell_exec_count(self, tk_root, count, label):
        """Ensure that the cell handles being given an existing cell with an execution
        count."""

        cell = nb.new_code_cell()
        cell.execution_count = count

        code_cell = CodeCell(cell, parent=tk_root)
        code_cell.grid(row=0)

        tk_root.update()
        assert code_cell.exec_count["text"] == label

    @py.test.mark.tk
    @py.test.mark.this
    @py.test.mark.parametrize(
        "txt,stream,height",
        [
            ("Hi there\n", "stdout", 1),
            ("a\nb\nc\n", "stdout", 3),
            ("1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n", "stdout", 5),
            ("Logging info\n", "stderr", 1),
        ],
    )
    def test_init_existing_cell_stream(self, tk_root, txt, stream, height):
        """Ensure that the cell handles being given an existing cell with stream
        output."""

        cell = nb.new_code_cell()
        cell.outputs.append(nb.new_output("stream", name=stream, text=txt))

        code_cell = CodeCell(cell, parent=tk_root)
        code_cell.grid(row=0)

        tk_root.update()

        assert code_cell.stream.get("1.0", "end-1c") == txt
        assert code_cell.stream.cget("height") == height

    @py.test.mark.tk
    @py.test.mark.parametrize("txt", ["Hi there", "a\nb\nc"])
    def test_init_existing_cell_output_text(self, tk_root, txt):
        """Ensure that the cell handles being given an existing cell with text
        output."""

        data = {"text/plain": txt}

        cell = nb.new_code_cell()
        cell.outputs.append(nb.new_output("execute_result", data=data))

        code_cell = CodeCell(cell, parent=tk_root)
        code_cell.grid(row=0)

        tk_root.update()

        assert code_cell.textdata["text"] == txt

    @py.test.mark.tk
    def test_init_existing_cell_output_image(self, tk_root, testdata):
        """Ensure that the cell handles being given an existing cell with image
        output."""

        imgpath = testdata("tk/circle.png", path_only=True)
        img = Image.open(imgpath)
        image = encode(img).decode("utf-8")

        data = {"image/png": image + "\n"}

        cell = nb.new_code_cell()
        cell.outputs.append(nb.new_output("execute_result", data=data))

        code_cell = CodeCell(cell, parent=tk_root)
        code_cell.grid(row=1)

        tk_root.update()
        assert code_cell.imgdata is not None  # Is there a better check than this?

    @py.test.mark.tk
    @py.test.mark.parametrize(
        "txt,height,final",
        [
            ("abc", 1, "abc"),
            ("abc\ndef", 2, "abc\ndef"),
            ("abc\n\ndef", 3, "abc\n\ndef"),
            ("abc\ndef\nx\x08\x08", 2, "abc\ndef"),
        ],
    )
    def test_cell_resizes_on_input(self, tk_root, txt, height, final):
        """Ensure that the code cell resizes based on user input."""

        cell = nb.new_code_cell()

        code_cell = CodeCell(cell, parent=tk_root)
        code_cell.grid(row=1)
        tk_root.update()

        code_cell.textbox.focus_force()

        for c in txt:
            sym = c

            if sym == "\n":
                sym = "Return"

            if sym == "\x08":
                sym = "BackSpace"

            code_cell.textbox.event_generate("<KeyPress>", keysym=sym)

        value = code_cell.textbox.get("1.0", "end-1c")
        tk_root.update()

        assert value == final
        assert code_cell.textbox.cget("height") == height


class TestMarkdownCell:
    """Test cases for the markdown cell ui component"""

    @py.test.mark.tk
    @py.test.mark.parametrize(
        "txt,height",
        [(None, 1), ("# Hello World", 1), ("- Item one\n- Item two\n-Item three", 3)],
    )
    def test_init(self, tk_root, txt, height):
        """Ensure that a cell can be created successfully based on an existing cell."""

        cell = nb.new_markdown_cell()

        if txt is not None:
            cell.source = txt

        md_cell = MarkdownCell(cell, parent=tk_root)
        md_cell.grid(row=1)

        assert md_cell.textbox.cget("height") == height
        assert md_cell.textbox.cget("wrap") == "word"

    @py.test.mark.tk
    @py.test.mark.parametrize(
        "txt,height", [("abc", 1), ("abc\ndef", 2), ("abc\n\ndef", 3)]
    )
    def test_cell_resizes_on_input(self, tk_root, txt, height):
        """Ensure that the code cell resizes based on user input."""

        cell = nb.new_markdown_cell()

        markdown_cell = MarkdownCell(cell, parent=tk_root)
        markdown_cell.grid(row=1)
        tk_root.update()

        markdown_cell.textbox.focus_force()

        for c in txt:
            sym = c

            if sym == "\n":
                sym = "Return"

            if sym == "\x08":
                sym = "BackSpace"

            markdown_cell.textbox.event_generate("<KeyPress>", keysym=sym)

        assert markdown_cell.textbox.cget("height") == height
