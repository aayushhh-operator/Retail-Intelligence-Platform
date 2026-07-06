"""OrderAnalyticsJob Placeholder."""
from spark.base_job import BaseSparkJob

class OrderAnalyticsJob(BaseSparkJob):
    def __init__(self):
        super().__init__("OrderAnalyticsJob")
    def load_data(self):
        return {}
    def transform(self, dataframes):
        pass
    def write_output(self, df):
        pass

def main():
    pass
