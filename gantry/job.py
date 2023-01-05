
class Job():

    def __init__(self, packet):
        self._packet = packet
        self._inputs = packet['job_description']
        self._results = packet['job_result']

    def __str__(self):
        return f"{self._packet['id']}  {self._packet['status']}  {self._inputs['name']} "

    @property
    def inputs(self):
        return self._inputs

    @property
    def results(self):
        return self._results
