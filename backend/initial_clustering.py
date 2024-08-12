import os
import logging
from pyspark.sql import SparkSession
from pyspark.ml.feature import HashingTF, IDF, Tokenizer
from pyspark.ml.clustering import KMeans
from pyspark.ml import Pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def create_spark_session():
    return (SparkSession.builder
            .appName("SMS Initial Clustering")
            .master(os.getenv("SPARK_MASTER", "local[*]"))
            .getOrCreate())

def load_config(spark_context):
    spark_context._jsc.hadoopConfiguration().set("fs.s3a.access.key", os.getenv("MINIO_ACCESS_KEY"))
    spark_context._jsc.hadoopConfiguration().set("fs.s3a.secret.key", os.getenv("MINIO_SECRET_KEY"))
    spark_context._jsc.hadoopConfiguration().set("fs.s3a.endpoint", f"http://{os.getenv('MINIO_ENDPOINT')}:{os.getenv('MINIO_PORT')}")
    spark_context._jsc.hadoopConfiguration().set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    spark_context._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")

def cluster_sms(data, num_clusters=100):
    tokenizer = Tokenizer(inputCol="content", outputCol="words")
    hashingTF = HashingTF(inputCol="words", outputCol="rawFeatures", numFeatures=10000)
    idf = IDF(inputCol="rawFeatures", outputCol="features")
    kmeans = KMeans(k=num_clusters, seed=1)

    pipeline = Pipeline(stages=[tokenizer, hashingTF, idf, kmeans])
    model = pipeline.fit(data)

    return model, model.transform(data)

if __name__ == "__main__":
    try:
        spark = create_spark_session()
        load_config(spark.sparkContext)
        logger.info("Spark session created and configured successfully")

        bucket_name = os.getenv("MINIO_BUCKET_NAME", "sms-data")
        training_data_path = f"s3a://{bucket_name}/training-data"
        model_output_path = f"s3a://{bucket_name}/sms-cluster-model"
        clustered_data_output_path = f"s3a://{bucket_name}/clustered-training-data"

        training_data = spark.read.parquet(training_data_path)
        logger.info(f"Successfully loaded training data from {training_data_path}. Row count: {training_data.count()}")

        model, clustered_data = cluster_sms(training_data)
        logger.info("SMS clustering completed successfully")

        model.save(model_output_path)
        logger.info(f"Model saved successfully to {model_output_path}")

        clustered_data.write.parquet(clustered_data_output_path)
        logger.info(f"Clustered data saved successfully to {clustered_data_output_path}")

        logger.info("Initial clustering process completed successfully")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

    finally:
        if spark:
            spark.stop()
            logger.info("Spark session stopped")
