import logging
import re
from pyspark.sql import SparkSession
from pyspark.ml.feature import RegexTokenizer, StopWordsRemover, CountVectorizer, IDF, StringIndexer, VectorAssembler
from pyspark.ml.clustering import KMeans
from pyspark.ml import Pipeline
from pyspark.sql.functions import udf, rand, when, lit, col, count
from pyspark.sql.types import FloatType

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_amount(content):
    if content is None:
        return None
    amount_pattern = r'(?i)(?:rs\.?|inr)\s*(\d+(?:[.,]\d+)?)'
    match = re.search(amount_pattern, content)
    if match:
        amount_str = match.group(1).replace(',', '')
        return float(amount_str)
    return 0.0

def main():
    file_location = "sms_training_data.csv"
    file_type = "csv"
    infer_schema = "false"
    first_row_is_header = "true"
    delimiter = ","

    logger.info("Starting Spark session")
    spark = SparkSession.builder.appName("SMSClustering").getOrCreate()

    logger.info("Reading CSV file from location: %s", file_location)
    try:
        df = spark.read.format(file_type) \
          .option("inferSchema", infer_schema) \
          .option("header", first_row_is_header) \
          .option("sep", delimiter) \
          .option("multiline", True) \
          .option("quote", "\"") \
          .option("escape", "\"") \
          .load(file_location)
        logger.info("CSV file loaded successfully")
    except Exception as e:
        logger.error("Error loading CSV file: %s", str(e))
        spark.stop()
        return

    logger.info("Checking for null values in the DataFrame")
    try:
        null_counts = df.select([count(when(col(c).isNull(), c)).alias(c) for c in df.columns]).collect()[0]
        logger.info("Null counts: %s", null_counts)
    except Exception as e:
        logger.error("Error checking null values: %s", str(e))

    logger.info("Handling null values by replacing with empty strings")
    df = df.withColumn("content", when(df.content.isNull(), lit("")).otherwise(df.content))

    logger.info("Defining UDF for extracting amounts from content")
    extract_amount_udf = udf(extract_amount, FloatType())
    df = df.withColumn("extracted_amount", extract_amount_udf(df.content))

    logger.info("Replacing null extracted amounts with 0")
    df = df.withColumn("extracted_amount", when(df.extracted_amount.isNull(), 0).otherwise(df.extracted_amount))

    logger.info("Displaying sample data")
    df.show(5, truncate=False)

    logger.info("Setting up ML pipeline stages")
    tokenizer = RegexTokenizer(inputCol="content", outputCol="words", pattern="\\s+|[^\\w]+", gaps=False, minTokenLength=1)
    remover = StopWordsRemover(inputCol=tokenizer.getOutputCol(), outputCol="filtered")
    countVectorizer = CountVectorizer(inputCol=remover.getOutputCol(), outputCol="rawFeatures", minDF=2.0)
    idf = IDF(inputCol=countVectorizer.getOutputCol(), outputCol="contentFeatures")
    senderIndexer = StringIndexer(inputCol="sender", outputCol="senderIndex")
    assembler = VectorAssembler(inputCols=["senderIndex", "contentFeatures", "extracted_amount"], outputCol="features")
    kmeans = KMeans(k=20, seed=1)

    pipeline = Pipeline(stages=[tokenizer, remover, countVectorizer, idf, senderIndexer, assembler, kmeans])


    try:
        logger.info("Fitting the pipeline to the data")
        model = pipeline.fit(df)
        logger.info("Pipeline fitted successfully")

        logger.info("Transforming data using the fitted model")
        clustered_df = model.transform(df)
        logger.info("Data transformation complete")

        logger.info("Selecting and saving cluster representatives")
        representatives = clustered_df.groupBy("prediction") \
                                      .agg({"content": "first", "sender": "first", "extracted_amount": "first"}) \
                                      .select("prediction", "first(content)", "first(sender)", "first(extracted_amount)")
        representatives.write.csv("cluster_representatives.csv", header=True)
        logger.info("Cluster representatives saved to cluster_representatives.csv")

        logger.info("Saving the trained model")
        model.save("sms_clustering_model")
        logger.info("Model saved successfully")

    except Exception as e:
        logger.error("An error occurred during clustering: %s", str(e))
    
    finally:
        logger.info("Stopping Spark session")
        spark.stop()

if __name__ == "__main__":
    main()
