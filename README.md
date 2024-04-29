# Event Driven GenAI app


## Endpoints
1. Send Task to API Gateway
    - **URL**: `http://localhost:5000/send-task`
    - **Method**: POST
    - **Request Body**:
        ```json
       {
          "task": {
             "name": "summary sample",
             "action": "summary",
             "payload": {
                "text": "This is sample text."
             }
          }
       }
        ```
    - **Response**:
       ```json
       {
          "response": {
          "status": "Task sent",
           "task_id": "d0001447"
          }
       }
       ```

2. Get Task from API Gateway
    - **URL**: `http://localhost:5000/get-result/<task_id>`
    - **Method**: GET 
    - **Response**:
       ```json
       {
          "response": {
             "result": "Processed task Action Result: d0001447 : summary",
             "task_id": "d0001447"
          }
       }
       ```
      

TODO:
- syncronous and asyncronous services 
- chat api on multiple LLMs 
- streaming chat on llm
- text to image model - long running, load balanced, limited request
- prompt management 
- autonuze.me service management
- predictive analysis tools 