import pytest
import os, sys
import warnings
from pprint import pprint

from nbformat import NotebookNode
import IPython

try:
    from exceptions import Exception, TypeError, ImportError
except:
    pass

from runipy.notebook_runner import NotebookRunner

wrapped_stdin = sys.stdin
sys.stdin = sys.__stdin__
sys.stdin = wrapped_stdin
try:
    from Queue import Empty
except:
    from queue import Empty

# code copied from runipy main.py
with warnings.catch_warnings():
    try:
        from IPython.utils.shimmodule import ShimWarning
        warnings.filterwarnings('error', '', ShimWarning)
    except ImportError:
        class ShimWarning(Warning):
            """Warning issued by iPython 4.x regarding deprecated API."""
            pass

    try:
        # IPython 3
        from IPython.nbformat import reads, NBFormatError
    except ShimWarning:
        # IPython 4
        from nbformat import reads, NBFormatError
    except ImportError:
        # IPython 2
        from IPython.nbformat.current import reads, NBFormatError
    finally:
        warnings.resetwarnings()

class IPyNbException(Exception):
    """ custom exception for error reporting. """

def pytest_collect_file(path, parent):
    if path.fnmatch("test*.ipynb"):
        return IPyNbFile(path, parent)

def get_cell_description(cell_input):
    """Gets cell description

    Cell description is the first line of a cell,
    in one of this formats:

    * single line docstring
    * single line comment
    * function definition
    """
    try:
        first_line = cell_input.split("\n")[0]
        if first_line.startswith(('"', '#', 'def', '%')):
            return first_line.replace('"','').replace("#",'').replace('def ', '').replace("_", " ").strip()
    except:
        pass
    return ""

class IPyNbFile(pytest.File):
    def collect(self):
        with self.fspath.open() as f:
            payload = f.read()
        self.notebook_folder = self.fspath.dirname
        try:
            # Ipython 3
            self.nb = reads(payload, 3)
        except (TypeError, NBFormatError):
            # Ipython 2
            self.nb = reads(payload, 'json')
        self.runner = NotebookRunner(self.nb)

        cell_num = 1

        for cell in self.runner.iter_code_cells():
            yield IPyNbCell(self.name, self, cell_num, cell)
            cell_num += 1

    def setup(self):
        self.fixture_cell = None

    def teardown(self):
        self.runner.shutdown_kernel()

class IPyNbCell(pytest.Item):

    MIME_MAP = {
        'image/jpeg': 'jpeg',
        'image/png': 'png',
        'text/plain': 'text',
        'text/html': 'html',
        'text/latex': 'latex',
        'application/javascript': 'html',
        'application/json': 'json',
        'image/svg+xml': 'svg',
    }

    def __init__(self, name, parent, cell_num, cell):
        cell_description = get_cell_description(cell.input)
        nodeid = parent.nodeid + "::" + f"cell {cell_num:2d}"
        if cell_description: nodeid += " " + cell_description[0:40]

        super(IPyNbCell, self).__init__(name, parent, nodeid=nodeid)

        self.cell_num = cell_num
        self.cell = cell
        self.cell_description = cell_description


    # use run_cell from runipy/notebook_runner.py as a base for a better runtest
    # implementation than the original pytest-ipynb, to include reporting output streams
    def runtest(self):
        self.kc = self.parent.runner.kc
        cell = self.cell

        if ("SKIPCI" in self.cell_description) and ("CI" in os.environ):
            return

        if self.parent.fixture_cell:
            kc.execute(self.parent.fixture_cell.input, allow_stdin=False)

        if self.cell_description.lower().startswith("fixture") or self.cell_description.lower().startswith("setup"):
            self.parent.fixture_cell = self.cell

        self.kc.execute(cell.input, allow_stdin=False)
        reply = self.kc.get_shell_msg()
        status = reply['content']['status']
        traceback_text = ''
        if status == 'error':
            traceback_text = 'Cell raised uncaught exception: \n' + \
                '\n'.join(reply['content']['traceback'])

        outs = list()
        # XXX: we really only care for pyout and stdout streams below, so the following can be pruned a lot
        timeout = 20
        while True:
            try:
                msg = self.kc.get_iopub_msg(timeout=timeout)
                if msg['msg_type'] == 'status':
                    if msg['content']['execution_state'] == 'idle':
                        break
            except Empty:
                # execution state should return to idle
                # before the queue becomes empty,
                # if it doesn't, something bad has happened
                raise

            content = msg['content']
            msg_type = msg['msg_type']

            # IPython 3.0.0-dev writes pyerr/pyout in the notebook format
            # but uses error/execute_result in the message spec. This does the
            # translation needed for tests to pass with IPython 3.0.0-dev
            notebook3_format_conversions = {
                'error': 'pyerr',
                'execute_result': 'pyout'
            }
            msg_type = notebook3_format_conversions.get(msg_type, msg_type)

            out = NotebookNode(output_type=msg_type)

            if 'execution_count' in content:
                cell['prompt_number'] = content['execution_count']
                out.prompt_number = content['execution_count']

            if msg_type in ('status', 'pyin', 'execute_input'):
                continue
            elif msg_type == 'stream':
                out.stream = content['name']
                # in msgspec 5, this is name, text
                # in msgspec 4, this is name, data
                if 'text' in content:
                    out.text = content['text']
                else:
                    out.text = content['data']
            elif msg_type in ('display_data', 'pyout'):
                for mime, data in content['data'].items():
                    try:
                        attr = self.MIME_MAP[mime]
                    except KeyError:
                        raise NotImplementedError(
                            'unhandled mime type: %s' % mime
                        )

                    # In notebook version <= 3 JSON data is stored as a string
                    # Evaluation of IPython2's JSON gives strings directly
                    # Therefore do not encode for IPython versions prior to 3
                    json_encode = (
                            IPython.version_info[0] >= 3 and
                            mime == "application/json")

                    data_out = data if not json_encode else json.dumps(data)
                    setattr(out, "data_type", attr)
                    setattr(out, "data", data_out)
            elif msg_type == 'pyerr':
                out.ename = content['ename']
                out.evalue = content['evalue']
                out.traceback = content['traceback']
            elif msg_type == 'clear_output':
                outs = list()
                continue
            else:
                raise NotImplementedError(
                    'unhandled iopub message: %s' % msg_type
                )
            outs.append(out)
        #cell['outputs'] = outs

        if status == 'error':
            # Extract all output streams, so that we can display them in the exception
            pyout = []
            stdout_data = ''
            for out in outs:
                if out.output_type == 'pyout':
                    # text, html, json (others are binary)
                    if out.data_type in ["text", "html", "json"]:
                        pyout.append(out.data)
                    else:
                        pyout.append(f"[{out.data_type} object]")
                elif 'stream' in out and out.stream == 'stdout':
                    stdout_data = out.text
            #pprint(outs)
            #pprint(pyout)

            raise IPyNbException(self.cell_num, self.cell.input, "\n".join(pyout), stdout_data, traceback_text)


    # this is the old implementation, which needs to be merged with the new one
    # if we were to support all the previous features.
    def runtest2(self):
        kc = self.parent.runner.kc
        self.kc = kc
        cell = self.cell

        # must not restart kernel for each cell! (XXX: needs to be made configurable for those who want it to be restarted).
        #self.parent.runner.km.restart_kernel()

        if self.parent.notebook_folder:
            kc.execute(f"import os; os.chdir('{self.parent.notebook_folder}')")

        if ("SKIPCI" in self.cell_description) and ("CI" in os.environ):
            pass
        else:
            if self.parent.fixture_cell:
                kc.execute(self.parent.fixture_cell.input, allow_stdin=False)
            msg_id = kc.execute(self.cell.input, allow_stdin=False)
            if self.cell_description.lower().startswith("fixture") or self.cell_description.lower().startswith("setup"):
                self.parent.fixture_cell = self.cell

            timeout = 20
            while True:
                try:
                    msg = kc.get_shell_msg(block=True, timeout=timeout)
                    if msg.get("parent_header", None) and msg["parent_header"].get("msg_id", None) == msg_id:
                        break
                except Empty:
                    raise IPyNbException(self.cell_num, self.cell.input, "no output?",
                                         "no stdout",
                                         "Timeout of %d seconds exceeded executing cell: %s" % (timeout, self.cell.input))

            reply = msg['content']
            if reply['status'] == 'error':
                raise IPyNbException(self.cell_num, self.cell.input, "nooutput?", "nostdout?", '\n'.join(reply['traceback']))

    def repr_failure(self, excinfo):
        """ called when self.runtest() raises an exception. """
        if isinstance(excinfo.value, IPyNbException):
            return "\n".join([
                "*** Failed cell %d: ***\n\n"
                "*** Input ***\n%s\n\n"
                "*** Output ***\n%s\n\n"
                "*** STDOUT ***\n%s\n\n"
                "*** Traceback ***\n%s\n\n\n\n" % excinfo.value.args,
            ])
        else:
            return "pytest plugin exception: %s" % str(excinfo.value)
