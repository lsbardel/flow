import datetime
import re
import sys



class ExceptionReporter(object):
    """
    A class to organize and coordinate reporting on exceptions.
    """
    def __init__(self, exc_type, exc_value, tb):
        self.exc_type = exc_type
        self.exc_value = exc_value
        self.tb = tb

    def get_traceback(self):
        '''
        Return a string for the traceback
        '''
        frames = self.get_traceback_frames()
        c = {
            'exception_type': self.exc_type.__name__,
            'exception_value': self.exc_value,
            'frames': frames,
            'lastframe': frames[-1],
            'sys_executable': sys.executable,
            'sys_version_info': '%d.%d.%d' % sys.version_info[0:3],
            'server_time': datetime.datetime.now(),
            'sys_path' : sys.path,
            }
        return c

    def get_template_exception_info(self):
        origin, (start, end) = self.exc_value.source
        template_source = origin.reload()
        context_lines = 10
        line = 0
        upto = 0
        source_lines = []
        before = during = after = ""
        for num, next in enumerate(linebreak_iter(template_source)):
            if start >= upto and end <= next:
                line = num
                before = escape(template_source[upto:start])
                during = escape(template_source[start:end])
                after = escape(template_source[end:next])
            source_lines.append( (num, escape(template_source[upto:next])) )
            upto = next
        total = len(source_lines)

        top = max(1, line - context_lines)
        bottom = min(total, line + 1 + context_lines)

        self.template_info = {
            'message': self.exc_value.args[0],
            'source_lines': source_lines[top:bottom],
            'before': before,
            'during': during,
            'after': after,
            'top': top,
            'bottom': bottom,
            'total': total,
            'line': line,
            'name': origin.name,
        }

    def _get_lines_from_file(self, filename, lineno, context_lines, loader=None, module_name=None):
        """
        Returns context_lines before and after lineno from file.
        Returns (pre_context_lineno, pre_context, context_line, post_context).
        """
        source = None
        if loader is not None and hasattr(loader, "get_source"):
            source = loader.get_source(module_name)
            if source is not None:
                source = source.splitlines()
        if source is None:
            try:
                f = open(filename)
                try:
                    source = f.readlines()
                finally:
                    f.close()
            except (OSError, IOError):
                pass
        if source is None:
            return None, [], None, []

        encoding = 'ascii'
        for line in source[:2]:
            # File coding may be specified. Match pattern from PEP-263
            # (http://www.python.org/dev/peps/pep-0263/)
            match = re.search(r'coding[:=]\s*([-\w.]+)', line)
            if match:
                encoding = match.group(1)
                break
        source = [unicode(sline, encoding, 'replace') for sline in source]

        lower_bound = max(0, lineno - context_lines)
        upper_bound = lineno + context_lines

        pre_context = [line.strip('\n') for line in source[lower_bound:lineno]]
        context_line = source[lineno].strip('\n')
        post_context = [line.strip('\n') for line in source[lineno+1:upper_bound]]

        return lower_bound, pre_context, context_line, post_context

    def get_traceback_frames(self):
        frames = []
        tb = self.tb
        while tb is not None:
            # support for __traceback_hide__ which is used by a few libraries
            # to hide internal frames.
            if tb.tb_frame.f_locals.get('__traceback_hide__'):
                tb = tb.tb_next
                continue
            filename = tb.tb_frame.f_code.co_filename
            function = tb.tb_frame.f_code.co_name
            lineno = tb.tb_lineno - 1
            loader = tb.tb_frame.f_globals.get('__loader__')
            module_name = tb.tb_frame.f_globals.get('__name__')
            pre_context_lineno, pre_context, context_line, post_context = self._get_lines_from_file(filename, lineno, 7, loader, module_name)
            if pre_context_lineno is not None:
                frames.append({
                    'tb': tb,
                    'filename': filename,
                    'function': function,
                    'lineno': lineno + 1,
                    'vars': tb.tb_frame.f_locals.items(),
                    'id': id(tb),
                    'pre_context': pre_context,
                    'context_line': context_line,
                    'post_context': post_context,
                    'pre_context_lineno': pre_context_lineno + 1,
                })
            tb = tb.tb_next

        if not frames:
            frames = [{
                'filename': '&lt;unknown&gt;',
                'function': '?',
                'lineno': '?',
                'context_line': '???',
            }]

        return frames

    def format_exception(self):
        """
        Return the same data as from traceback.format_exception.
        """
        import traceback
        frames = self.get_traceback_frames()
        tb = [ (f['filename'], f['lineno'], f['function'], f['context_line']) for f in frames ]
        list = ['Traceback (most recent call last):\n']
        list += traceback.format_list(tb)
        list += traceback.format_exception_only(self.exc_type, self.exc_value)
        return list