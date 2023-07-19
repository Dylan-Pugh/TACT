import pandas as pd
from ioos_qc import qartod
from ioos_qc.config import QcConfig
from ioos_qc.streams import PandasStream
from ioos_qc.results import collect_results

#reconfigure into class that takes config & input data as args
#getter methods to get results as dfs or list, or JSON, etc.

class QARTODHandler:

    def __init__(self, datasource, config) -> None:
        self.datasource = datasource
        self.config = QcConfig(config)

    def run_tests(self, input_variable, time_variable):
        # Run QC
        # this takes a Context Config currently??
        self.results =  self.config.run(
            inp=self.datasource[input_variable],
            tinp=self.datasource[time_variable],
            zinp=self.datasource['z']
        )

        # Set up the stream
        ps = PandasStream(self.datasource, time=time_variable)

        # Pass the run method the config to use
        stream_results = ps.run(self.config)
    
    def get_results(self):
        return self.results
    
    def get_results_list(self):
        return collect_results(self.results, how='list')
    
    def get_appended_results(self):
        result_df = pd.DataFrame(self.results["qartod"], columns=self.results["qartod"].keys())
        return pd.concat([self.datasource, result_df], axis=1)