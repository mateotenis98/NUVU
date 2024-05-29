import re
import time
import boto3
import json

def get_query(question):
    try:
        bedrock = boto3.client(
            'bedrock-runtime',
            region_name='us-east-1'
        )
        input = {
            'modelId': 'anthropic.claude-3-sonnet-20240229-v1:0',
            'contentType': 'application/json',
            'accept': 'application/json'
        }
        with open("./prompt.txt", "r") as file:
            prompt_data = file.read()
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": f"{prompt_data} {question}"
                }
            ]
        })
        response = bedrock.invoke_model(
            body=body,
            modelId=input['modelId'],
            accept=input['accept'],
            contentType=input['contentType']
        )
        response_body = json.loads(response['body'].read())
        print("Response Body:", response_body)  # Añadir esto para depuración

        if 'content' in response_body:
            for content_item in response_body['content']:
                if content_item['type'] == 'text':
                    sql_query = content_item['text'].strip()
                    print("Extracted SQL Query:", sql_query)  # Añadir esto para depuración
                    return sql_query

        return ""
    except Exception as e:
        print(f"Error in get_query: {str(e)}")
        return ""

def lambda_handler(event, context):
    try:
        question = json.loads(event['body'])['question']
        text_inside = get_query(question)
        
        # Añadir depuración aquí
        print("Generated SQL Query:", text_inside)
        
        # Verificar que la consulta no esté vacía
        if not text_inside.strip():
            raise ValueError("La consulta SQL generada está vacía.")
        
        query = f"""
        {text_inside}
        """
        
        database = 'datos-demograficos'
        catalog = 'AwsDataCatalog'
        
        athena_client = boto3.client('athena')
        QueryResponse = athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={
                'Database': database,
                'Catalog': catalog
            },
            ResultConfiguration={
                'OutputLocation': 's3://foa-prod-analitycs-data-storage-bucket/datos-demograficos/'
            }
        )
        QueryID = QueryResponse['QueryExecutionId']
        time.sleep(5)
        query_results = athena_client.get_query_results(QueryExecutionId=QueryID)
        
        json_response = []
        for row in query_results['ResultSet']['Rows'][1:]:
            result = {f"column_{index}": column.get('VarCharValue', '') for index, column in enumerate(row['Data'])}
            json_response.append(result)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(json_response)
        }
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }
