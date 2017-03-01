# Copyright (c) 2017 Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import functools


def finally_(is_method=False):
  """
  Passes an additional parameter at the beginning which is a list of callables
  that will be called after the function returns.
  """

  if is_method:
    def decorator(func):
      @functools.wraps(func)
      def wrapper(self, *args, **kwargs):
        handlers = []
        try:
          return func(self, handlers, *args, **kwargs)
        finally:
          for handler in handlers:
            handler()
      return wrapper
  else:
    def decorator(func):
      @functools.wraps(func)
      def wrapper(*args, **kwargs):
        handlers = []
        try:
          return func(handlers, *args, **kwargs)
        finally:
          for handler in handlers:
            handler()
      return wrapper

  return decorator
