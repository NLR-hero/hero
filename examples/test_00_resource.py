import boto3
import hero as hq

hq.session.get_session()

def test_resource():
    project = hq.session.get_project()
    queue = hq.session.get_queue()

    dyn_resource = boto3.resource("dynamodb")
    table = dyn_resource.Table("hero-dynamodb-project-queue-names")
    table.load()


   

