
class Job():
    
    def __init__(self, packet):
        self._packet = packet
        self._inputs = packet['job_description']
        self._results = packet['job_result']
        
    @property
    def inputs(self):
        return self._inputs
    
    @property
    def results(self):
        return self._results