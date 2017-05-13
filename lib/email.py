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

import click
from smtplib import SMTP, SMTP_SSL
from email.mime.text import MIMEText

config = require('../config')


def make_smtp():
  if config.email['smtp_ssl']:
    cls = SMTP_SSL
  else:
    cls = SMTP
  return cls(config.email['smtp_host'])


@click.command()
@click.argument('from_', 'from')
@click.argument('to')
def main(from_, to):
  """
  Send a test-email using the nodepy registry email configuration.
  """

  part = email.MIMEText('This is a test email')
  part['From'] = from_
  part['To'] = to
  part['Subject'] = 'Test email'
  s = email.make_smtp()
  s.sendmail(from_, [to], part.as_string())
  s.quit()


if require.main == module:
  main()
