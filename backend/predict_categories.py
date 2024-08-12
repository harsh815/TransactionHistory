import os
import logging
from pyspark.sql import SparkSession
from pyspark.ml.feature import HashingTF, IDF, Tokenizer
from pyspark.ml import Pipeline
from pyspark.ml.linalg import Vectors
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def create_spark_session():
    return (SparkSession.builder
            .appName("SMS Category Prediction")
            .master(os.getenv("SPARK_MASTER", "local[*]"))
            .getOrCreate())

def load_config(spark_context):
    spark_context._jsc.hadoopConfiguration().set("fs.s3a.access.key", os.getenv("MINIO_ACCESS_KEY"))
    spark_context._jsc.hadoopConfiguration().set("fs.s3a.secret.key", os.getenv("MINIO_SECRET_KEY"))
    spark_context._jsc.hadoopConfiguration().set("fs.s3a.endpoint", f"http://{os.getenv('MINIO_ENDPOINT')}:{os.getenv('MINIO_PORT')}")
    spark_context._jsc.hadoopConfiguration().set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    spark_context._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")

def load_model(spark):
    bucket_name = os.getenv("MINIO_BUCKET_NAME", "sms-data")
    model_path = f"s3a://{bucket_name}/final-sms-model"
    model_data = spark.read.parquet(model_path).first()
    return model_data["centers"], model_data["labels"]

def find_nearest_cluster(vector, centers):
    return min(range(len(centers)), key=lambda i: Vectors.squared_distance(vector, centers[i]))

def predict_categories(spark, data, centers, labels):
    tokenizer = Tokenizer(inputCol="content", outputCol="words")
    hashingTF = HashingTF(inputCol="words", outputCol="rawFeatures", numFeatures=10000)
    idf = IDF(inputCol="rawFeatures", outputCol="features")
    
    pipeline = Pipeline(stages=[tokenizer, hashingTF, idf])
    feature_data = pipeline.fit(data).transform(data)
    
    find_nearest_cluster_udf = udf(lambda vector: find_nearest_cluster(vector, centers))
    clustered_data = feature_data.withColumn("prediction", find_nearest_cluster_udf("features"))
    
    get_label_udf = udf(lambda prediction: labels.get(prediction, "Unknown"), StringType())
    return clustered_data.withColumn("category", get_label_udf("prediction"))

if __name__ == "__main__":
    try:
        spark = create_spark_session()
        load_config(spark.sparkContext)
        logger.info("Spark session created and configured successfully")

        centers, labels = load_model(spark)
        logger.info("Model loaded successfully")

        bucket_name = os.getenv("MINIO_BUCKET_NAME", "sms-data")
        new_data_path = f"s3a://{bucket_name}/new-sms-data"
        categorized_data_path = f"s3a://{bucket_name}/categorized-sms-data"

        new_data = spark.read.parquet(new_data_path)
        logger.info(f"New SMS data loaded from {new_data_path}")

        categorized_data = predict_categories(spark, new_data, centers, labels)
        logger.info("Categories predicted for new SMS data")

        categorized_data.write.parquet(categorized_data_path)
        logger.info(f"Categorized data saved to {categorized_data_path}")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

    finally:
        if spark:
            spark.stop()
            logger.info("Spark session stopped")
