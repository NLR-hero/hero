""" 
{    "eventName" : ["INSERT", "UPDATE"] }
"""
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
        "password": "8fc2a2e2-ed9e-413d-996a-72da94e11c5c",
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
        if "item" in job_description.keys():
            tmp = (
                job_description["id"],
                job_description["queue"],
                "ready",
                job_description.get("project", "None"),
                json.dumps(job_description["item"], default=str),
            )
            jobs.append(tmp)
        else:
            print("WTF", job_description)

    if len(jobs) > 0:
        argument_string = ",".join(
            "('%s', '%s', '%s', '%s', '%s')" % (b, a, x, y, z)
            for (b, a, x, y, z) in jobs
        )
        # print(argument_string)
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    "INSERT INTO hero.jobs  (id, queue_name, status, name, job_description) VALUES "
                    + argument_string
                )
            except Exception as e:
                print(str(e))


def update_records(connection, records):
    print("RDS update_records =====> ", len(records))

    jobs = {}
    for record in records:
        job_description = {
            k: deserializer.deserialize(v)
            for k, v in record["dynamodb"]["NewImage"].items()
        }
        tmp_status = job_description.get("status", "Unknown")
        jobs[tmp_status] = jobs.get(tmp_status, [])
        jobs[tmp_status].append(job_description)

    print(jobs.keys())

    if len(jobs.get("claimed", [])) > 0:
        argument_string = (
            "(" + ",".join(f"'{job['id']}'" for job in jobs["claimed"]) + ")"
        )
        with connection.cursor() as cursor:
            cmd = """
                   UPDATE hero.jobs
                    SET
                        status = 'claimed',
                        updated_on = NOW()
                    WHERE id IN {job_ids}
            """.format(
                job_ids=argument_string
            )
            cursor.execute(cmd)

    # add results
    elif len(jobs.get("done", [])) > 0:
        argument_string = "(" + ",".join(f"'{job['id']}'" for job in jobs["done"]) + ")"
        with connection.cursor() as cursor:
            cmd = """
                   UPDATE hero.jobs
                    SET
                        status = 'done',
                        updated_on = NOW()
                    WHERE id IN {job_ids}
            """.format(
                job_ids=argument_string
            )
            cursor.execute(cmd)


def lambda_handler(event, context):
    deserializer = TypeDeserializer()

    insert_events = [x for x in event["Records"] if x["eventName"] == "INSERT"]
    modify_events = [x for x in event["Records"] if x["eventName"] == "MODIFY"]
    remove_events = [x for x in event["Records"] if x["eventName"] == "REMOVE"]

    print(
        f"INSERT --> {len(insert_events)}.  MODIFY --> {len(modify_events)}. REMOVE --> {len(remove_events)}"
    )

    connection = rds_connection()
    connection.autocommit = True

    # run the inserts
    insert_records(connection, insert_events)

    # run the updates
    update_records(connection, modify_events)

    connection.close()

    # TODO implement
    return {"statusCode": 200, "body": json.dumps("Dynamo to RDS")}
