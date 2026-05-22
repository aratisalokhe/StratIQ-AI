import os
from crewai import Agent, Task, Crew, Process

# YOUR API KEYS
os.environ["GROQ_API_KEY"] = "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"

# AGENT 1 - RESEARCHER
researcher = Agent(
    role="Market Researcher",
    goal="Find latest market information about the given topic",
    backstory="You are an expert market researcher with 10 years experience finding market data, news and trends.",
    verbose=True,
    llm="groq/llama-3.3-70b-versatile"
)

# AGENT 2 - ANALYST
analyst = Agent(
    role="Business Analyst",
    goal="Analyze research and find key insights, opportunities and risks",
    backstory="You are a senior business analyst who gives clear actionable insights.",
    verbose=True,
    llm="groq/llama-3.3-70b-versatile"
)

# AGENT 3 - REPORTER
reporter = Agent(
    role="Report Writer",
    goal="Write a clear professional business report",
    backstory="You write excellent executive business reports.",
    verbose=True,
    llm="groq/llama-3.3-70b-versatile"
)

# TASKS
research_task = Task(
    description="Research this topic in detail: {topic}. Find latest news, trends, key players, market size and important data.",
    expected_output="A detailed research summary with at least 5 facts and data points.",
    agent=researcher
)

analysis_task = Task(
    description="Analyze the research about {topic}. Find top 3 opportunities and top 3 risks.",
    expected_output="A structured analysis with opportunities and risks.",
    agent=analyst,
    context=[research_task]
)

report_task = Task(
    description="""Write a professional report about {topic} using this exact format:

# MarketMind Report

## Executive Summary

## Key Market Insights

## Opportunities

## Risks

## Recommendation
    """,
    expected_output="A complete formatted business report.",
    agent=reporter,
    context=[research_task, analysis_task]
)

# RUN
crew = Crew(
    agents=[researcher, analyst, reporter],
    tasks=[research_task, analysis_task, report_task],
    process=Process.sequential,
    verbose=True
)

result = crew.kickoff(inputs={"topic": "Electric Vehicle market in India 2024"})

print("\n" + "="*50)
print("FINAL REPORT")
print("="*50)
print(result)

# SAVE REPORT
with open("report.md", "w") as f:
    f.write(str(result))
print("\nReport saved to report.md!")