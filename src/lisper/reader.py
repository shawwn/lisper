from typing import *

import json
import ast
import os

class ReaderError(Exception):
    pass

class EndOfFile(ReaderError):
    pass

def determine_mode(filename):
    _, ext = os.path.splitext(filename)
    if ext in [".el"]:
        return "elisp"
    if ext in [".clj", ".cljs"]:
        return "clojure"
    if ext in [".txt", ".md", ".rst"]:
        return "atoms"
    return "lisp"

def determine_start(filename: str, string: str):
    if ":" in filename:
        line = int(filename.split(":")[1])
        col = 0
        if filename.count(":") >= 2:
            col = int(filename.split(":")[2])
        return line2pos(string, line, col)
    return 0

def determine_end(filename: str, string: str):
    # if filename.count(":") == 2:
    #     return int(filename.split(":")[2])
    return len(string)

def stream(string: str = None, start=None, end=None, more=None, mode=None, filename=None):
    if filename is None:
        filename = "<unknown>"
    filepath = filename.split(":")[0]
    if string is None:
        with open(filepath, mode="rb") as f:
            string = f.read()
    if start is None:
        start = determine_start(filename, string)
    if end is None:
        end = determine_end(filename, string)
    if mode is None:
        mode = determine_mode(filename)
    return ["lit", "stream", string, start, end, more, mode, filepath]

def stream_item(s, idx, *val):
    if val:
        s[idx] = val[0]
    return s[idx]

def stream_string(s, *val) -> bytes:
    return stream_item(s, 2, *val)

def stream_pos(s, *val) -> int:
    return stream_item(s, 3, *val)

def stream_end(s, *val) -> int:
    return stream_item(s, 4, *val)

def stream_more(s, *val) -> Any:
    return stream_item(s, 5, *val)

def stream_mode(s, *val) -> str:
    return stream_item(s, 6, *val)

def stream_filename(s, *val) -> str:
    return stream_item(s, 7, *val)

def lisp_mode_p(mode: str):
    return not text_mode_p(mode)

def text_mode_p(mode: str):
    return mode in ["text", "characters", "atoms"]

def reading_lisp(s):
    return reading(s, "lisp")

def reading_text(s):
    return reading(s, "text")

def reading(s, *modes):
    for mode in modes:
        if mode == "lisp" and lisp_mode_p(mode):
            return True
        elif mode == "text" and text_mode_p(mode):
            return True
        elif mode == stream_mode(s):
            return True
    else:
        return False

def delimiter_p(c):
    return c and c in "\"()[]{},;\r\n"

def elisp_delimiter_p(c):
    return c and c in "\"()[],;\r\n"

def atoms_delimiter_p(c: str):
    return c and not c.isidentifier()

def text_delimiter_p(c):
    return c and c in "\n"

def delimiter_fn(s):
    if reading_lisp(s):
        if stream_mode(s) == 'elisp':
            return elisp_delimiter_p
        return delimiter_p
    else:
        if stream_mode(s) == "atoms":
            return atoms_delimiter_p
        return text_delimiter_p

def closing_p(c):
    return c and c in ")]}"

def elisp_closing_p(c):
    return c and c in ")]"

def text_closing_p(c):
    return False

def closing_fn(s):
    if reading_lisp(s):
        if stream_mode(s) == 'elisp':
            return elisp_closing_p
        return closing_p
    else:
        return text_closing_p

def whitespace_p(c):
    return c and c in " \t\r\n"

def looking_at(s, predicate):
    if c := peek_char(s):
        if predicate(c) if callable(predicate) else c == predicate:
            return c

def parse_char(string: bytes, pos: int, end: int) -> Tuple[Optional[str], int]:
    for n in range(1, 5):
        if pos + n > end:
            return None, 0
        try:
            return string[pos:pos + n].decode("utf8"), n
        except UnicodeDecodeError:
            pass
    return string[pos:pos + 1].decode('latin1'), 1

def parse_chars(string: bytes, pos: int, end: int, count=1) -> Tuple[Optional[str], int]:
    if count == 1:
        return parse_char(string, pos, end)
    total = 0
    out = []
    for n in range(count):
        char, nbytes = parse_char(string, pos + total, end)
        if char is None:
            return char, nbytes
        out.append(char)
        total += nbytes
    return ''.join(out), total

def peek_char(s, count=1, offset=0):
    pos = stream_pos(s) + offset
    char, nbytes = parse_chars(stream_string(s), pos, stream_end(s), count)
    return char

def forward_bytes(s, nbytes: int):
    stream_pos(s, stream_pos(s) + nbytes)

def read_char(s, count=1, offset=0):
    pos = stream_pos(s) + offset
    char, nbytes = parse_chars(stream_string(s), pos, stream_end(s), count)
    forward_bytes(s, nbytes)
    return char

def read_line(s):
    r = []
    while (c := read_char(s)) and c != "\n":
        r.append(c)
    return ''.join(r) + "\n"

def skip_non_code(s):
    if reading_lisp(s):
        while c := peek_char(s):
            if whitespace_p(c):
                read_char(s)
            elif c == ";":
                read_line(s)
            else:
                break
    # elif stream_mode(s) in ["atoms"]:




def skip(s, *predicates: Union[Callable, str]):
    r = []
    while True:
        for predicate in predicates:
            if looking_at(s, predicate):
                break
        else:
            break
        r.append(read_char(s))
    return ''.join(r)

def read_from_string(string, start=0, end=None, more=None, mode=None):
    s = stream(string, start=start, end=end, more=more, mode=mode)
    return read(s), stream_pos(s)

def read(s, eof=None, start=None):
    form = read1(s, eof=eof, start=start)
    if stream_mode(s) not in ["text", "characters", "atoms"]:
        c = peek_char(s)
        if c == ":":
            read_char(s)
            return wrap(s, "%colon", form, start=start)
        if c and c in "([{." and stream_mode(s) in ["lumen"]:
            e = wrap(s, "%snake", form, start=start)
            # print(e)
            return e
        if c == ",":
            eos = object()
            r = ["%tuple", form]
            while True:
                read_char(s)
                form = read1(s, eof=eos, start=start, form=r)
                if form is eos:
                    return expected(s, "tuple", start)
                if form is not None:
                    r.append(form)
                if peek_char(s) != ",":
                    break
            return r
    return form

def read1(s, eof=None, start=None, form=None):
    if start is None:
        start = stream_pos(s)
    c = peek_char(s)
    if c is None:
        return eof
    elif stream_mode(s) == "characters":
        return read_char(s)
    elif stream_mode(s) == "atoms":
        return read_atom(s)
    elif c == '"' and stream_mode(s) != "characters":
        if stream_mode(s) != "text":
            if peek_char(s, 3) == '"""':
                form = read_string(s, '"""', '"""', backquote=True)
                expr = ast.literal_eval(form)
                return json.dumps(expr)
        return read_string(s, '"', '"', backquote=True)
    elif stream_mode(s) not in ["text"]:
        if c == ";":
            return ["lit", "comment", read_line(s)]
        elif c == "(":
            form = read_list(s, "(", ")", start=start)
            if form == stream_more(s):
                return form
            # if len(form) == 1 and form[0] and isinstance(form[0], list) and form[0][0] in ["%tuple", "%colon"]:
            if len(form) == 1 and form[0] and isinstance(form[0], list) and form[0][0] in ["%tuple"]:
                return form[0]
            return form
        elif c == "[":
            form = read_list(s, "[", "]", start=start)
            if form == stream_more(s):
                return form
            # if stream_mode(s) in ["bel", "arc"]:
            #     return ["fn", ["_"], form]
            return ["%brackets", *form]
        elif c == "{" and stream_mode(s) != "elisp":
            return ["%braces", *read_list(s, "{", "}", start=start)]
        # elif c == "|":
        #     return read_string(s, "|", "|", False)
        elif c == "|":
            n = 1
            while peek_char(s, 1, n) == "|":
                n += 1
            open, close = "|" * n, "|" * n
            while (c := peek_char(s, 1, n)) in ["\r", "\n"]:
                open = open + c
                close = c + close
                n += 1
            form = read_string(s, open, close, backquote=True)
            if form == stream_more(s):
                return form
            expr = form[len(open):-len(close)]
            return "|" + expr + "|"
        elif c == "'":
            read_char(s)
            return wrap(s, "quote", start=start)
        elif c == "`":
            read_char(s)
            return wrap(s, "quasiquote", start=start)
        elif c == ("~" if stream_mode(s) == "clojure" else ","):
            read_char(s)
            if peek_char(s) == "@":
                read_char(s)
                return wrap(s, "unquote-splicing", start=start)
            return wrap(s, "unquote", start=start)
        elif closing_fn(s)(c):
            if form:
                # read_char(s)
                return
            # raise BadSyntax(f"Unexpected {peek_char(s)!r} at {format_line_info(s, stream_pos(s))} from {format_line_info(s, start)}")
            raise BadSyntax(s, start)
    return read_atom(s, backquote=True)

class BadSyntax(SyntaxError):
    def __init__(self, s, start: int):
        msg = f"Unexpected {peek_char(s)!r} at {format_line_info(s, stream_pos(s))} from {format_line_info(s, start)}"
        super().__init__(msg)
        self.stream = s
        self.start = start

def read_all(s, *, verbose=False):
    eof = object()
    if verbose:
        prev = stream_pos(s)
        import tqdm
        with tqdm.tqdm(total=stream_end(s), position=stream_pos(s)) as pbar:
            while (x := read(s, eof)) is not eof:
                yield x
                pbar.update(stream_pos(s) - prev)
                prev = stream_pos(s)
    else:
        while (x := read(s, eof)) is not eof:
            yield x

def string2lines(string: Union[str, bytes]):
    return string.splitlines(keepends=True)

def line2pos(string: Union[str, bytes], line: int, col: int = 0):
    lines = string2lines(string)
    line -= 1 # line numbers are 1-based
    if line < len(lines):
        lines[line] = lines[line][0:col]
    pos = sum([len(line) for line in lines[0:line + 1]])
    return pos

def line_info(string: Union[str, bytes], pos: int):
    lines = string2lines(string[0:pos + 1])
    line = len(lines)
    col = len(lines[-1]) + 1
    return line, col

def format_line_info(s, pos: int):
    line, col = line_info(stream_string(s), pos)
    if (filename := stream_filename(s)) is not None:
        return f"pos {pos} (line {line} column {col} file {filename!r})"
    else:
        return f"pos {pos} (line {line} column {col})"

def expected(s, c: str, start: int):
    if (more := stream_more(s)) is not None:
        return more
    raise EndOfFile(f"Expected {c!r} at {format_line_info(s, stream_pos(s))} from {format_line_info(s, start)}")

def read_list(s, open: str, close: str, start=None):
    if start is None:
        start = stream_pos(s)
    assert read_char(s) == open
    out = []
    skip_non_code(s)
    while (c := peek_char(s)) and c != close:
        out.append(read(s, start=start))
        skip_non_code(s)
    if c != close:
        return expected(s, close, start)
    assert read_char(s) == close
    # if len(out) == 1 and isinstance(out[0], list) and out[0] and out[0][0] == "%tuple":
    #     return out[0]
    return out

def read_atom(s, *, backquote: Optional[bool] = None):
    start = stream_pos(s)
    text_mode = text_mode_p(stream_mode(s))
    lisp_mode = not text_mode
    if looking_at(s, ";") and lisp_mode:
        comment = read_line(s)
        return ["lit", "comment", comment]
    if lisp_mode:
        while skip(s, delimiter_fn(s)) or skip(s, whitespace_p):
            pass
    elif looking_at(s, delimiter_fn(s)):
        return read_char(s)
    if whitespace := skip_non_code(s):
        if stream_mode(s) in ["characters", "text", "atoms"]:
            return ["lit", "whitespace", whitespace]
    if looking_at(s, delimiter_fn(s)):
        return ["lit", "delimiter", read_char(s)]
    # if delim := skip(s, delimiter_fn(s)):
    #     if stream_mode(s) in ["characters", "text", "atoms"]:
    #         return ["lit", "delimiters", delim]
    # while looking_at(s, delimiter_fn(s)):
    #     read_char(s)
    out = []
    while c := peek_char(s):
        if backquote is not None:
            if c == '\\' or (stream_mode(s) == "elisp" and c == '?' and len(out) == 0):
                c = read_char(s)
                if backquote:
                    out.append(c)
                out.append(c1 := read_char(s) or expected(s, f"character after {c}", start))
                if c == '?' and c1 == '\\':
                    out.append(read_char(s) or expected(s, f"character after {c1}", start))
                continue
        if not c or whitespace_p(c) or delimiter_fn(s)(c):
            break
        out.append(read_char(s) or expected(s, "character", start))
    if (more := stream_more(s)) in out:
        return more
    form = "".join(out)
    if form.endswith(":") and form != ":":
        stream_pos(s, stream_pos(s) - 1)
        return form[:-1]
    return form

def read_string(s, open: str, close: str, *, backquote: Optional[bool] = None):
    start = stream_pos(s)
    assert read_char(s, len(open)) == open
    out = []
    n = len(close)
    while c := peek_char(s, n):
        if c == close:
            break
        if backquote is not None and c[0] == "\\":
            read_char(s)
            if backquote:
                out.append(c[0])
        out.append(read_char(s) or "")
    if c != close:
        return expected(s, close, start)
    assert read_char(s, n) == close
    return open + "".join(out) + close


def wrap(s, x, *rest, start=None):
    if (y := read(s, start=start)) == stream_more(s):
        return y
    elif x == "%snake" and y and isinstance(y, list) and y[0] == "%snake":
        return [x, *rest, *y[1:]]
    else:
        return [x, *rest, y]

def read_from_file(filename, more=None, mode=None, start=0, end=None):
    with open(filename) as f:
        source = f.read()
    return stream(source, more=more, mode=mode, filename=filename, start=start, end=end)

# s = reader.stream(open(os.path.expanduser("~/ml/bel/bel.bel")).read(), mode='bel'); bel = reader.read_all(s, verbose=True)
# s = reader.stream(open(os.path.expanduser("~/all-emacs.el")).read(), mode='elisp'); emacs = reader.read_all(s, verbose=True)

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    filename = args[0]
    mode = args[1] if len(args) >= 2 else None
    forms = []
    s = stream(filename=filename, mode=mode)
    string = stream_string(s)
    filename = stream_filename(s)
    try:
        for form in read_all(s, verbose=sys.stdout.isatty()):
            forms.append(form)
    except BadSyntax as e:
        start = e.start
        msg = str(e)
        line_start, col_start = line_info(string, start)
        line_pos, col_pos = line_info(string, stream_pos(s))
        forms.append(["lit", "error", {"type": "syntax",
                                       "message": msg,
                                       "pos": {"offset": stream_pos(s), "line": line_pos, "column": col_pos},
                                       "start": {"offset": start, "line": line_start, "column": col_start}}])
    print(json.dumps(["lit", "file", {"forms": forms,
                                     "filename": filename,
                                      "mode": stream_mode(s)}]))
