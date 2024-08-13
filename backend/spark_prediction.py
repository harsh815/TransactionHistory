from pyspark.sql import SparkSession
from pyspark.ml import PipelineModel
from pyspark.sql.functions import udf
from pyspark.sql.types import FloatType
import re
import json
import sys

def extract_amount(content):
    amount_pattern = r'(?i)(?:rs\.?|inr)\s*(\d+(?:[.,]\d+)?)'
    match = re.search(amount_pattern, content)
    if match:
        amount_str = match.group(1).replace(',', '')
        return float(amount_str)
    return 0.0

def predict_sms(sms_data):
    spark = SparkSession.builder.appName("SMSPrediction").getOrCreate()

    # Load the models
    clustering_model = PipelineModel.load("sms_clustering_model")
    classification_model = PipelineModel.load("sms_classification_model")

    # Create DataFrame from input
    df = spark.createDataFrame(sms_data, ["timestamp", "sender", "content"])

    # Extract amount
    extract_amount_udf = udf(extract_amount, FloatType())
    df = df.withColumn("extracted_amount", extract_amount_udf(df.content))

    # Apply clustering
    clustered_df = clustering_model.transform(df)

    # Apply classification
    result_df = classification_model.transform(clustered_df)

    # Select relevant columns
    output_df = result_df.select("timestamp", "sender", "prediction", "extracted_amount")

    # Collect results
    results = output_df.collect()

    spark.stop()

    return [{"timestamp": row.timestamp, "sender": row.sender, "category": row.prediction, "amount": row.extracted_amount} for row in results]

if __name__ == "__main__":
    # Read JSON input from stdin
    sms_data = json.load(sys.stdin)
    
    # Process and predict
    categorized_sms = predict_sms(sms_data)
    
    # Output JSON result to stdout
    json.dump(categorized_sms, sys.stdout)
