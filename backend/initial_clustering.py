from pyspark.sql import SparkSession
from pyspark.ml.feature import HashingTF, IDF, Tokenizer
from pyspark.ml.clustering import KMeans
from pyspark.ml import Pipeline

def create_spark_session():
    return SparkSession.builder.appName("SMS Initial Clustering").getOrCreate()

def cluster_sms(data, num_clusters=100):
    tokenizer = Tokenizer(inputCol="content", outputCol="words")
    hashingTF = HashingTF(inputCol="words", outputCol="rawFeatures", numFeatures=10000)
    idf = IDF(inputCol="rawFeatures", outputCol="features")
    kmeans = KMeans(k=num_clusters, seed=1)

    pipeline = Pipeline(stages=[tokenizer, hashingTF, idf, kmeans])
    model = pipeline.fit(data)

    return model, model.transform(data)

if __name__ == "__main__":
    spark = create_spark_session()
    
    # Load your training data
    training_data = spark.read.parquet("s3a://your-bucket/training-data")
    
    model, clustered_data = cluster_sms(training_data)
    
    # Save the model and clustered data for the next step
    model.save("s3a://your-bucket/sms-cluster-model")
    clustered_data.write.parquet("s3a://your-bucket/clustered-training-data")