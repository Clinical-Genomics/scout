# -*- coding: utf-8 -*-
import logging
import logging.handlers


class TlsSMTPHandler(logging.handlers.SMTPHandler):
    def emit(self, record):
        """Emit a record.
        Format the record and send it to the specified addressees.
        """
        try:
            import smtplib

            try:
                from email.utils import formatdate
            except ImportError:
                formatdate = self.date_time

            port = self.mailport
            if not port:
                port = smtplib.SMTP_PORT

            smtp = smtplib.SMTP(self.mailhost, port)
            msg = self.format(record)
            msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s" % (
                self.fromaddr,
                ",".join(self.toaddrs),
                self.getSubject(record),
                formatdate(),
                msg,
            )

            if self.username:
                smtp.ehlo()  # For 'tls', add this line
                smtp.starttls()  # For 'tls', add this line
                smtp.ehlo()  # For 'tls', add this line
                smtp.login(self.username, self.password)

            smtp.sendmail(self.fromaddr, self.toaddrs, msg)
            smtp.quit()

        except (KeyboardInterrupt, SystemExit):
            raise

        except:
            self.handleError(record)
