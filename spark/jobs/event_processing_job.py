"""EventProcessingJob Placeholder."""
from spark.base_job import BaseSparkJob

class EventProcessingJob(BaseSparkJob):
    def __init__(self):
        super().__init__("EventProcessingJob")
    def load_data(self):
        return {}
    def transform(self, dataframes):
        pass
    def write_output(self, df):
        pass

def main():
    pass
