""" 
{    "eventName" : ["INSERT", "UPDATE"] }
"""

import json
import boto3
import psycopg2

from boto3.dynamodb.types import TypeDeserializer
deserializer = TypeDeserializer()

def rds_connection():

    # send to DB
    credentials = {
        "host": "hero-database-2.cluster-c5rea6ohaa0g.us-west-2.rds.amazonaws.com",
        "database": "hero",
        "user": "heroops",
        "application_name": "hero-python",
        "port": "5432",
        "password": "8fc2a2e2-ed9e-413d-996a-72da94e11c5c"
    }
    return psycopg2.connect(**credentials, connect_timeout=30)
    
def insert_records(connection, records):
    print("RDS insert_records =====> ", len(records))
    
    jobs = []
    for record in records:
        job_description = {
            k: deserializer.deserialize(v)
            for k, v in record["dynamodb"]["NewImage"].items()
        }
        
        
        if "inputs" in job_description.keys():
            tmp = (job_description['task_id'], 
                job_description['queue'], 
                "ready", 
                job_description.get("project", "None"), 
                json.dumps(job_description['inputs'], default=str) )
            if job_description['inputs'].get("stream_db", True):
                jobs.append(tmp)
        else:
            print("ERROR", "no item", job_description)
        
    if len(jobs) > 0:
        argument_string = ",".join("('%s', '%s', '%s', '%s', '%s')" % (b, a, x, y, z) for (b, a, x, y, z) in jobs)
        # print(argument_string)
        with connection.cursor() as cursor:
            try:
                cursor.execute("INSERT INTO hero.jobs  (id, queue_name, status, name, job_description) VALUES " + argument_string)
            except Exception as e:
                print("ERROR " + "failed insert " + str(e))
                
def update_records(connection, records):
    
    jobs = {}
    for record in records:
        job_description = {
            k: deserializer.deserialize(v)
            for k, v in record["dynamodb"]["NewImage"].items()
        }
        tmp_status = job_description.get('status', "Unknown")
        if job_description.get("inputs", {}).get("stream_db", True):
            jobs[tmp_status] = jobs.get(tmp_status, [])
            jobs[tmp_status].append(job_description)
        
        print("UPDATE", job_description['status'], job_description['claimed_resource_name'])
   
   
    if len(jobs.get('Unknown', [])) > 0:
        print("RDS unknown ERROR =====> ", len(jobs.get('Unknown', [])))
        print("RDS unknown ERROR =====> ", jobs.get('Unknown', []))
    
    if len(jobs.get('claimed', [])) > 0:
        print("RDS claimed =====> ", len(jobs['claimed']))
        
        argument_string = ",".join(f"('{job['task_id']}', '{job.get('claimed_resource_name')}')" for job in jobs['claimed']) 
        print("argument_string", argument_string)
        with connection.cursor() as cursor:
            cmd = """
                UPDATE hero.jobs as t
                SET
                    status = 'claimed',
                    updated_on = NOW(),
                    start_time = NOW(),
                    resource_name = c.resource_name
                FROM ( values {values}) as c(id, resource_name) 
                where c.id = t.id::text  
            """.format(values=argument_string)
            cursor.execute(cmd)
            
            
    # add results
    if  len(jobs.get('complete', [])) > 0:
        print("RDS complete =====> ", len(jobs['complete']))
        print(jobs['complete'])
        
        
        argument_string = ",".join(f"('{job['task_id']}', '{ json.dumps(job.get('results'), default=str) }')" for job in jobs['complete']) 
        print("argument_string ---> ", argument_string)
        
        with connection.cursor() as cursor:
            cmd = """
                UPDATE hero.jobs as t
                SET
                    status = 'complete',
                    updated_on = NOW(),
                    end_time = NOW(),
                    job_result = cast(c.job_result AS json)
                FROM ( values {values}) as c(id, job_result) 
                where c.id = t.id::text  
            """.format(values=argument_string)
            cursor.execute(cmd)
        

def lambda_handler(event, context):
    
    deserializer = TypeDeserializer()

    insert_events = [x for x in event["Records"] if x["eventName"] == "INSERT"]
    modify_events = [x for x in event["Records"] if x["eventName"] == "MODIFY"]
    remove_events = [x for x in event["Records"] if x["eventName"] == "REMOVE"]


    connection = rds_connection()
    connection.autocommit = True

    # run the inserts
    insert_records(connection, insert_events)

    # run the updates
    update_records(connection, modify_events)
    
    connection.close()

    
    return {
        'statusCode': 200,
        'body': json.dumps('Dynamo to RDS')
    }
