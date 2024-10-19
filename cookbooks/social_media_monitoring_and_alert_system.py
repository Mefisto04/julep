# -*- coding: utf-8 -*-
"""Social_Media_Monitoring_and_Alert_System.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1SasPLOzILN6c46EJGSN5GmgGQyndDdvc
"""

import uuid
import yaml
import time
from julep import Client

# UUIDs for agent and tasks
AGENT_UUID = uuid.uuid4()
MONITOR_SOCIAL_MEDIA_TASK_UUID = uuid.uuid4()
ANALYZE_TRENDS_TASK_UUID = uuid.uuid4()
SEND_ALERT_TASK_UUID = uuid.uuid4()

api_key = ""  # Your API key here
client = Client(api_key=api_key, environment="dev")

agent = client.agents.create_or_update(
    agent_id=AGENT_UUID,
    name="Social Media Monitor",
    about="An AI agent that monitors social media for keywords and trends.",
    model="gpt-4o",
)

monitor_social_media_task_def = yaml.safe_load("""
name: Monitor Social Media
input_schema:
  type: object
  properties:
    keywords:
      type: array
      items:
        type: string
main:
- prompt:
    - role: system
      content: >-
        Monitor the specified social media platforms for the following keywords:
        {{inputs[0].keywords}}.
        Return the posts containing these keywords.
  unwrap: true
- evaluate:
    posts: _
- return:
    posts: _
""")

monitor_social_media_task = client.tasks.create_or_update(
    task_id=MONITOR_SOCIAL_MEDIA_TASK_UUID,
    agent_id=AGENT_UUID,
    **monitor_social_media_task_def
)

# Define the analyze trends task
analyze_trends_task_def = yaml.safe_load("""
name: Analyze Trends
input_schema:
  type: object
  properties:
    posts:
      type: array
      items:
        type: string
    threshold:
      type: integer
main:
- prompt:
    - role: system
      content: >-
        Analyze the following posts for trends and return any posts exceeding the threshold of
        {{inputs[0].threshold}} mentions:
        {{inputs[0].posts}}.
        Return the trending posts.
  unwrap: true
- evaluate:
    trends: _
- return:
    trends: _
""")

analyze_trends_task = client.tasks.create_or_update(
    task_id=ANALYZE_TRENDS_TASK_UUID,
    agent_id=AGENT_UUID,
    **analyze_trends_task_def
)

# Define the send alert task
send_alert_task_def = yaml.safe_load("""
name: Send Alert
input_schema:
  type: object
  properties:
    trends:
      type: array
      items:
        type: string
main:
- prompt:
    - role: system
      content: >-
        Send an alert for the following trends detected on social media:
        {{inputs[0].trends}}.
        Confirm the alert has been sent.
  unwrap: true
- return:
    status: "Alert sent"
""")

send_alert_task = client.tasks.create_or_update(
    task_id=SEND_ALERT_TASK_UUID,
    agent_id=AGENT_UUID,
    **send_alert_task_def
)

def analyze_trends(posts, threshold):
    trends = [post for post in posts if posts.count(post) >= threshold]
    return {"trends": trends} if trends else {"trends": []}

def send_alert(trends):
    if not trends:
        return {"status": "No trends detected to alert."}

    input_trends = {"trends": trends}
    execution = client.executions.create(
        task_id=SEND_ALERT_TASK_UUID,
        input=input_trends
    )
    time.sleep(2)
    result = client.executions.get(execution.id)

    output = client.executions.transitions.list(execution_id=result.id).items[0].output
    return {"status": output}

keywords = ["AI", "Healthcare", "Data"]
monitor_result = {
    "posts": [
        "AI in Healthcare is revolutionizing patient care.",
        "Data-driven insights are essential for AI development.",
        "Healthcare providers are adopting AI technologies."
    ]
}

threshold = 2
trends_result = analyze_trends(monitor_result["posts"], threshold)

if trends_result.get("trends"):
    alert_result = send_alert(trends_result["trends"])
else:
    alert_result = {"status": "No trends detected."}

def print_output(monitor_result, trends_result, alert_result):
    print("Demonstrating Social Media Monitoring and Alert System:\n")
    print("Posts Monitored:")
    print(f"Posts containing specified keywords:\n{', '.join(monitor_result['posts'])}\n")
    print("Trends Analyzed:")
    print(f"Trending posts based on the defined threshold:\n{', '.join(trends_result['trends'])}\n")
    print("Alert Status:")
    print(f"Alert status: {alert_result.get('status', 'No alert sent')}\n")

print_output(monitor_result, trends_result, alert_result)

