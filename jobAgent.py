import os
from dotenv import load_dotenv
from langchain_core.tools import tool          # 补上这一行
from langchain_classic.agents import create_openai_tools_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import pymysql
import json

load_dotenv()

@tool                                          # 加上装饰器
def get_current_weather(city: str) -> str:
    """获取指定城市的当前天气信息。当用户询问某个城市的天气时使用此工具。"""
    return f"{city}今天的天气是晴天，气温 25℃，微风。"

@tool                                          # 加上装饰器
def get_job_list_size(city: str,jobDate: str,jobName: str) -> str:
    """获取指定城市{city},{jobDate}指定日期包含{jobName}职位名称的招聘岗位数"""
    conn = pymysql.connect(host='192.168.154.128', user='cyd', password='Cyd!123456789', database='collect-data',
                           charset='utf8mb4')
    try:
        cursor = conn.cursor()

        job_name_search = f"%{jobName}%"

        # 执行统计 SQL
        cursor.execute("SELECT COUNT(*) FROM boss_job_details where job_name like %s and created_time = %s and city_name = %s and boss_online = 1", (job_name_search, jobDate, city))

        # 获取结果（COUNT(*) 只会返回一行一列，所以用 fetchone()）
        count = cursor.fetchone()[0]

        return f"城市{city}指定日期{jobDate}包含职位名称{jobName}的招聘岗位数{count}。"

    finally:
        cursor.close()
        conn.close()

@tool                                          # 加上装饰器
def get_job_list(city: str,jobDate: str,jobName: str) -> str:
    """获取指定城市{city},{jobDate}指定日期包含{jobName}职位名称的所有招聘岗位列表"""
    conn = pymysql.connect(host='192.168.154.128', user='cyd', password='Cyd!123456789', database='collect-data',
                           charset='utf8mb4')
    try:
        cursor = conn.cursor()

        job_name_search = f"%{jobName}%"

        # 执行统计 SQL
        cursor.execute("SELECT * FROM boss_job_details where job_name like %s and created_time = %s and city_name = %s and boss_online = 1", (job_name_search, jobDate, city))

        # 获取记录列表
        results = cursor.fetchall()

        if not results:
            return f"没有查询到数据。"

        return json.dumps(results, ensure_ascii=False, default=str)

    finally:
        cursor.close()
        conn.close()


llm = ChatOpenAI(
    model="MiniMax-M2.7",
    base_url="https://api.minimaxi.com/v1",
    api_key=os.getenv("MINIMAX_API_KEY"),
    temperature=0,
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个乐于助人的AI助手。请根据用户的问题，合理使用工具来获取信息并给出准确的回答。"),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

tools = [get_current_weather,get_job_list_size,get_job_list]
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

if __name__ == "__main__":
    response = agent_executor.invoke({"input": "武汉2026-09-22日java所有招聘职位列表？"})
    print("最终回答:", response["output"])