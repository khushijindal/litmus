# (c) 2015, Andrew Gaffney <andrew@agaffney.org>
# (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    callback: actionable
    type: stdout
    short_description: shows only items that need attention
    description:
      - Use this callback when you dont care about OK nor Skipped.
      - This callback suppresses any non Failed or Changed status.
    version_added: "2.1"
    extends_documentation_fragment:
      - default_callback
    requirements:
      - set as stdout callback in configuration
'''

from ansible.plugins.callback.default import CallbackModule as CallbackModule_default


class CallbackModule(CallbackModule_default):

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'actionable'

    def __init__(self):
        self.super_ref = super(CallbackModule, self)
        self.super_ref.__init__()
        self.last_task = None
        self.shown_title = False

    def v2_playbook_on_handler_task_start(self, task):
        self.super_ref.v2_playbook_on_handler_task_start(task)
        self.shown_title = True

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.last_task = task
        self.shown_title = False

    def display_task_banner(self):
        if not self.shown_title:
            self.super_ref.v2_playbook_on_task_start(self.last_task, None)
            self.shown_title = True

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.display_task_banner()
        self.super_ref.v2_runner_on_failed(result, ignore_errors)

    def v2_runner_on_ok(self, result):
        if result._result.get('changed', False):
            self.display_task_banner()
            #self.super_ref.v2_runner_on_ok(result)

    def v2_runner_on_unreachable(self, result):
        self.display_task_banner()
        self.super_ref.v2_runner_on_unreachable(result)

    def v2_runner_on_skipped(self, result):
        pass

    def v2_playbook_on_include(self, included_file):
        pass

    def v2_runner_item_on_ok(self, result):
        if result._result.get('changed', False):
            self.display_task_banner()
            #self.super_ref.v2_runner_item_on_ok(result)

    def v2_runner_item_on_skipped(self, result):
        pass

    def v2_runner_item_on_failed(self, result):
        self.display_task_banner()
        self.super_ref.v2_runner_item_on_failed(result)

    def v2_runner_retry(self, result):
        task_name = result.task_name or result._task
        final_result = result._result['retries'] - result._result['attempts']
        msg = "FAILED - RETRYING: %s (%d retries left)." % (task_name,
                                                            final_result)
        display_verbosity = self._display.verbosity
        required_result = '_ansible_verbose_always'
        if (display_verbosity > 2 or required_result in result._result):
            if required_result not in result._result:
                msg += "Result was: %s" % self._dump_results(result._result)
        self._display.v('%s' % (msg))


