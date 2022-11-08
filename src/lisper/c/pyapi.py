from __future__ import annotations

# From https://www.programcreek.com/python/?code=Frank-qlu%2Frecruit%2Frecruit-master%2F%E6%8B%9B%E8%81%98%E7%88%AC%E8%99%AB%2FzlzpView%2Fvenv%2FLib%2Fsite-packages%2Fclick%2F_winconsole.py

# See also the `pybuffer` pip module: https://github.com/ShigekiKarita/mir-pybuffer/blob/master/pybuffer/__init__.py

import inspect
import ctypes as _c
from typing import Tuple, Optional, Sequence, Literal, Union

# from https://github.com/ShigekiKarita/mir-pybuffer/blob/master/pybuffer/__init__.py
# see also
# https://docs.python.org/3/c-api/buffer.html#buffer-request-types
# $CONDA_PREFIX/include/python3.6m/object.h
PyBUF_SIMPLE = 0
PyBUF_WRITABLE = 0x0001
PyBUF_FORMAT = 0x0004
PyBUF_ND = 0x0008
PyBUF_STRIDES = 0x0010 | PyBUF_ND

PyBUF_C_CONTIGUOUS = 0x0020 | PyBUF_STRIDES
PyBUF_F_CONTIGUOUS = 0x0040 | PyBUF_STRIDES
PyBUF_ANY_CONTIGUOUS = 0x0080 | PyBUF_STRIDES
PyBUF_INDIRECT = 0x0100 | PyBUF_STRIDES

PyBUF_CONTIG_RO = PyBUF_ND
PyBUF_CONTIG = PyBUF_ND | PyBUF_WRITABLE

PyBUF_STRIDED_RO = PyBUF_STRIDES
PyBUF_STRIDED = PyBUF_STRIDES | PyBUF_WRITABLE

PyBUF_RECORDS_RO = PyBUF_STRIDES | PyBUF_FORMAT
PyBUF_RECORDS = PyBUF_STRIDES | PyBUF_FORMAT | PyBUF_WRITABLE

PyBUF_FULL_RO = PyBUF_INDIRECT | PyBUF_FORMAT
PyBUF_FULL = PyBUF_INDIRECT | PyBUF_FORMAT | PyBUF_WRITABLE

PyBUF_READ = 0x100
PyBUF_WRITE = 0x200

c_ssize_p = _c.POINTER(_c.c_ssize_t)

# https://gist.github.com/riga/0a751a4555276804b54fdfeb97629a6a
import gc
import sys

# configuration of Py_IncRef and Py_DecRef
_c_inc_ref = _c.pythonapi.Py_IncRef
_c_inc_ref.argtypes = [_c.py_object]
_c_dec_ref = _c.pythonapi.Py_DecRef
_c_dec_ref.argtypes = [_c.py_object]


def inc_ref(obj, n=1):
  """
  Increases the reference count of an object *obj* by *n*.
  """
  for _ in range(n):
    _c_inc_ref(obj)


def dec_ref(obj, n=1, collect=True):
  """
  Decreases the reference count of an object *obj* by *n*. When *collect* is *True*, the garbage
  collector is initiated afterwards.
  """
  for _ in range(n):
    _c_dec_ref(obj)

  if collect:
    gc.collect()

def ref_count(obj):
    """
    Returns the number of references to an object *obj*.
    """
    # subtract 3 for: function argument, reference in getrefcount, and the function stack
    return sys.getrefcount(obj) - 3
    # return len(gc.get_referrers(obj)) - 1

def asvoidp(ptr):
  return _c.cast(ptr, _c.c_void_p)

def isnull(ptr):
  return asvoidp(ptr).value is None

def deref(ptr):
  if not isnull(ptr):
    return ptr.contents

all_objs = globals().setdefault("all_objs", {})

def asobj(ptr):
  if not isnull(ptr):
    addr = asvoidp(ptr).value
    obj = _c.cast(ptr, _c.py_object)
    all_objs[addr] = obj.value
    # inc_ref(obj)
    return obj.value

# From https://gist.github.com/Ivoz/6838728

# Create a function prototype for a 3-arg function
# typedef PyObject * (*ternaryfunc)(PyObject *, PyObject *, PyObject *);
ternaryfunc = _c.CFUNCTYPE(_c.py_object, _c.py_object, _c.py_object, _c.c_void_p)

# typedef PyObject *(*reprfunc)(PyObject *);
reprfunc = _c.CFUNCTYPE(_c.py_object, _c.py_object)

class PyBufferProcs(_c.Structure):
  pass

class PyObject(_c.Structure):
  pass

class PyVarObject(_c.Structure):
  pass

class PyTypeObject(_c.Structure):
  def __repr__(self):
    return f"#<PyTypeObject {self.tp_name.decode('utf-8')!r}>"

class _PyInterpreterFrame(_c.Structure):
  pass

class PyThreadState(_c.Structure):
  pass

class PyInterpreterState(_c.Structure):
  pass

PyThread_type_lock = _c.c_void_p

class pyruntimestate(_c.Structure):
  pass


class pyinterpreters(_c.Structure):
  pass

PyObject._fields_ = (
  ("ob_refcnt", _c.c_ssize_t),
  ("ob_type", _c.POINTER(PyTypeObject)),
)

PyVarObject._fields_ = (
  *PyObject._fields_,
  ("ob_size", _c.c_ssize_t), # Number of items in variable part
)

PyTypeObject._fields_ = (
  # ("ob_refcnt", _c.c_ssize_t),
  # ("ob_type", _c.c_void_p),
  # ("ob_size", _c.c_ssize_t),
  *PyVarObject._fields_,
  ("tp_name", _c.c_char_p),
  ("tp_basicsize", _c.c_ssize_t),
  ("tp_itemsize", _c.c_ssize_t),
  ("tp_dealloc", _c.c_void_p),
  ("tp_print", _c.c_void_p),
  ("tp_getattr", _c.c_void_p),
  ("tp_setattr", _c.c_void_p),
  ("tp_reserved", _c.c_void_p),
  ("tp_repr", reprfunc),
  ("tp_as_number", _c.c_void_p),
  ("tp_as_sequence", _c.c_void_p),
  ("tp_as_wrapping", _c.c_void_p),
  ("tp_hash", _c.c_void_p),
  ("tp_call", ternaryfunc),
  ("tp_str", reprfunc),
  ("tp_getattro", _c.c_void_p),
  ("tp_setattro", _c.c_void_p),

  # /* Functions to access object as input/output buffer */
  # PyBufferProcs *tp_as_buffer;
  ("tp_as_buffer", _c.POINTER(PyBufferProcs)),

  # /* Flags to define presence of optional/expanded features */
  # unsigned long tp_flags;
  ("tp_flags", _c.c_ulong),
  #
  # const char *tp_doc; /* Documentation string */
  ("tp_doc", _c.c_char_p),
)

class PyFrameObject(_c.Structure):
  pass

# # /* See Objects/frame_layout.md for an explanation of the frame stack
# #  * including explanation of the PyFrameObject and _PyInterpreterFrame
# #  * structs. */
# #
# #
# PyFrameObject._fields_ = [
# # struct _frame {
# #     PyObject_HEAD
#   *PyObject._fields_,
# #     PyFrameObject *f_back;      /* previous frame, or NULL */
#   ("f_back", _c.POINTER(PyFrameObject)),
# #     struct _PyInterpreterFrame *f_frame; /* points to the frame data */
#   ("f_frame", _c.POINTER(_PyInterpreterFrame)),
# #     PyObject *f_trace;          /* Trace function */
#   ("f_trace", _c.c_void_p),
# #     int f_lineno;               /* Current line number. Only valid if non-zero */
#   ("f_lineno", _c.c_int),
# #     char f_trace_lines;         /* Emit per-line trace events? */
#   ("f_trace_lines", _c.c_char),
# #     char f_trace_opcodes;       /* Emit per-opcode trace events? */
#   ("f_trace_opcodes", _c.c_char),
# #     char f_fast_as_locals;      /* Have the fast locals of this frame been converted to a dict? */
#   ("f_fast_as_locals", _c.c_char),
# #     /* The frame data, if this frame object owns the frame */
# #     PyObject *_f_frame_data[1];
#   ("_f_frame_data", (_c.c_void_p * 1)),
# # };
# ]

# typedef struct {
#     int b_type;                 /* what kind of block this is */
#     int b_handler;              /* where to jump to find handler */
#     int b_level;                /* value stack level to pop to */
# } PyTryBlock;
class PyTryBlock(_c.Structure):
  _fields_ = [
    ("b_type", _c.c_int),
    ("b_handler", _c.c_int),
    ("b_level", _c.c_int),
  ]

CO_MAXBLOCKS = 20

PyFrameObject._fields_ = [
# struct _frame {
#     PyObject_VAR_HEAD
      *PyVarObject._fields_,
#     struct _frame *f_back;      /* previous frame, or NULL */
      ("f_back", _c.POINTER(PyFrameObject)),
#     PyCodeObject *f_code;       /* code segment */
      ("f_code", _c.c_void_p),
#     PyObject *f_builtins;       /* builtin symbol table (PyDictObject) */
      ("f_builtins", _c.c_void_p),
#     PyObject *f_globals;        /* global symbol table (PyDictObject) */
      ("f_globals", _c.c_void_p),
#     PyObject *f_locals;         /* local symbol table (any mapping) */
      ("f_locals", _c.c_void_p),
#     PyObject **f_valuestack;    /* points after the last local */
      ("f_valuestack", _c.POINTER(_c.c_void_p)),
#     /* Next free slot in f_valuestack.  Frame creation sets to f_valuestack.
#        Frame evaluation usually NULLs it, but a frame that yields sets it
#        to the current stack top. */
#     PyObject **f_stacktop;
      ("f_stacktop", _c.POINTER(_c.c_void_p)),
#     PyObject *f_trace;          /* Trace function */
      ("f_trace", _c.c_void_p),
#     char f_trace_lines;         /* Emit per-line trace events? */
      ("f_trace_lines", _c.c_char),
#     char f_trace_opcodes;       /* Emit per-opcode trace events? */
      ("f_trace_opcodes", _c.c_char),
#
#     /* Borrowed reference to a generator, or NULL */
#     PyObject *f_gen;
      ("f_gen", _c.c_void_p),
#
#     int f_lasti;                /* Last instruction if called */
      ("f_lasti", _c.c_int),
#     /* Call PyFrame_GetLineNumber() instead of reading this field
#        directly.  As of 2.3 f_lineno is only valid when tracing is
#        active (i.e. when f_trace is set).  At other times we use
#        PyCode_Addr2Line to calculate the line from the current
#        bytecode index. */
#     int f_lineno;               /* Current line number */
      ("f_lineno", _c.c_int),
#     int f_iblock;               /* index in f_blockstack */
      ("f_iblock", _c.c_int),
#     char f_executing;           /* whether the frame is still executing */
      ("f_executing", _c.c_char),
#     PyTryBlock f_blockstack[CO_MAXBLOCKS]; /* for try and loop blocks */
      ("f_blockstack", (PyTryBlock * CO_MAXBLOCKS)),
#     PyObject *f_localsplus[1];  /* locals+stack, dynamically sized */
      ("f_localsplus", _c.POINTER(_c.c_void_p)),
# };
]

pycapi_PyEval_GetFrame = _c.pythonapi.PyEval_GetFrame
pycapi_PyEval_GetFrame.restype = _c.POINTER(PyFrameObject)
pycapi_PyEval_GetFrame.argtypes = []
def PyEval_GetFrame():
  return pycapi_PyEval_GetFrame()

# PyFrameObject *PyFrame_GetBack(PyFrameObject *frame)
pycapi_PyFrame_GetBack = _c.pythonapi.PyFrame_GetBack
pycapi_PyFrame_GetBack.restype = _c.POINTER(PyFrameObject)
pycapi_PyFrame_GetBack.argtypes = [_c.POINTER(PyFrameObject)]
def PyFrame_GetBack(frame):
  if frame:
    return pycapi_PyFrame_GetBack(frame)

#
# extern PyFrameObject* _PyFrame_New_NoTrack(PyCodeObject *code);

_Py_CODEUNIT = _c.c_uint16

_PyInterpreterFrame._fields_ = (
# typedef struct _PyInterpreterFrame {
#     /* "Specials" section */
#     PyFunctionObject *f_func; /* Strong reference */
      ("f_func", _c.c_void_p),
#     PyObject *f_globals; /* Borrowed reference */
      ("f_globals", _c.c_void_p),
#     PyObject *f_builtins; /* Borrowed reference */
      ("f_builtins", _c.c_void_p),
#     PyObject *f_locals; /* Strong reference, may be NULL */
      ("f_locals", _c.c_void_p),
#     PyCodeObject *f_code; /* Strong reference */
      ("f_code", _c.c_void_p),
#     PyFrameObject *frame_obj; /* Strong reference, may be NULL */
      ("frame_obj", _c.c_void_p),
#     /* Linkage section */
#     struct _PyInterpreterFrame *previous;
      ("previous", _c.POINTER(_PyInterpreterFrame)),
#     // NOTE: This is not necessarily the last instruction started in the given
#     // frame. Rather, it is the code unit *prior to* the *next* instruction. For
#     // example, it may be an inline CACHE entry, an instruction we just jumped
#     // over, or (in the case of a newly-created frame) a totally invalid value:
#     _Py_CODEUNIT *prev_instr;
      ("prev_instr", _c.POINTER(_Py_CODEUNIT)),
#     int stacktop;     /* Offset of TOS from localsplus  */
      ("stacktop", _c.c_int),
#     bool is_entry;  // Whether this is the "root" frame for the current _PyCFrame.
      ("is_entry", _c.c_bool),
#     char owner;
      ("owner", _c.c_char),
#     /* Locals and stack */
#     PyObject *localsplus[1];
      ("localsplus", _c.c_void_p),
# } _PyInterpreterFrame;
)

class _PyCFrame(_c.Structure):
  pass

_PyCFrame._fields_ = (
# // Internal structure: you should not use it directly, but use public functions
# // like PyThreadState_EnterTracing() and PyThreadState_LeaveTracing().
# typedef struct _PyCFrame {
#     /* This struct will be threaded through the C stack
#      * allowing fast access to per-thread state that needs
#      * to be accessed quickly by the interpreter, but can
#      * be modified outside of the interpreter.
#      *
#      * WARNING: This makes data on the C stack accessible from
#      * heap objects. Care must be taken to maintain stack
#      * discipline and make sure that instances of this struct cannot
#      * accessed outside of their lifetime.
#      */
#     uint8_t use_tracing;  // 0 or 255 (or'ed into opcode, hence 8-bit type)
      ("use_tracing", _c.c_uint8),
#     /* Pointer to the currently executing frame (it can be NULL) */
#     struct _PyInterpreterFrame *current_frame;
      ("current_frame", _c.POINTER(_PyInterpreterFrame)),
#     struct _PyCFrame *previous;
      ("previous", _c.POINTER(_PyCFrame)),
# } _PyCFrame;
)


# struct _ts {
#     /* See Python/ceval.c for comments explaining most fields */
#
#     PyThreadState *prev;
#     PyThreadState *next;
#     PyInterpreterState *interp;
#
#     /* Has been initialized to a safe state.
#
#        In order to be effective, this must be set to 0 during or right
#        after allocation. */
#     int _initialized;
#
#     /* Was this thread state statically allocated? */
#     int _static;
#
#     int recursion_remaining;
#     int recursion_limit;
#     int recursion_headroom; /* Allow 50 more calls to handle any errors. */
#
#     /* 'tracing' keeps track of the execution depth when tracing/profiling.
#        This is to prevent the actual trace/profile code from being recorded in
#        the trace/profile. */
#     int tracing;
#     int tracing_what; /* The event currently being traced, if any. */
#
#     /* Pointer to current _PyCFrame in the C stack frame of the currently,
#      * or most recently, executing _PyEval_EvalFrameDefault. */
#     _PyCFrame *cframe;
#
#     Py_tracefunc c_profilefunc;
#     Py_tracefunc c_tracefunc;
#     PyObject *c_profileobj;
#     PyObject *c_traceobj;
#
#     /* The exception currently being raised */
#     PyObject *curexc_type;
#     PyObject *curexc_value;
#     PyObject *curexc_traceback;
#
#     /* Pointer to the top of the exception stack for the exceptions
#      * we may be currently handling.  (See _PyErr_StackItem above.)
#      * This is never NULL. */
#     _PyErr_StackItem *exc_info;
#
#     PyObject *dict;  /* Stores per-thread state */
#
#     int gilstate_counter;
#
#     PyObject *async_exc; /* Asynchronous exception to raise */
#     unsigned long thread_id; /* Thread id where this tstate was created */
#
#     /* Native thread id where this tstate was created. This will be 0 except on
#      * those platforms that have the notion of native thread id, for which the
#      * macro PY_HAVE_THREAD_NATIVE_ID is then defined.
#      */
#     unsigned long native_thread_id;
#
#     int trash_delete_nesting;
#     PyObject *trash_delete_later;
#
#     /* Called when a thread state is deleted normally, but not when it
#      * is destroyed after fork().
#      * Pain:  to prevent rare but fatal shutdown errors (issue 18808),
#      * Thread.join() must wait for the join'ed thread's tstate to be unlinked
#      * from the tstate chain.  That happens at the end of a thread's life,
#      * in pystate.c.
#      * The obvious way doesn't quite work:  create a lock which the tstate
#      * unlinking code releases, and have Thread.join() wait to acquire that
#      * lock.  The problem is that we _are_ at the end of the thread's life:
#      * if the thread holds the last reference to the lock, decref'ing the
#      * lock will delete the lock, and that may trigger arbitrary Python code
#      * if there's a weakref, with a callback, to the lock.  But by this time
#      * _PyRuntime.gilstate.tstate_current is already NULL, so only the simplest
#      * of C code can be allowed to run (in particular it must not be possible to
#      * release the GIL).
#      * So instead of holding the lock directly, the tstate holds a weakref to
#      * the lock:  that's the value of on_delete_data below.  Decref'ing a
#      * weakref is harmless.
#      * on_delete points to _threadmodule.c's static release_sentinel() function.
#      * After the tstate is unlinked, release_sentinel is called with the
#      * weakref-to-lock (on_delete_data) argument, and release_sentinel releases
#      * the indirectly held lock.
#      */
#     void (*on_delete)(void *);
#     void *on_delete_data;
#
#     int coroutine_origin_tracking_depth;
#
#     PyObject *async_gen_firstiter;
#     PyObject *async_gen_finalizer;
#
#     PyObject *context;
#     uint64_t context_ver;
#
#     /* Unique thread state id. */
#     uint64_t id;
#
#     PyTraceInfo trace_info;
#
#     _PyStackChunk *datastack_chunk;
#     PyObject **datastack_top;
#     PyObject **datastack_limit;
#     /* XXX signal handlers should also be here */
#
#     /* The following fields are here to avoid allocation during init.
#        The data is exposed through PyThreadState pointer fields.
#        These fields should not be accessed directly outside of init.
#        This is indicated by an underscore prefix on the field names.
#
#        All other PyInterpreterState pointer fields are populated when
#        needed and default to NULL.
#        */
#        // Note some fields do not have a leading underscore for backward
#        // compatibility.  See https://bugs.python.org/issue45953#msg412046.
#
#     /* The thread's exception stack entry.  (Always the last entry.) */
#     _PyErr_StackItem exc_state;
#
#     /* The bottom-most frame on the stack. */
#     _PyCFrame root_cframe;
# };

PyThreadState._fields_ = (
  #     /* See Python/ceval.c for comments explaining most fields */
  #
  #     PyThreadState *prev;
  #     PyThreadState *next;
  #     PyInterpreterState *interp;
  ("prev", _c.POINTER(PyThreadState)),
  ("next", _c.POINTER(PyThreadState)),
  ("interp", _c.POINTER(PyInterpreterState)),
  #
  #     /* Has been initialized to a safe state.
  #
  #        In order to be effective, this must be set to 0 during or right
  #        after allocation. */
  #     int _initialized;
  ("_initialized", _c.c_int),
  #
  #     /* Was this thread state statically allocated? */
  #     int _static;
  ("_static", _c.c_int),
  #     int recursion_remaining;
  #     int recursion_limit;
  #     int recursion_headroom; /* Allow 50 more calls to handle any errors. */
  ("recursion_remaining", _c.c_int),
  ("recursion_limit", _c.c_int),
  ("recursion_headroom", _c.c_int),
  #     /* 'tracing' keeps track of the execution depth when tracing/profiling.
  #        This is to prevent the actual trace/profile code from being recorded in
  #        the trace/profile. */
  #     int tracing;
  #     int tracing_what; /* The event currently being traced, if any. */
  ("tracing", _c.c_int),
  ("tracing_what", _c.c_int),
  #
  #     /* Pointer to current _PyCFrame in the C stack frame of the currently,
  #      * or most recently, executing _PyEval_EvalFrameDefault. */
  #     _PyCFrame *cframe;
  ("cframe", _c.POINTER(_PyCFrame)),
  #
  #     Py_tracefunc c_profilefunc;
  #     Py_tracefunc c_tracefunc;
  ("c_profilefunc", _c.c_void_p),
  ("c_tracefunc", _c.c_void_p),
  #     PyObject *c_profileobj;
  #     PyObject *c_traceobj;
  ("c_profileobj", _c.py_object),
  ("c_traceobj", _c.py_object),
  #
  #     /* The exception currently being raised */
  #     PyObject *curexc_type;
  #     PyObject *curexc_value;
  #     PyObject *curexc_traceback;
  ("curexc_type", _c.py_object),
  ("curexc_value", _c.py_object),
  ("curexc_traceback", _c.py_object),
  #     /* Pointer to the top of the exception stack for the exceptions
  #      * we may be currently handling.  (See _PyErr_StackItem above.)
  #      * This is never NULL. */
  #     _PyErr_StackItem *exc_info;
  ("exc_info", _c.c_void_p),
  #
  #     PyObject *dict;  /* Stores per-thread state */
  ("dict", _c.py_object),
  #
  #     int gilstate_counter;
  ("gilstate_counter", _c.c_int),
  #
  #     PyObject *async_exc; /* Asynchronous exception to raise */
  #     unsigned long thread_id; /* Thread id where this tstate was created */
  ("async_exc", _c.py_object),
  ("thread_id", _c.c_ulong),
  #
  #     /* Native thread id where this tstate was created. This will be 0 except on
  #      * those platforms that have the notion of native thread id, for which the
  #      * macro PY_HAVE_THREAD_NATIVE_ID is then defined.
  #      */
  #     unsigned long native_thread_id;
  ("native_thread_id", _c.c_ulong),
  #
  #     int trash_delete_nesting;
  #     PyObject *trash_delete_later;
  ("trash_delete_nesting", _c.c_int),
  ("trash_delete_later", _c.c_void_p),
  #
  #     /* Called when a thread state is deleted normally, but not when it
  #      * is destroyed after fork().
  #      * Pain:  to prevent rare but fatal shutdown errors (issue 18808),
  #      * Thread.join() must wait for the join'ed thread's tstate to be unlinked
  #      * from the tstate chain.  That happens at the end of a thread's life,
  #      * in pystate.c.
  #      * The obvious way doesn't quite work:  create a lock which the tstate
  #      * unlinking code releases, and have Thread.join() wait to acquire that
  #      * lock.  The problem is that we _are_ at the end of the thread's life:
  #      * if the thread holds the last reference to the lock, decref'ing the
  #      * lock will delete the lock, and that may trigger arbitrary Python code
  #      * if there's a weakref, with a callback, to the lock.  But by this time
  #      * _PyRuntime.gilstate.tstate_current is already NULL, so only the simplest
  #      * of C code can be allowed to run (in particular it must not be possible to
  #      * release the GIL).
  #      * So instead of holding the lock directly, the tstate holds a weakref to
  #      * the lock:  that's the value of on_delete_data below.  Decref'ing a
  #      * weakref is harmless.
  #      * on_delete points to _threadmodule.c's static release_sentinel() function.
  #      * After the tstate is unlinked, release_sentinel is called with the
  #      * weakref-to-lock (on_delete_data) argument, and release_sentinel releases
  #      * the indirectly held lock.
  #      */
  #     void (*on_delete)(void *);
  #     void *on_delete_data;
  ("on_delete", _c.c_void_p),
  ("on_delete_data", _c.c_void_p),
  #
  #     int coroutine_origin_tracking_depth;
  ("coroutine_origin_tracking_depth", _c.c_int),
  #
  #     PyObject *async_gen_firstiter;
  #     PyObject *async_gen_finalizer;
  ("async_gen_firstiter", _c.py_object),
  ("async_gen_finalizer", _c.py_object),
  #
  #     PyObject *context;
  #     uint64_t context_ver;
  ("context", _c.c_void_p),
  ("context_ver", _c.c_uint64),
  #
  #     /* Unique thread state id. */
  #     uint64_t id;
  ("id", _c.c_uint64),
  #
  #     PyTraceInfo trace_info;
  #
  #     _PyStackChunk *datastack_chunk;
  #     PyObject **datastack_top;
  #     PyObject **datastack_limit;
  #     /* XXX signal handlers should also be here */
  #
  #     /* The following fields are here to avoid allocation during init.
  #        The data is exposed through PyThreadState pointer fields.
  #        These fields should not be accessed directly outside of init.
  #        This is indicated by an underscore prefix on the field names.
  #
  #        All other PyInterpreterState pointer fields are populated when
  #        needed and default to NULL.
  #        */
  #        // Note some fields do not have a leading underscore for backward
  #        // compatibility.  See https://bugs.python.org/issue45953#msg412046.
  #
  #     /* The thread's exception stack entry.  (Always the last entry.) */
  #     _PyErr_StackItem exc_state;
  #
  #     /* The bottom-most frame on the stack. */
  #     _PyCFrame root_cframe;
)

class pythreads(_c.Structure):
  pass

pythreads._fields_ = (
#     struct pythreads {
#         uint64_t next_unique_id;
          ("next_unique_id", _c.c_uint64),
#         /* The linked list of threads, newest first. */
#         PyThreadState *head;
          ("head", _c.POINTER(PyThreadState)),
#         /* Used in Modules/_threadmodule.c. */
#         long count;
          ("count", _c.c_long),
#         /* Support for runtime thread stack size tuning.
#            A value of 0 means using the platform's default stack size
#            or the size specified by the THREAD_STACK_SIZE macro. */
#         /* Used in Python/thread.c. */
#         size_t stacksize;
          ("stacksize", _c.c_size_t),
#     } threads;
)



# /* interpreter state */
#
# /* PyInterpreterState holds the global state for one of the runtime's
#    interpreters.  Typically the initial (main) interpreter is the only one.
#
#    The PyInterpreterState typedef is in Include/pytypedefs.h.
#    */
PyInterpreterState._fields_ = (
# struct _is {
#
#     PyInterpreterState *next;
      ("next", _c.POINTER(PyInterpreterState)),
#
#     struct pythreads {
#         uint64_t next_unique_id;
#         /* The linked list of threads, newest first. */
#         PyThreadState *head;
#         /* Used in Modules/_threadmodule.c. */
#         long count;
#         /* Support for runtime thread stack size tuning.
#            A value of 0 means using the platform's default stack size
#            or the size specified by the THREAD_STACK_SIZE macro. */
#         /* Used in Python/thread.c. */
#         size_t stacksize;
#     } threads;
      ("threads", pythreads),
#
#     /* Reference to the _PyRuntime global variable. This field exists
#        to not have to pass runtime in addition to tstate to a function.
#        Get runtime from tstate: tstate->interp->runtime. */
#     struct pyruntimestate *runtime;
      ("runtime", _c.POINTER(pyruntimestate)),
#
#     int64_t id;
      ("id", _c.c_int64),
#     int64_t id_refcount;
      ("id_refcount", _c.c_int64),
#     int requires_idref;
      ("requires_idref", _c.c_int),
#     PyThread_type_lock id_mutex;
      ("id_mutex", _c.c_void_p),
#
#     /* Has been initialized to a safe state.
#
#        In order to be effective, this must be set to 0 during or right
#        after allocation. */
#     int _initialized;
      ("_initialized", _c.c_int),
#     int finalizing;
      ("finalizing", _c.c_int),
#
#     /* Was this interpreter statically allocated? */
#     bool _static;
      ("_static", _c.c_bool),
#
#     struct _ceval_state ceval;
#     struct _gc_runtime_state gc;
#
#     // sys.modules dictionary
#     PyObject *modules;
#     PyObject *modules_by_index;
#     // Dictionary of the sys module
#     PyObject *sysdict;
#     // Dictionary of the builtins module
#     PyObject *builtins;
#     // importlib module
#     PyObject *importlib;
#     // override for config->use_frozen_modules (for tests)
#     // (-1: "off", 1: "on", 0: no override)
#     int override_frozen_modules;
#
#     PyObject *codec_search_path;
#     PyObject *codec_search_cache;
#     PyObject *codec_error_registry;
#     int codecs_initialized;
#
#     PyConfig config;
# #ifdef HAVE_DLOPEN
#     int dlopenflags;
# #endif
#
#     PyObject *dict;  /* Stores per-interpreter state */
#
#     PyObject *builtins_copy;
#     PyObject *import_func;
#     // Initialized to _PyEval_EvalFrameDefault().
#     _PyFrameEvalFunction eval_frame;
#
#     Py_ssize_t co_extra_user_count;
#     freefunc co_extra_freefuncs[MAX_CO_EXTRA_USERS];
#
# #ifdef HAVE_FORK
#     PyObject *before_forkers;
#     PyObject *after_forkers_parent;
#     PyObject *after_forkers_child;
# #endif
#
#     struct _warnings_runtime_state warnings;
#     struct atexit_state atexit;
#
#     PyObject *audit_hooks;
#
#     struct _Py_unicode_state unicode;
#     struct _Py_float_state float_state;
#     /* Using a cache is very effective since typically only a single slice is
#        created and then deleted again. */
#     PySliceObject *slice_cache;
#
#     struct _Py_tuple_state tuple;
#     struct _Py_list_state list;
#     struct _Py_dict_state dict_state;
#     struct _Py_async_gen_state async_gen;
#     struct _Py_context_state context;
#     struct _Py_exc_state exc_state;
#
#     struct ast_state ast;
#     struct types_state types;
#     struct callable_cache callable_cache;
#
#     /* The following fields are here to avoid allocation during init.
#        The data is exposed through PyInterpreterState pointer fields.
#        These fields should not be accessed directly outside of init.
#
#        All other PyInterpreterState pointer fields are populated when
#        needed and default to NULL.
#
#        For now there are some exceptions to that rule, which require
#        allocation during init.  These will be addressed on a case-by-case
#        basis.  Also see _PyRuntimeState regarding the various mutex fields.
#        */
#
#     /* the initial PyInterpreterState.threads.head */
#     PyThreadState _initial_thread;
# };
)

# typedef struct _Py_atomic_address {
#     uintptr_t _value;
# } _Py_atomic_address;

class _Py_atomic_address(_c.Structure):
  _fields_ = [
    ("_value", _c.POINTER(_c.c_uint))
  ]

pyinterpreters._fields_ = (
#     struct pyinterpreters {
#         PyThread_type_lock mutex;
          ("mutex", PyThread_type_lock),
#         /* The linked list of interpreters, newest first. */
#         PyInterpreterState *head;
          ("head", _c.POINTER(PyInterpreterState)),
#         /* The runtime's initial interpreter, which has a special role
#            in the operation of the runtime.  It is also often the only
#            interpreter. */
#         PyInterpreterState *main;
          ("main", _c.POINTER(PyInterpreterState)),
#         /* _next_interp_id is an auto-numbered sequence of small
#            integers.  It gets initialized in _PyInterpreterState_Init(),
#            which is called in Py_Initialize(), and used in
#            PyInterpreterState_New().  A negative interpreter ID
#            indicates an error occurred.  The main interpreter will
#            always have an ID of 0.  Overflow results in a RuntimeError.
#            If that becomes a problem later then we can adjust, e.g. by
#            using a Python int. */
#         int64_t next_id;
          ("next_id", _c.c_int64),
#     } interpreters;
)

# struct _xidregitem {
#     PyTypeObject *cls;
#     crossinterpdatafunc getdata;
#     struct _xidregitem *next;
# };
class _xidregitem(_c.Structure):
  pass

_xidregitem._fields_ = [
    ("cls", _c.POINTER(PyTypeObject)),
    ("getdata", _c.c_void_p),
    ("next", _c.POINTER(_xidregitem)),
  ]

class _xidregistry(_c.Structure):
  pass

_xidregistry._fields_ = (
#     // XXX Remove this field once we have a tp_* slot.
#     struct _xidregistry {
#         PyThread_type_lock mutex;
          ("mutex", PyThread_type_lock),
#         struct _xidregitem *head;
          ("head", _c.POINTER(_xidregitem)),
#     } xidregistry;
)

# /* Full Python runtime state */
#
# /* _PyRuntimeState holds the global state for the CPython runtime.
#    That data is exposed in the internal API as a static variable (_PyRuntime).
#    */
pyruntimestate._fields_ = (
# typedef struct pyruntimestate {
#     /* Has been initialized to a safe state.
#
#        In order to be effective, this must be set to 0 during or right
#        after allocation. */
#     int _initialized;
      ("_initialized", _c.c_int),
#
#     /* Is running Py_PreInitialize()? */
#     int preinitializing;
      ("preinitializing", _c.c_int),
#
#     /* Is Python preinitialized? Set to 1 by Py_PreInitialize() */
#     int preinitialized;
      ("preinitialized", _c.c_int),
#
#     /* Is Python core initialized? Set to 1 by _Py_InitializeCore() */
#     int core_initialized;
      ("core_initialized", _c.c_int),
#
#     /* Is Python fully initialized? Set to 1 by Py_Initialize() */
#     int initialized;
      ("initialized", _c.c_int),
#
#     /* Set by Py_FinalizeEx(). Only reset to NULL if Py_Initialize()
#        is called again.
#
#        Use _PyRuntimeState_GetFinalizing() and _PyRuntimeState_SetFinalizing()
#        to access it, don't access it directly. */
#     _Py_atomic_address _finalizing;
      ("_finalizing", _Py_atomic_address),
#
#     struct pyinterpreters {
#         PyThread_type_lock mutex;
#         /* The linked list of interpreters, newest first. */
#         PyInterpreterState *head;
#         /* The runtime's initial interpreter, which has a special role
#            in the operation of the runtime.  It is also often the only
#            interpreter. */
#         PyInterpreterState *main;
#         /* _next_interp_id is an auto-numbered sequence of small
#            integers.  It gets initialized in _PyInterpreterState_Init(),
#            which is called in Py_Initialize(), and used in
#            PyInterpreterState_New().  A negative interpreter ID
#            indicates an error occurred.  The main interpreter will
#            always have an ID of 0.  Overflow results in a RuntimeError.
#            If that becomes a problem later then we can adjust, e.g. by
#            using a Python int. */
#         int64_t next_id;
#     } interpreters;
      ("interpreters", pyinterpreters),
#     // XXX Remove this field once we have a tp_* slot.
#     struct _xidregistry {
#         PyThread_type_lock mutex;
#         struct _xidregitem *head;
#     } xidregistry;
      ("xidregistry", _xidregistry),
#
#     unsigned long main_thread;
      ("main_thread", _c.c_ulong),
#
# #define NEXITFUNCS 32
#     void (*exitfuncs[NEXITFUNCS])(void);
      ("exitfuncs", _c.c_void_p * 32),
#     int nexitfuncs;
      ("nexitfuncs", _c.c_int),
#
#     struct _ceval_runtime_state ceval;
#     struct _gilstate_runtime_state gilstate;
#
#     PyPreConfig preconfig;
#
#     // Audit values must be preserved when Py_Initialize()/Py_Finalize()
#     // is called multiple times.
#     Py_OpenCodeHookFunction open_code_hook;
#     void *open_code_userdata;
#     _Py_AuditHookEntry *audit_hook_head;
#
#     struct _Py_unicode_runtime_ids unicode_ids;
#
#     /* All the objects that are shared by the runtime's interpreters. */
#     struct _Py_global_objects global_objects;
#
#     /* The following fields are here to avoid allocation during init.
#        The data is exposed through _PyRuntimeState pointer fields.
#        These fields should not be accessed directly outside of init.
#
#        All other _PyRuntimeState pointer fields are populated when
#        needed and default to NULL.
#
#        For now there are some exceptions to that rule, which require
#        allocation during init.  These will be addressed on a case-by-case
#        basis.  Most notably, we don't pre-allocated the several mutex
#        (PyThread_type_lock) fields, because on Windows we only ever get
#        a pointer type.
#        */
#
#     /* PyInterpreterState.interpreters.main */
#     PyInterpreterState _main_interpreter;
# } _PyRuntimeState;
)


def as_PyObject(obj: object) -> PyObject:
  if isinstance(obj, PyObject):
    return obj
  return PyObject.from_address(id(obj))

def as_PyTypeObject(obj: type) -> PyTypeObject:
  if isinstance(obj, PyTypeObject):
    return obj
  if not inspect.isclass(obj):
    raise TypeError("Expected type")
  return PyTypeObject.from_address(id(obj))

def typeof(obj: object) -> PyTypeObject:
  if isinstance(obj, PyTypeObject):
    return obj
  return as_PyObject(obj).ob_type.contents

# _c.sizeof(PyVarObject)
# PyObject.from_address(id(b'asdf')).ob_type.contents.tp_name


class Py_buffer(_c.Structure):
  _buf: int
  _obj: _c.py_object
  _len: int
  _itemsize: int
  _readonly: int
  _ndim: int
  _format: bytes
  _shape: c_ssize_p
  _strides: c_ssize_p
  _suboffsets: c_ssize_p
  _internal: int
  _closed: bool

  _fields_ = [
    ('_buf', _c.c_void_p),
    ('_obj', _c.py_object),
    ('_len', _c.c_ssize_t),
    ('_itemsize', _c.c_ssize_t),
    ('_readonly', _c.c_int),
    ('_ndim', _c.c_int),
    ('_format', _c.c_char_p),
    ('_shape', c_ssize_p),
    ('_strides', c_ssize_p),
    ('_suboffsets', c_ssize_p),
    ('_internal', _c.c_void_p)
  ]

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._closed = False

  @classmethod
  def new(cls, obj, *, writable=None, flags=None):
    if flags is not None and writable is not None:
      raise ValueError("Either writable or flags should be set, not both")
    if flags is None:
      flags = PyBUF_FULL if writable else PyBUF_FULL_RO
    self = PyObject_GetBuffer(obj, flags)
    if self is None:
      raise ValueError(f"Can't get buffer interface for object: {obj!r}")
    return self

  @property
  def closed(self):
    return self._closed

  def verify_open(self):
    if self.closed:
      raise RuntimeError("Py_buffer closed")

  def close(self, again=False):
    if not again:
      if self.closed:
        return
    PyBuffer_Release(self)
    self._closed = True

  def __del__(self):
    self.close()

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.close()

  @property
  def len(self) -> int:
    return self._len

  def __len__(self):
    return self.len

  @property
  def obj(self) -> _c.py_object:
    return self._obj

  @property
  def readonly(self) -> bool:
    return bool(self._readonly)

  @property
  def format(self) -> str:
    return 'B' if self._format is None else self._format.decode('utf-8')

  @property
  def shape(self) -> Tuple[int, ...]:
    return () if isnull(self._shape) else tuple(self._shape[0:self.ndim])

  @property
  def ndim(self) -> int:
    return self._ndim

  @property
  def numel(self) -> int:
    n = 1
    for x in self.shape:
      n *= x
    return n

  @property
  def strides(self) -> Tuple[int, ...]:
    return () if isnull(self._strides) else tuple(self._strides[0:self.ndim])

  @property
  def suboffsets(self) -> Tuple[int, ...]:
    return () if isnull(self._suboffsets) else tuple(self._suboffsets[0:self.ndim])

  @property
  def contiguous(self) -> Optional[str]:
    if PyBuffer_IsContiguous(self, 'C'):
      return 'C'
    elif PyBuffer_IsContiguous(self, 'F'):
      return 'F'

  @property
  def address(self) -> int:
    self.verify_open()
    return out_pointer(self._buf)

  def pointer(self, indices: Optional[Sequence[int]] = None) -> int:
    self.verify_open()
    return PyBuffer_GetPointer(self, indices)

  def get_contiguous_memory(self, *, writable: Optional[bool] = None, order: Literal['C', 'F'] = 'C') -> memoryview:
    self.verify_open()
    if writable is None:
      writable = not self.readonly
    if writable and self.readonly:
      raise ValueError("Requested writable contiguous buffer, but self.readonly is True")
    return PyMemoryView_GetContiguous(self.obj, PyBUF_WRITE if writable else PyBUF_READ, order)

  def get_contiguous_ndarray(self, *, writable: Optional[bool] = None, order: Literal['C', 'F'] = 'C'):
    import numpy as np
    mem = self.get_contiguous_memory(writable=writable, order=order)
    dtype = np.dtype(mem.format)
    return np.frombuffer(mem, dtype=dtype)


# typedef int (*getbufferproc)(PyObject *exporter, Py_buffer *view, int flags);
getbufferproc = _c.CFUNCTYPE(_c.c_bool, _c.py_object, _c.POINTER(Py_buffer), _c.c_int)
# typedef void (*releasebufferproc)(PyObject *exporter, Py_buffer *view);
releasebufferproc = _c.CFUNCTYPE(None, _c.py_object, _c.POINTER(Py_buffer))

# typedef struct {
#      getbufferproc bf_getbuffer;
#      releasebufferproc bf_releasebuffer;
# } PyBufferProcs;
PyBufferProcs._fields_ = (
  ("bf_getbuffer", getbufferproc),
  ("bf_releasebuffer", releasebufferproc),
)

def get_buffer(obj, *, writable=None, flags=None) -> Py_buffer:
  return Py_buffer.new(obj, writable=writable, flags=flags)

def get_pointer(obj, *, writable=None, flags=None):
  with get_buffer(obj) as buf:
    return buf.pointer()

CPointerType = type(_c.pointer(_c.c_int(0)))
CRefType = type(_c.byref(_c.c_int(0)))

def in_(x):
  if isinstance(x, CPointerType):
    return x
  return _c.pointer(x)

def out(x):
  if isinstance(x, CRefType):
    return x
  return _c.byref(x)

def out_pointer(x: Union[_c.c_void_p, int]) -> int:
  if isinstance(x, _c.c_void_p):
    return x.value or 0
  elif isinstance(x, int):
    return x
  else:
    raise TypeError(f"out_pointer({x!r})")

def in_indices(shape, indices):
  ndim = len(shape)
  out = (_c.c_ssize_t * ndim)()
  if indices is not None:
    out[:] = indices
    for i in range(ndim):
      if indices[i] < 0 or indices[i] > shape[i]:
        raise ValueError(f"Bad index [{i}]: {indices[i]} in indices array. shape: {shape} indices: {indices}")
  return out

def in_order(order: str = 'C') -> _c.c_char:
  if order not in ['C', 'F']:
    raise TypeError(f"Expected order to be 'C' or 'F', got {order!r}")
  return _c.c_char(ord(order))

def in_buffertype(buffertype: int) -> int:
  if buffertype not in [PyBUF_READ, PyBUF_WRITE]:
    raise TypeError(f"PyMemoryView_GetContiguous: Expected buffertype of PyBUF_READ or PyBUF_WRITE, got {buffertype}")
  return buffertype

# def in_object(x) -> _c.POINTER(_c.py_object):
#   if isinstance(x, _c.py_object):
#     return in_(x)
#   return in_(_c.py_object(x))

def in_object(x) -> _c.py_object:
  if isinstance(x, _c.py_object):
    return x
  return _c.py_object(x)

def in_buffer(x: Py_buffer):
  if not isinstance(x, Py_buffer):
    raise TypeError(f"Expected Py_buffer, got {x}")
  return x

def out_buffer(x: Py_buffer):
  if not isinstance(x, Py_buffer):
    raise TypeError(f"Expected Py_buffer, got {x}")
  return out(x)

Py_buffer_p = _c.POINTER(Py_buffer)
py_object_p = _c.POINTER(_c.py_object)
in_py_object = _c.py_object
in_py_buffer = Py_buffer
out_py_buffer = _c.POINTER(Py_buffer)

# https://docs.python.org/3/c-api/buffer.html#c.PyObject_GetBuffer
# int PyObject_GetBuffer(PyObject *exporter, Py_buffer *view, int flags)
capi_PyObject_GetBuffer = _c.pythonapi.PyObject_GetBuffer
capi_PyObject_GetBuffer.restype = _c.c_int
capi_PyObject_GetBuffer.argtypes = [in_py_object, out_py_buffer, _c.c_int]

def PyObject_GetBuffer(exporter: object, flags: int = PyBUF_FULL) -> Py_buffer:
  view = Py_buffer()
  res = capi_PyObject_GetBuffer(in_object(exporter), out_buffer(view), flags)
  if res == 0:
    return view
  else:
    del view

# https://docs.python.org/3/c-api/buffer.html#c.PyBuffer_Release
# void PyBuffer_Release(Py_buffer *view)
capi_PyBuffer_Release = _c.pythonapi.PyBuffer_Release
capi_PyBuffer_Release.restype = None
capi_PyBuffer_Release.argtypes = [out_py_buffer]

def PyBuffer_Release(view: Py_buffer):
  capi_PyBuffer_Release(out_buffer(view))

# https://docs.python.org/3/c-api/buffer.html#c.PyBuffer_GetPointer
# void *PyBuffer_GetPointer(Py_buffer *view, Py_ssize_t *indices)
capi_PyBuffer_GetPointer = _c.pythonapi.PyBuffer_GetPointer
capi_PyBuffer_GetPointer.restype = _c.c_void_p
capi_PyBuffer_GetPointer.argtypes = [out_py_buffer, c_ssize_p]

def PyBuffer_GetPointer(view: Py_buffer, indices: Optional[Sequence[int]] = None) -> int:
  indices_p = in_indices(view.shape, indices)
  res = capi_PyBuffer_GetPointer(out_buffer(view), indices_p)
  del indices_p
  return out_pointer(res)

# https://docs.python.org/3/c-api/buffer.html#c.PyBuffer_IsContiguous
# int PyBuffer_IsContiguous(Py_buffer *view, char order)
capi_PyBuffer_IsContiguous = _c.pythonapi.PyBuffer_IsContiguous
capi_PyBuffer_IsContiguous.restype = _c.c_bool
capi_PyBuffer_IsContiguous.argtypes = [out_py_buffer, _c.c_char]

def PyBuffer_IsContiguous(view: Py_buffer, order: Literal['C', 'F'] = 'C') -> bool:
  return capi_PyBuffer_IsContiguous(out_buffer(view), in_order(order))

try:
  # https://docs.python.org/3/c-api/buffer.html#c.PyObject_CheckBuffer
  # int PyObject_CheckBuffer(PyObject *obj)
  capi_PyObject_CheckBuffer = _c.pythonapi.PyObject_CheckBuffer
  capi_PyObject_CheckBuffer.restype = _c.c_bool
  capi_PyObject_CheckBuffer.argtypes = [in_py_object]
except AttributeError:
  capi_PyObject_CheckBuffer = None

def PyObject_CheckBuffer(obj: object) -> bool:
  if capi_PyObject_CheckBuffer is None:
    try:
      buf = PyObject_GetBuffer(obj, PyBUF_FULL_RO)
      PyBuffer_Release(buf)
      return True
    except TypeError:
      return False
  else:
    return capi_PyObject_CheckBuffer(in_object(obj))

# https://docs.python.org/3/c-api/memoryview.html#c.PyMemoryView_GetContiguous
# PyObject *PyMemoryView_GetContiguous(PyObject *obj, int buffertype, char order)
capi_PyMemoryView_GetContiguous = _c.pythonapi.PyMemoryView_GetContiguous
capi_PyMemoryView_GetContiguous.restype = _c.py_object
capi_PyMemoryView_GetContiguous.argtypes = [in_py_object, _c.c_int, _c.c_char]

def PyMemoryView_GetContiguous(obj, buffertype=PyBUF_READ, order: Literal['C', 'F'] = 'C'):
  return capi_PyMemoryView_GetContiguous(in_object(obj), in_buffertype(buffertype), in_order(order))

#PyInterpreterState *PyInterpreterState_Get(void)
capi_PyInterpreterState_Get = _c.pythonapi.PyInterpreterState_Get
capi_PyInterpreterState_Get.restype = _c.POINTER(PyInterpreterState)
capi_PyInterpreterState_Get.argtypes = []
def PyInterpreterState_Get():
  return capi_PyInterpreterState_Get()

# PyThreadState *PyThreadState_Get()
capi_PyThreadState_Get = _c.pythonapi.PyThreadState_Get
capi_PyThreadState_Get.restype = _c.POINTER(PyThreadState)
capi_PyThreadState_Get.argtypes = []
def PyThreadState_Get():
  return capi_PyThreadState_Get()

# PyObject *PyThreadState_GetDict(void)
capi_PyThreadState_GetDict = _c.pythonapi.PyThreadState_GetDict
capi_PyThreadState_GetDict.restype = _c.c_void_p
capi_PyThreadState_GetDict.argtypes = []
def PyThreadState_GetDict():
  return asobj(capi_PyThreadState_GetDict())



# PyAPI_FUNC(PyThreadState *) _PyThreadState_Prealloc(PyInterpreterState *);
#
# /* Similar to PyThreadState_Get(), but don't issue a fatal error
#  * if it is NULL. */
# PyAPI_FUNC(PyThreadState *) _PyThreadState_UncheckedGet(void);
#
# PyAPI_FUNC(PyObject *) _PyThreadState_GetDict(PyThreadState *tstate);
#
# /* PyGILState */
#
# /* Helper/diagnostic function - return 1 if the current thread
#    currently holds the GIL, 0 otherwise.
#
#    The function returns 1 if _PyGILState_check_enabled is non-zero. */
# PyAPI_FUNC(int) PyGILState_Check(void);
#
# /* Get the single PyInterpreterState used by this process' GILState
#    implementation.
#
#    This function doesn't check for error. Return NULL before _PyGILState_Init()
#    is called and after _PyGILState_Fini() is called.
#
#    See also _PyInterpreterState_Get() and _PyInterpreterState_GET(). */
# PyAPI_FUNC(PyInterpreterState *) _PyGILState_GetInterpreterStateUnsafe(void);
#
# /* The implementation of sys._current_frames()  Returns a dict mapping
#    thread id to that thread's current frame.
# */
# PyAPI_FUNC(PyObject *) _PyThread_CurrentFrames(void);
#
# /* Routines for advanced debuggers, requested by David Beazley.
#    Don't use unless you know what you are doing! */

# PyAPI_FUNC(PyInterpreterState *) PyInterpreterState_Main(void);
capi_PyInterpreterState_Main = _c.pythonapi.PyInterpreterState_Main
capi_PyInterpreterState_Main.restype = _c.POINTER(PyInterpreterState)
capi_PyInterpreterState_Main.argtypes = []
def PyInterpreterState_Main():
  return capi_PyInterpreterState_Main()

# PyAPI_FUNC(PyInterpreterState *) PyInterpreterState_Head(void);
capi_PyInterpreterState_Head = _c.pythonapi.PyInterpreterState_Head
capi_PyInterpreterState_Head.restype = _c.POINTER(PyInterpreterState)
capi_PyInterpreterState_Head.argtypes = []
def PyInterpreterState_Head():
  return capi_PyInterpreterState_Head()

# PyAPI_FUNC(PyInterpreterState *) PyInterpreterState_Next(PyInterpreterState *);
capi_PyInterpreterState_Next = _c.pythonapi.PyInterpreterState_Next
capi_PyInterpreterState_Next.restype = _c.POINTER(PyInterpreterState)
capi_PyInterpreterState_Next.argtypes = [_c.POINTER(PyInterpreterState)]
def PyInterpreterState_Next(state):
  if state:
    return capi_PyInterpreterState_Next(state)

# PyAPI_FUNC(PyThreadState *) PyInterpreterState_ThreadHead(PyInterpreterState *);
capi_PyInterpreterState_ThreadHead = _c.pythonapi.PyInterpreterState_ThreadHead
capi_PyInterpreterState_ThreadHead.restype = _c.POINTER(PyThreadState)
capi_PyInterpreterState_ThreadHead.argtypes = [_c.POINTER(PyInterpreterState)]
def PyInterpreterState_ThreadHead(state):
  if state:
    return capi_PyInterpreterState_ThreadHead(state)

# PyAPI_FUNC(PyThreadState *) PyThreadState_Next(PyThreadState *);
capi_PyThreadState_Next = _c.pythonapi.PyThreadState_Next
capi_PyThreadState_Next.restype = _c.POINTER(PyThreadState)
capi_PyThreadState_Next.argtypes = [_c.POINTER(PyThreadState)]
def PyThreadState_Next(tstate):
  if tstate:
    return capi_PyThreadState_Next(tstate)

# PyAPI_FUNC(void) PyThreadState_DeleteCurrent(void);



# /* Frame evaluation API */
#
# typedef PyObject* (*_PyFrameEvalFunction)(PyThreadState *tstate, PyFrameObject *, int);
#
# PyAPI_FUNC(_PyFrameEvalFunction) _PyInterpreterState_GetEvalFrameFunc(
#     PyInterpreterState *interp);
# PyAPI_FUNC(void) _PyInterpreterState_SetEvalFrameFunc(
#     PyInterpreterState *interp,
#     _PyFrameEvalFunction eval_frame);
#
# PyAPI_FUNC(const PyConfig*) _PyInterpreterState_GetConfig(PyInterpreterState *interp);
#
# // Get the configuration of the currrent interpreter.
# // The caller must hold the GIL.
# PyAPI_FUNC(const PyConfig*) _Py_GetConfig(void);


# PyThreadState *
# PyGILState_GetThisThreadState(void)
# {
#     return _PyGILState_GetThisThreadState(&_PyRuntime.gilstate);
# }
capi_PyGILState_GetThisThreadState = _c.pythonapi.PyGILState_GetThisThreadState
capi_PyGILState_GetThisThreadState.restype = _c.POINTER(PyThreadState)
capi_PyGILState_GetThisThreadState.argtypes = []
def PyGILState_GetThisThreadState():
    return capi_PyGILState_GetThisThreadState()

_PyRuntime = pyruntimestate.in_dll(_c.pythonapi, "_PyRuntime")

class PyConfig(_c.Structure):
  pass


# https://stackoverflow.com/questions/7015487/ctypes-variable-length-structures
import copy

class StructureVariableSized(_c.Structure):
    _variable_sized_ = []

    def __new__(self, variable_sized=(), **kwargs):
        def name_builder(name, variable_sized):
            for variable_sized_field_name, variable_size in variable_sized:
                name += variable_sized_field_name.title() + '[{0}]'.format(variable_size)
            return name

        local_fields = copy.deepcopy(self._fields_)
        for matching_field_name, matching_type in self._variable_sized_:
            match_type = None
            for variable_sized_field_name, variable_size in variable_sized:
                if variable_sized_field_name == matching_field_name:
                    match_type = matching_type
                    break
            if match_type is None:
                raise Exception
            local_fields.append((variable_sized_field_name, match_type*variable_size))
        name = name_builder(self.__name__, variable_sized)
        class BaseCtypesStruct(_c.Structure):
            _fields_ = local_fields
            _variable_sized_ = self._variable_sized_
        classdef = BaseCtypesStruct
        classdef.__name__ = name
        return BaseCtypesStruct(**kwargs)


# typedef struct {
#     /* If length is greater than zero, items must be non-NULL
#        and all items strings must be non-NULL */
#     Py_ssize_t length;
#     wchar_t **items;
# } PyWideStringList;

class PyWideStringList(_c.Structure):
  _fields_ = [
    ("length", _c.c_ssize_t),
    ("items", _c.POINTER(_c.c_wchar_p)),
    ]
  def __len__(self):
    return self.length
  def __getitem__(self, i):
    if i < 0 or i >= len(self):
      raise IndexError(i)
    return self.items[i]

# class PyWideStringList(_c.Structure):
#   _fields_ = [
#     ("items", _c.POINTER(_c.c_wchar_p))
#     ]
#   def __len__(self):
#     n = 0
#     if self.items:
#       pp = self.items
#       if pp[n]:
#         n += 1
#     return n
#   def __getitem__(self, i):
#     if i < 0 or i >= len(self):
#       raise IndexError(i)
#     return self.items[i]

PyConfig._fields_ = [
# /* This structure is best documented in the Doc/c-api/init_config.rst file. */
# typedef struct PyConfig {
#     int _config_init;     /* _PyConfigInitEnum value */
  ("_config_init", _c.c_int),
#
#     int isolated;
  ("isolated", _c.c_int),
#     int use_environment;
  ("use_environment", _c.c_int),
#     int dev_mode;
  ("dev_mode", _c.c_int),
#     int install_signal_handlers;
  ("install_signal_handlers", _c.c_int),
#     int use_hash_seed;
  ("use_hash_seed", _c.c_int),
#     unsigned long hash_seed;
  ("hash_seed", _c.c_ulong),
#     int faulthandler;
  ("faulthandler", _c.c_int),

  #     /* Enable PEG parser?
  #        1 by default, set to 0 by -X oldparser and PYTHONOLDPARSER */
  #     int _use_peg_parser;
  ("_use_peg_parser", _c.c_int),

#     int tracemalloc;
  ("tracemalloc", _c.c_int),
#     int import_time;
  ("import_time", _c.c_int),
#     int code_debug_ranges;
#   ("code_debug_ranges", _c.c_int),
# #     int show_ref_count;
  ("show_ref_count", _c.c_int),
#     int dump_refs;
  ("dump_refs", _c.c_int),
# #     wchar_t *dump_refs_file;
#   ("dump_refs_file", _c.c_wchar_p),
#     int malloc_stats;
  ("malloc_stats", _c.c_int),
#     wchar_t *filesystem_encoding;
  ("filesystem_encoding", _c.c_wchar_p),
#     wchar_t *filesystem_errors;
  ("filesystem_errors", _c.c_wchar_p),
#     wchar_t *pycache_prefix;
  ("pycache_prefix", _c.c_wchar_p),
#     int parse_argv;
  ("parse_argv", _c.c_int),
# #     PyWideStringList orig_argv;
#   ("orig_argv", PyWideStringList),
#     PyWideStringList argv;
  ("argv", PyWideStringList),

#     /* Program name:
  #
  #        - If Py_SetProgramName() was called, use its value.
  #        - On macOS, use PYTHONEXECUTABLE environment variable if set.
  #        - If WITH_NEXT_FRAMEWORK macro is defined, use __PYVENV_LAUNCHER__
  #          environment variable is set.
  #        - Use argv[0] if available and non-empty.
  #        - Use "python" on Windows, or "python3 on other platforms. */
  #     wchar_t *program_name;
  ("program_name", _c.c_wchar_p),

#     PyWideStringList xoptions;
  ("xoptions", PyWideStringList),
#     PyWideStringList warnoptions;
  ("warnoptions", PyWideStringList),
#     int site_import;
  ("site_import", _c.c_int),
#     int bytes_warning;
  ("bytes_warning", _c.c_int),
# #     int warn_default_encoding;
#   ("warn_default_encoding", _c.c_int),
#     int inspect;
  ("inspect", _c.c_int),
#     int interactive;
  ("interactive", _c.c_int),
#     int optimization_level;
  ("optimization_level", _c.c_int),
#     int parser_debug;
  ("parser_debug", _c.c_int),
#     int write_bytecode;
  ("write_bytecode", _c.c_int),
#     int verbose;
  ("verbose", _c.c_int),
#     int quiet;
  ("quiet", _c.c_int),
#     int user_site_directory;
  ("user_site_directory", _c.c_int),
#     int configure_c_stdio;
  ("configure_c_stdio", _c.c_int),
#     int buffered_stdio;
  ("buffered_stdio", _c.c_int),
#     wchar_t *stdio_encoding;
  ("stdio_encoding", _c.c_wchar_p),
#     wchar_t *stdio_errors;
  ("stdio_errors", _c.c_wchar_p),
# # #ifdef MS_WINDOWS
# #     int legacy_windows_stdio;
#   ("legacy_windows_stdio", _c.c_int),
# # #endif
#     wchar_t *check_hash_pycs_mode;
  ("check_hash_pycs_mode", _c.c_wchar_p),
# #     int use_frozen_modules;
#   ("use_frozen_modules", _c.c_int),
# #     int safe_path;
#   ("safe_path", _c.c_int),
#
#     /* --- Path configuration inputs ------------ */
#     int pathconfig_warnings;
  ("pathconfig_warnings", _c.c_int),
# #     wchar_t *program_name;
#   ("program_name", _c.c_wchar_p),
#     wchar_t *pythonpath_env;
  ("pythonpath_env", _c.c_wchar_p),
#     wchar_t *home;
  ("home", _c.c_wchar_p),
#
#     /* --- Path configuration outputs ----------- */
#     int module_search_paths_set;
  ("module_search_paths_set", _c.c_int),
#     PyWideStringList module_search_paths;
  ("module_search_paths", PyWideStringList),
# #     wchar_t *stdlib_dir;
#   ("stdlib_dir", _c.c_wchar_p),
#     wchar_t *executable;
  ("executable", _c.c_wchar_p),
#     wchar_t *base_executable;
  ("base_executable", _c.c_wchar_p),
#     wchar_t *prefix;
  ("prefix", _c.c_wchar_p),
#     wchar_t *base_prefix;
  ("base_prefix", _c.c_wchar_p),
#     wchar_t *exec_prefix;
  ("exec_prefix", _c.c_wchar_p),
#     wchar_t *base_exec_prefix;
  ("base_exec_prefix", _c.c_wchar_p),
  #     wchar_t *platlibdir;
  ("platlibdir", _c.c_wchar_p),
#
#     /* --- Parameter only used by Py_Main() ---------- */
#     int skip_source_first_line;
  ("skip_source_first_line", _c.c_int),
#     wchar_t *run_command;
  ("run_command", _c.c_wchar_p),
#     wchar_t *run_module;
  ("run_module", _c.c_wchar_p),
#     wchar_t *run_filename;
  ("run_filename", _c.c_wchar_p),
#
#     /* --- Private fields ---------------------------- */
#
#     // Install importlib? If equals to 0, importlib is not initialized at all.
#     // Needed by freeze_importlib.
#     int _install_importlib;
  ("_install_importlib", _c.c_int),
#
#     // If equal to 0, stop Python initialization before the "main" phase.
#     int _init_main;
  ("_init_main", _c.c_int),
#
#     // If non-zero, disallow threads, subprocesses, and fork.
#     // Default: 0.
#     int _isolated_interpreter;
  ("_isolated_interpreter", _c.c_int),
#
# #     // If non-zero, we believe we're running from a source tree.
# #     int _is_python_build;
#   ("_is_python_build", _c.c_int),
  ("_orig_argv", PyWideStringList),
# } PyConfig;
]

pycapi__PyInterpreterState_GetConfig = _c.pythonapi._PyInterpreterState_GetConfig
pycapi__PyInterpreterState_GetConfig.argtypes = [_c.POINTER(PyInterpreterState)]
pycapi__PyInterpreterState_GetConfig.restype = _c.POINTER(PyConfig)

def PyInterpreterState_GetConfig(state):
  if state:
    return pycapi__PyInterpreterState_GetConfig(state)


# /* Get the original command line arguments, before Python modified them.
#
#    See also PyConfig.orig_argv. */
# PyAPI_FUNC(void) Py_GetArgcArgv(int *argc, wchar_t ***argv);
pycapi_Py_GetArgcArgv = _c.pythonapi.Py_GetArgcArgv
pycapi_Py_GetArgcArgv.argtypes = [_c.POINTER(_c.c_int), _c.POINTER(_c.POINTER(_c.c_wchar_p))]
pycapi_Py_GetArgcArgv.restype = None
def Py_GetArgcArgv():
  argc = _c.c_int()
  argv = _c.POINTER(_c.c_wchar_p)()
  pycapi_Py_GetArgcArgv(out(argc), out(argv))
  return tuple((_c.c_wchar_p * max(argc.value, 0)).from_address(asvoidp(argv).value))



