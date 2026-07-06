"""RevenueAggregationJob Placeholder."""
from spark.base_job import BaseSparkJob

class RevenueAggregationJob(BaseSparkJob):
    def __init__(self):
        super().__init__("RevenueAggregationJob")
    def load_data(self):
        return {}
    def transform(self, dataframes):
        pass
    def write_output(self, df):
        pass

def main():
    pass
