"""
Scheme Interpreter in CircuitPython
Based on Lispy.py (c) Peter Norvig, 2010; See http://norvig.com/lispy2.html

Adafruit invests time and resources providing this open source code.
Please support Adafruit and open source hardware by purchasing
products from Adafruit!

Written by Dave Astels for Adafruit Industries
Copyright (c) 2019 Adafruit Industries
Licensed under the MIT license.

All text above must be included in any redistribution.
"""

# Initially we'll avoid all pylint's complaints.
# Over time we'll bring it in line.

# pylint: disable=wrong-import-order,no-member,missing-docstring,invalid-name
# pylint: disable=redefined-builtin,multiple-statements,too-many-branches
# pylint: disable=too-many-return-statements,no-else-return,bad-whitespace
# pylint: disable=superfluous-parens,exec-used,wrong-import-position
# pylint: disable=unnecessary-lambda,multiple-imports
# pylint: disable=misplaced-comparison-constant,too-few-public-methods
# pylint: disable=dangerous-default-value,unnecessary-semicolon
# pylint: disable=broad-except,bad-continuation

################ Symbol, Procedure, classes

import ure, sys
from io import StringIO
import gc


class Symbol(str): pass

def Sym(s, symbol_table={}):
    "Find or create unique Symbol entry for str s in symbol table."
    if s not in symbol_table: symbol_table[s] = Symbol(s)
    return symbol_table[s]

_quote, _if, _cond, _set, _define, _lambda, _begin, _definemacro, = map(Sym,
"quote   if   cond   set!  define   lambda   begin   define-macro".split())

_quasiquote, _unquote, _unquotesplicing = map(Sym,
"quasiquote   unquote   unquote-splicing".split())

class Procedure(object):
    "A user-defined Scheme procedure."
    def __init__(self, parms, exp, env):
        self.parms, self.exp, self.env = parms, exp, env
    def __call__(self, *args):
        return eval(self.exp, Env(self.parms, args, self.env))

################ parse, read, and user interaction

def parse(inport):
    "Parse a program: read and expand/error-check it."
    # Backwards compatibility: given a str, convert it to an InPort
    if isinstance(inport, str): inport = InPort(StringIO(inport))
    return expand(read(inport), toplevel=True)

eof_object = Symbol('#<eof-object>') # Note: uninterned; can't be read

class InPort(object):
    "An input port. Retains a line of chars."
    # tokenizer = r"""\s*(,@|[('`,)]|"(?:[\\].|[^\\"])*"|;.*|[^\s('"`,;)]*)(.*)"""
    tokenizer = r"""[ ]*(,@|[('`,)]|"(?:[\\].|[^\\"])*"|;.*|[^ ('"`,;)]*)(.*)"""
    def __init__(self, afile):
        self._file = afile; self.line = ''
    def next_token(self):
        "Return the next token, reading new text into line buffer if needed."
        while True:
            if self.line == '': self.line = self._file.readline()
            if self.line == '': return eof_object
            self.line = self.line.strip()
            m = ure.match(InPort.tokenizer, self.line)
            token = m.group(1)
            self.line = m.group(2)
            if token != '' and not token.startswith(';'):
                return token

def readchar(inport):
    "Read the next character from an input port."
    if inport.line != '':
        ch, inport.line = inport.line[0], inport.line[1:]
        return ch
    else:
        return inport.file.read(1) or eof_object

def read(inport):
    "Read a Scheme expression from an input port."
    def read_ahead(token):
        if '(' == token:
            L = []
            while True:
                token = inport.next_token()
                if token == ')':
                    return L
                else: L.append(read_ahead(token))
        elif ')' == token: raise SyntaxError('unexpected )')
        elif token in quotes: return [quotes[token], read(inport)]
        elif token is eof_object: raise SyntaxError('unexpected EOF in list')
        else: return atom(token)
    # body of read:
    token1 = inport.next_token()
    return eof_object if token1 is eof_object else read_ahead(token1)

quotes = {"'":_quote, "`":_quasiquote, ",":_unquote, ",@":_unquotesplicing}

def atom(token):
    'Numbers become numbers; #t and #f are booleans; "..." string; otherwise Symbol.'
    if token == '#t': return True
    elif token == '#f': return False
    elif token[0] == '"': return token[1:-1]#.decode('string_escape')
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return Sym(token)

def to_string(x):
    "Convert a Python object back into a Lisp-readable string."
    if x is True: return "#t"
    elif x is False: return "#f"
    elif isa(x, Symbol): return str(x)
#    elif isa(x, str): return '"%s"' % x.encode('string_escape').replace('"',r'\"')
    elif isa(x, str): return '"%s"' % x.replace('"',r'\"')
    elif isa(x, list):
        return '('+' '.join(map(to_string, x))+')'
    else: return str(x)

def load(filename):
    "Eval every expression from a file."
    if not filename.endswith('.scm'):
        filename = filename + '.scm'
    inport = InPort(open(filename))
    while True:
        try:
            x = parse(inport)
            if x is eof_object: return
            eval(x)
        except Exception as e:
            sys.print_exception(e)

############ REPL history support

history_max_size = 40
history = []

def load_history():
    with open('history.txt', 'r') as f:
        history = f.readlines()

def save_history():
    with open('history.txt', 'w'):
        for line in history[:history_max_size]:
            f.write('{0}\n'.format(line))

def add_to_history(line):
    if not history or history[0] != line:
        history.insert(0, line.strip())

def get_history(offset):
    if offset < 0 or offset >= len(history):
        return ''
    return history[offset]

def repl():
    "A prompt-read-eval-print loop."
    input = ''
    line = ''
    index = 0
    ctrl_c_seen = False

    while True:                         # for each command
        try:
            if input:
                prompt = '... '
            else:
                prompt = '==> '
            sys.stdout.write(prompt)
            index = 0
            line = ''
            history_offset = -1

            while True:                   # for each character
                ch = ord(sys.stdin.read(1))

                # if ch == 3:               # CTRL-C
                #     print('ctrl-c from ch == 3')
                #     if ctrl_c_seen:
                #         return
                #     ctrl_c_seen = True
                #     input = ''
                #     sys.stdout.write('\n')
                #     break

                ctrl_c_seen = False

                if 32 <= ch <= 126:           # printable character
                    line = line[:index] + chr(ch) + line[index:]
                    index += 1

                elif ch in {10, 13}:          # EOL - try to process
                    if input:
                        input = input + ' ' + line.strip()
                    else:
                        input = line.strip()
                    add_to_history(line.strip())
                    line = ''
                    try:
                        x = parse(input)
                        if x is eof_object:
                            raise SyntaxError('unexpected EOF in list')
                        val = eval(x)
                        if val is not None:
                            sys.stdout.write('\x1b[0G\x1b[{0}C\n'.format(index + len(prompt)))
                            sys.stdout.write(to_string(val))
                        input = ''
                    except SyntaxError as e:
                        if str(e) != 'unexpected EOF in list':
                            sys.stdout.write('\n')
                            sys.stdout.write(str(e))
                            input = ''
                    sys.stdout.write('\n')
                    break

                #####################

                elif ch == 1:             # CTRL-A: start of line
                    index = 0

                elif ch == 5:             # CTRL-E: end of line
                    index = len(line)

                #####################

                elif ch == 2:             # CTRL-B: back a word
                    while index > 0 and line[index-1] == ' ':
                        index -= 1
                    while index > 0 and line[index-1] != ' ':
                        index -= 1

                elif ch == 6:             # CTRL-F: forward a word
                    while index < len(line) and line[index] == ' ':
                        index += 1
                    while index < len(line) and line[index] != ' ':
                        index += 1

                #####################

                elif ch == 4:             # CTRL-D: delete forward
                    if index < len(line):
                        line = line[:index] + line[index+1:]

                elif ch == 11:            # CTRL-K: clear to end of line
                    line = line[:index]

                elif ch in {08, 127}:     # backspace/DEL
                    if index > 0:
                        line = line[:index - 1] + line[index:]
                        index -= 1

                #####################

                elif ch == 19:            # CTRL-S: save history
                    save_history()

                #####################

                elif ch == 27:            # ESC
                    next1, next2 = ord(sys.stdin.read(1)), ord(sys.stdin.read(1))
                    if next1 == 91:           # [
                        if next2 == 68:       # left arrow
                            if index > 0:
                                index -= 1
                            else:
                                sys.stdout.write('\x07')
                        elif next2 == 67:     # right arrow
                            if index < len(line):
                                index += 1
                            else:
                                sys.stdout.write('\x07')
                        elif next2 == 66:     # down arrow
                            if history_offset > -1:
                                history_offset -= 1
                                line = get_history(history_offset)
                                index = len(line)
                            else:
                                sys.stdout.write('\x07')
                        elif next2 == 65:     # up arrow
                            if history_offset < len(history) - 1:
                                history_offset += 1
                                line = get_history(history_offset)
                                index = len(line)
                            else:
                                sys.stdout.write('\x07')

                else:
                    print('Unknown character: {0}'.format(ch))

                # Update screen
                sys.stdout.write("\x1b[1000D") # Move all the way left
                sys.stdout.write("\x1b[0K")    # Clear the line
                sys.stdout.write(prompt)
                sys.stdout.write(line)
                sys.stdout.write("\x1b[1000D") # Move all the way left again
                sys.stdout.write("\x1b[{0}C".format(len(prompt) + index)) # Move cursor too index
                # sys.stdout.flush()
        except KeyboardInterrupt:
            print('ctrl-c from KeyboardInterrupt')
            if ctrl_c_seen:
                return
            ctrl_c_seen = True
            input = ''
            sys.stdout.write('\n')
        except Exception as e:
            sys.stdout.write('\n')
            sys.print_exception(e)
            sys.stdout.write('\n')
            input = ''

################ Environment class

class Env(object):
    "An environment: a dict of {'var':val} pairs, with an outer Env."
    def __init__(self, parms=(), args=(), outer=None):
        # Bind parm list to corresponding args, or single parm to list of args
        self.storage = {}
        self.outer = outer
        if isa(parms, Symbol):
            self.storage.update({str(parms):list(args)})
        else:
            if len(args) != len(parms):
                raise TypeError('expected %s, given %s, '
                                % (to_string(parms), to_string(args)))
            try:
                self.storage.update(zip([str(p) for p in parms],args))
            except TypeError as e:
                sys.print_exception(e)
    def find(self, var):
        "Find the innermost Env where var appears."
        if str(var) in self.storage: return self
        elif self.outer is None:
            raise LookupError(str(var))
        else: return self.outer.find(var)

def is_pair(x): return x != [] and isa(x, list)
def cons(x, y): return [x]+y

def callcc(proc):
    "Call proc with current continuation; escape only"
    ball = RuntimeWarning("Sorry, can't continue this continuation any longer.")
    def throw(retval): ball.retval = retval; raise ball
    try:
        return proc(throw)
    except RuntimeWarning as w:
        if w is ball: return ball.retval
        else: raise w

def mod_vars(mod):
    names = [i for i in dir(mod) if i[0] != '_']
    values = [getattr(mod, i) for i in names]
    return dict(zip(names, values))

def add_globals(self):
    "Add some Scheme standard procedures."
    import math, operator as op
    self.storage.update(mod_vars(math))
    # self.update(mod_vars(cmath))
    self.storage.update({
        '+':op.add, '-':op.sub, '*':op.mul, '/':op.truediv, 'not':op.not_,
        '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq,
        'equal?':op.eq, 'eq?':op.is_, 'length':len, 'cons':cons,
        'car':lambda x:x[0], 'cdr':lambda x:x[1:], 'append':op.add,
        'list':lambda *x:list(x), 'list?': lambda x:isa(x,list),
        'null?':lambda x:x==[], 'symbol?':lambda x: isa(x, Symbol),
        'boolean?':lambda x: isa(x, bool), 'pair?':is_pair,
        'port?': lambda x:isa(x,file), 'apply':lambda proc,l: proc(*l),
        'eval':lambda x: eval(expand(x)), 'load':lambda fn: load(fn), 'call/cc':callcc,
        'open-input-file':open,'close-input-port':lambda p: p.file.close(),
        'open-output-file':lambda f:open(f,'w'), 'close-output-port':lambda p: p.close(),
        'eof-object?':lambda x:x is eof_object, 'read-char':readchar,
        'read':read, 'write':lambda x,port=sys.stdout:port.write(to_string(x)),
        'display':lambda x,port=sys.stdout:port.write(x if isa(x,str) else to_string(x)),
        'newline':lambda port=sys.stdout:port.write("\n")})
    return self

isa = isinstance

global_env = add_globals(Env())

################ eval (tail recursive)

def eval(x, env=global_env):
    "Evaluate an expression in an environment."
    while True:
        if isa(x, Symbol):       # variable reference
            return env.find(str(x)).storage[str(x)]
        elif not isa(x, list):   # constant literal
            return x
        elif x[0] is _quote:     # (quote exp)
            (_, exp) = x
            return exp
        elif x[0] is _if:        # (if test conseq alt)
            (_, test, conseq, alt) = x
            x = (conseq if eval(test, env) else alt)
        elif x[0] is _cond:      # (cond (test code)...)
            for clause in x[1:]:
                if eval(clause[0], env):
                    for exp in clause[1:-1]:
                        eval(exp, env)
                    x = clause[-1]
                    break
        elif x[0] is _set:       # (set! var exp)
            (_, var, exp) = x
            env.find(var).storage[str(var)] = eval(exp, env)
            return None
        elif x[0] is _define:    # (define var exp)
            (_, var, exp) = x
            env.storage[str(var)] = eval(exp, env)
            return None
        elif x[0] is _lambda:    # (lambda (var*) exp)
            (_, vars, exp) = x
            return Procedure(vars, exp, env)
        elif x[0] is _begin:     # (begin exp+)
            for exp in x[1:-1]:
                eval(exp, env)
            x = x[-1]
        else:                    # (proc exp*)
            exps = [eval(exp, env) for exp in x]
            proc = exps.pop(0)
            if isa(proc, Procedure):
                x = proc.exp
                env = Env(proc.parms, exps, proc.env)
            else:
                return proc(*exps)

################ expand

def expand(x, toplevel=False):
    "Walk tree of x, making optimizations/fixes, and signaling SyntaxError."
    require(x, x!=[], "Empty list can't be expanded")                    # () => Error
    if not isa(x, list):                 # constant => unchanged
        return x
    elif x[0] is _quote:                 # (quote exp)
        require(x, len(x)==2)
        return x
    elif x[0] is _if:
        if len(x)==3: x = x + [None]     # (if t c) => (if t c None)
        require(x, len(x)==4)
        return list(map(expand, x))
    elif x[0] is _cond:
        require(x, len(x) > 1)
        for clause in x[1:]:
            require (clause, len(clause) >= 2)
        return list(map(expand, x))
    elif x[0] is _set:
        require(x, len(x)==3);
        var = x[1]                       # (set! non-var exp) => Error
        require(x, isa(var, Symbol), "can set! only a symbol")
        return [_set, var, expand(x[2])]
    elif x[0] is _define or x[0] is _definemacro:
        require(x, len(x)>=3)
        _def, v, body = x[0], x[1], x[2:]
        if isa(v, list) and v:           # (define (f args) body)
            f, args = v[0], v[1:]        #  => (define f (lambda (args) body))
            return expand([_def, f, [_lambda, args]+body])
        else:
            require(x, len(x)==3)        # (define non-var/list exp) => Error
            require(x, isa(v, Symbol), "can define only a symbol")
            exp = expand(x[2])
            if _def is _definemacro:
                require(x, toplevel, "define-macro only allowed at top level")
                proc = eval(exp)
                require(x, callable(proc), "macro must be a procedure")
                macro_table[v] = proc    # (define-macro v proc)
                return None              #  => None; add v:proc to macro_table
            return [_define, v, exp]
    elif x[0] is _begin:
        if len(x)==1: return None        # (begin) => None
        else: return [expand(xi, toplevel) for xi in x]
    elif x[0] is _lambda:                # (lambda (x) e1 e2)
        require(x, len(x)>=3)            #  => (lambda (x) (begin e1 e2))
        vars, body = x[1], x[2:]
        require(x, (isa(vars, list) and all(isa(v, Symbol) for v in vars))
                or isa(vars, Symbol), "illegal lambda argument list")
        exp = body[0] if len(body) == 1 else [_begin] + body
        return [_lambda, vars, expand(exp)]
    elif x[0] is _quasiquote:            # `x => expand_quasiquote(x)
        require(x, len(x)==2)
        return expand_quasiquote(x[1])
    elif isa(x[0], Symbol) and x[0] in macro_table:
        return expand(macro_table[x[0]](*x[1:]), toplevel) # (m arg...)
    else:                                #        => macroexpand if m isa macro
        return list(map(expand, x))            # (f arg...) => expand each

def require(x, predicate, msg="wrong length"):
    "Signal a syntax error if predicate is false."
    if not predicate: raise SyntaxError(to_string(x)+': '+msg)

_append, _cons, _let = map(Sym, "append cons let".split())

def expand_quasiquote(x):
    """Expand `x => 'x; `,x => x; `(,@x y) => (append x y) """
    if not is_pair(x):
        return [_quote, x]
    require(x, x[0] is not _unquotesplicing, "can't splice here")
    if x[0] is _unquote:
        require(x, len(x)==2)
        return x[1]
    elif is_pair(x[0]) and x[0][0] is _unquotesplicing:
        require(x[0], len(x[0])==2)
        return [_append, x[0][1], expand_quasiquote(x[1:])]
    else:
        return [_cons, expand_quasiquote(x[0]), expand_quasiquote(x[1:])]

def let(*args):
    args = list(args)
    x = cons(_let, args)
    require(x, len(args)>1)
    bindings, body = args[0], args[1:]
    require(x, all(isa(b, list) and len(b)==2 and isa(b[0], Symbol)
                   for b in bindings), "illegal binding list")
    vars, vals = zip(*bindings)
    return [[_lambda, list(vars)]+list(map(expand, body))] + list(map(expand, vals))

macro_table = {_let:let} ## More macros can go here

################ core builtins

eval(parse("""(begin

(define-macro and (lambda args
   (if (null? args) #t
       (if (= (length args) 1) (car args)
           `(if ,(car args) (and ,@(cdr args)) #f)))))

(define-macro or (lambda args
   (if (null? args) #f
       (if (= (length args) 1) (car args)
           `(if (not ,(car args)) (or ,@(cdr args)) #t)))))

(define-macro when (lambda args
  `(if ,(car args) (begin ,@(cdr args)))))

(define-macro unless (lambda args
  `(if (not ,(car args)) (begin ,@(cdr args)))))

;; More macros can also go here

)"""))


################ hardware builtins

import time
import board
import busio
from adafruit_bus_device.i2c_device import I2CDevice
import digitalio
import analogio

board_pins = mod_vars(board)

def get_board_pins():
    return list(board_pins.keys())

def get_pin(pin_name):
    try:
        return board_pins[pin_name]
    except KeyError:
        print('{0} is not a valid pin name'.format(pin_name))
        return None

def make_digital_pin(pin, direction, pull=None):
    p = digitalio.DigitalInOut(pin)
    p.direction = direction
    if direction is digitalio.Direction.INPUT:
        p.pull = pull
    return p

def make_analog_pin(pin, direction):
    if direction is digitalio.Direction.INPUT:
        p = analogio.AnalogIn(pin)
    else:
        p = analogio.AnalogOut(pin)
    return p

def set_pin_value(pin, value):
    pin.value = value

def get_pin_value(pin):
    return pin.value

def i2c_bus(scl, sda):
    return busio.I2C(scl, sda)

def i2c_device(i2c, address):
    return I2CDevice(i2c, address)



def execfile(f):
    exec(open(f).read())

def load_device(device_driver_name):
    try:
        execfile('./devices/{0}.py'.format(device_driver_name))
    except OSError:
        pass

    try:
        load('./devices/{0}.scm'.format(device_driver_name))
    except OSError:
        pass

global_env.storage.update({
    'load-device':load_device,
    'board-pins':get_board_pins,
    'board':get_pin,
    'digital-pin':make_digital_pin,
    'analog-pin':make_analog_pin,
    '**INPUT**':digitalio.Direction.INPUT,
    '**OUTPUT**':digitalio.Direction.OUTPUT,
    '**PULLUP**':digitalio.Pull.UP,
    '**PULLDOWN**':digitalio.Pull.DOWN,
    'pin-value':get_pin_value,
    'pin-value!':set_pin_value,

    'i2c':i2c_bus,

    'sleep':time.sleep
    })


if __name__ == '__main__':
    print('CircuitScheme version 1.0: {0} bytes free.\n'.format(gc.mem_free()))

    try:
        load("code")
    except OSError:
        pass

    load_history()
    repl()
    save_history()
