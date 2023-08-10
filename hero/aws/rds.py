import os
import json

import psycopg2
from psycopg2 import sql

from ..api.task import READY, CLAIMED, COMPLETE, FAILED
import logging

log = logging.getLogger('hero:aws:rds')


def rds_connection():
    # send to DB
    credentials = {
        "host": "hero-database-2.cluster-c5rea6ohaa0g.us-west-2.rds.amazonaws.com",
        "database": "hero",
        "user": "heroops",
        "application_name": "hero-python",
        "port": "5432",
        "password": os.environ["HERO_DATABASE_PASSWORD"],
    }
    return psycopg2.connect(**credentials, connect_timeout=30)


def delete_queue(project: str, queue: str):
    """Deletes a queue based on queue_url"""
    cmd = """
        delete from hero.jobs
        where queue_name='{queue}' and name='{project}'
    """.format(
        queue=queue, project=project
    )
    connection = rds_connection()
    with connection.cursor() as cursor:
        cmd = sql.SQL(cmd)
        cursor.execute(cmd)
        connection.commit()
        connection.close()


def put_item(task):
    """Puts a job into the jobs table"""
    cmd = """
        insert into hero.jobs (id, queue_name, status, name, job_description)
        values ('{id}', '{queue_name}', '{status}', '{name}', '{job_description}')
    """.format(
        id=task.task_id,
        queue_name=task.queue_url,
        status=READY,
        name=task.project,
        job_description=json.dumps(task.inputs, default=str),
    )
    connection = rds_connection()
    connection.autocommit = True
    with connection.cursor() as cursor:
        cmd = sql.SQL(cmd)
        cursor.execute(cmd)
        connection.commit()
        connection.close()


def get_item(job_id: str, queue: str):
    """Gets an item from the table"""
    cmd = """
        select id, queue_name, status, name, job_description
        from hero.jobs
        where id='{job_id}' and queue_name='{queue}'
    """.format(
        job_id=job_id, queue=queue
    )
    connection = rds_connection()
    with connection.cursor() as cursor:
        cmd = sql.SQL(cmd)
        cursor.execute(cmd)
        res = [x for x in cursor]
        connection.close()
        return res


def put_items(tasks):
    """Puts a list of items into the table"""
    jobs = []
    for task in tasks:
        tmp = (
            task.task_id,
            task.queue_url,
            READY,
            task.project,
            json.dumps(task.inputs, default=str),
        )
        jobs.append(tmp)

    if len(jobs) > 0:
        argument_string = ",".join(
            "('%s', '%s', '%s', '%s', '%s')" % (b, a, x, y, z)
            for (b, a, x, y, z) in jobs
        )
        connection = rds_connection()
        connection.autocommit = True
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    "INSERT INTO hero.jobs  (id, queue_name, status, name, job_description) VALUES "
                    + argument_string
                )
            except Exception as e:
                print(str(e))


def get_items(job_ids: list[str]):
    """Gets a set of jobs based on [job_id] list"""
    connection = rds_connection()
    with connection.cursor() as cursor:
        tuple_ids = tuple(job_ids)

        cmd = """
            select job_description
            from hero.jobs
            where id in {job_ids}
        """.format(
            job_ids=tuple_ids
        )
        cmd = sql.SQL(cmd)
        cursor.execute(cmd)
        connection.close()
        res = [x for x in cursor]
        return res


def get_jobs_status_count_by_queue_url(
    project: str, queue_name: str, status: str = "working"
):
    """Gets the job description based on job_id"""
    cmd = """
        select count(*)
        from hero.jobs
        where name='{project}' and queue_name='{queue_name}' and status='{status}'
    """.format(
        project=project, queue_name=queue_name, status=status
    )
    connection = rds_connection()
    with connection.cursor() as cursor:
        cmd = sql.SQL(cmd)
        cursor.execute(cmd)
        result = cursor.fetchone()
        connection.close()
        return result[0] if len(result) > 0 else 0


def get_jobs(job_ids: list[str]):
    """Gets a set of jobs based on [job_id] list"""
    connection = rds_connection()
    with connection.cursor() as cursor:
        tuple_ids = tuple(job_ids)

        cmd = """
            select id, queue_name, status, name, job_description
            from hero.jobs
            where id in {job_ids}
        """.format(
            job_ids=tuple_ids
        )
        cmd = sql.SQL(cmd)
        cursor.execute(cmd)
        res = [x for x in cursor]
        connection.close()
        return res


def get_job(job_id: str):
    """Gets the job description based on job_id"""
    cmd = """
        select queue_name, id,  name, status, job_description, job_result
        from hero.jobs
        where id='{job_id}'
    """.format(
        job_id=job_id
    )
    connection = rds_connection()
    with connection.cursor() as cursor:
        cmd = sql.SQL(cmd)
        cursor.execute(cmd)
        res = [x for x in cursor]
        connection.close()
        return res


def delete_job(job_id: str):
    """Deletes all jobs in queue"""
    connection = rds_connection()
    connection.autocommit = True
    with connection.cursor() as cursor:
        cmd = """
            delete FROM hero.jobs
            where id = '{job_id}'
        """.format(
            job_id=job_id
        )
        cmd = sql.SQL(cmd)
        cursor.execute(cmd)


def get_next_available_job(queue_name: str, n: int = 1):
    """Gets the next job based on priority and status == READY
    It does not wait for all jobs in a priority level to complete.
    """
    connection = rds_connection()
    connection.autocommit = True
    with connection.cursor() as cursor:
        query = sql.SQL(
            """
        WITH p as (
            SELECT * FROM hero.jobs
            WHERE queue_name = {queue_name} AND
                  status = {queued_status}
            LIMIT {n} FOR UPDATE SKIP LOCKED
        ),
        u AS (
        UPDATE hero.jobs as q
        SET
            status = {claimed_status},
            start_time = NOW(),
            updated_on = NOW()
        FROM p
        WHERE p.id = q.id)
        SELECT
            p.id AS id
        FROM p
        """
        ).format(
            queue_name=sql.Literal(queue_name),
            queued_status=sql.Literal(READY),
            claimed_status=sql.Literal(CLAIMED),
            n=sql.Literal(n),
        )
        cursor.execute(query)
        job_ids = [x[0] for x in cursor]
        connection.close()
        return job_ids


def set_job_status_sqscheck(job_id: str, status: str):
    """Sets the status of a job"""
    connection = rds_connection()
    connection.autocommit = True
    with connection.cursor() as cursor:
        query = sql.SQL(
            """
        UPDATE hero.jobs
        SET
            status = {status},
            updated_on = NOW()
        WHERE id = {job_id} and
              status = {queued}
        returning id
        """
        ).format(
            status=sql.Literal(status),
            job_id=sql.Literal(job_id),
            queued=sql.Literal("pending"),
        )
        cursor.execute(query)
        res = [x[0] for x in cursor]
        connection.close()
        return res


def update_item(task_id, status):
    connection = rds_connection()
    connection.autocommit = True
    with connection.cursor() as cursor:
        cmd = """
            UPDATE hero.jobs
            SET
                status = '{status}',
                updated_on = NOW()
            WHERE id = '{job_id}'
            """.format(
            status=status, job_id=task_id
        )
        cursor.execute(cmd)
    connection.close()
