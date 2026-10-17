"""Optional distributed batch encoding. Run only on a configured Spark cluster."""
import argparse,json
from pyspark.sql import SparkSession,types as T
p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True);p.add_argument('--model',required=True);p.add_argument('--revision',required=True);p.add_argument('--partitions',type=int,default=8);a=p.parse_args()
spark=SparkSession.builder.appName('group4-embedding').getOrCreate()
spec=dict(backend='sentence-transformers',model=a.model,revision=a.revision,max_seq_length=256,batch_size=64)
bc=spark.sparkContext.broadcast(spec)
def encode_partition(iterator):
    from lean_retrieval.core import Encoder
    encoder=Encoder(bc.value);batch=[]
    def emit(items):
        v=encoder.encode([x.statement for x in items])
        return [(x.id,x.statement,y.tolist()) for x,y in zip(items,v)]
    for row in iterator:
        batch.append(row)
        if len(batch)==64:
            yield from emit(batch);batch=[]
    if batch:yield from emit(batch)
schema=T.StructType([T.StructField('id',T.StringType(),False),T.StructField('statement',T.StringType(),False),T.StructField('vector',T.ArrayType(T.FloatType()),False)])
df=spark.read.json(a.input).select('id','statement').repartition(a.partitions)
spark.createDataFrame(df.rdd.mapPartitions(encode_partition),schema).write.mode('errorifexists').parquet(a.output)
spark.stop()
