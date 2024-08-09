from pyspark.sql import SparkSession
from pyspark.ml.feature import HashingTF, IDF, Tokenizer
from pyspark.ml import Pipeline
from pyspark.ml.linalg import Vectors
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

def create_spark_session():
    return SparkSession.builder.appName("SMS Category Prediction").getOrCreate()

def load_model(spark):
    model_data = spark.read.parquet("s3a://your-bucket/final-sms-model").first()
    centers = model_data["centers"]
    labels = model_data["labels"]
    return centers, labels

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
    spark = create_spark_session()
    
    # Load the model
    centers, labels = load_model(spark)
    
    # Load new SMS data
    new_data = spark.read.parquet("s3a://your-bucket/new-sms-data")
    
    # Predict categories
    categorized_data = predict_categories(spark, new_data, centers, labels)
    
    # Save the results
    categorized_data.write.parquet("s3a://your-bucket/categorized-sms-data")