import json
import logging
import requests
import os

openai_api_key = os.environ.get("OPENAI_KEY")

openai_url = "https://api.openai.com/v1/chat/completions"

logging.basicConfig(filename='chatbot.log', level=logging.INFO)

def LoadKnowledgeBase(FilePath):
    try:
        with open(FilePath, 'r') as File:
            return json.load(File)
    except FileNotFoundError:
        logging.error(f"Knowledge base file not found: {FilePath}")
        raise

def SearchJobs(Kb, Keyword):
    Results = []
    for Pathway in Kb.get("pathways", []):
        for ClusterGroup in Pathway.get("clusterGroups", []):
            for Cluster in ClusterGroup.get("clusters", []):
                for Occupation in Cluster.get("occupations", []):
                    if (Keyword in Occupation["name"].lower() or
                            Keyword in Occupation.get("overview", "").lower()):
                        Results.append({
                            "title": Occupation["name"],
                            "description": Occupation.get("overview", "No description available."),
                            "level": Occupation.get("level", "Unknown"),
                            "salary": Occupation.get("medianAnnualSalaryinGBP", "Unknown")
                        })
    return Results

def ListAllJobs(Kb):
    JobTitles = []
    for Pathway in Kb.get("pathways", []):
        for ClusterGroup in Pathway.get("clusterGroups", []):
            for Cluster in ClusterGroup.get("clusters", []):
                for Occupation in Cluster.get("occupations", []):
                    JobTitles.append(Occupation["name"])
    return JobTitles

def GetOpenAIResponse(Prompt):
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant specialized in green jobs you are also unable to give information about the green jobs if asked about a specific one as another part of the script will manage this if asked just say sorry i dont got information on me currently."},
            {"role": "user", "content": Prompt}
        ],
        "max_tokens": 150,
        "temperature": .7
    }

    try:
        response = requests.post(openai_url, headers=headers, json=data)
        response.raise_for_status()
        response_data = response.json()
        return response_data['choices'][0]['message']['content'].strip()

    except requests.exceptions.RequestException as e:
        logging.error(f"Error with OpenAI API request: {e}")
        return "An error occurred with the OpenAI API. Please try again later."
    except KeyError as e:
        logging.error(f"Error parsing response from OpenAI API: {e}")
        return "An error occurred while processing the response. Please try again later."

def IsJobQuery(UserInput):
    Keywords = ["job", "career", "work", "occupation", "list", "green"]
    return any(Keyword in UserInput for Keyword in Keywords)

def ChatBot():

    try:
        Kb = LoadKnowledgeBase('iFATE.json')
    except FileNotFoundError:
        print("Greg: Knowledge base file not found. Please ensure 'iFATE.json' exists in the directory.")
        return

    while True:
        UserInput = input("You: ").strip().lower()
        
        if UserInput in ["exit", "quit", "bye"]:
            break

        if IsJobQuery(UserInput):
            job_found = False
            for Pathway in Kb.get("pathways", []):
                for ClusterGroup in Pathway.get("clusterGroups", []):
                    for Cluster in ClusterGroup.get("clusters", []):
                        for Occupation in Cluster.get("occupations", []):
                            job_name = Occupation["name"].lower() 
                            
                            if job_name in UserInput: 
                                print(f"I found the job you're looking for: {Occupation['name']}")
                                print(f"Details for {Occupation['name']}:")
                                print(f"Description: {Occupation.get('overview', 'No description available.')}")
                                print(f"Level: {Occupation.get('level', 'Unknown')}")
                                print(f"Median Annual Salary: £{Occupation.get('medianAnnualSalaryinGBP', 'Unknown')}")
                                job_found = True
                                break
                        if job_found:
                            break
                if job_found:
                    break

            if not job_found:
                if "list" in UserInput or "what green" in UserInput:
                    AllJobs = ListAllJobs(Kb)
                    if AllJobs:
                        print("Here are all the green jobs available:")
                        for I, Title in enumerate(AllJobs, 1):
                            print(f"{I}. {Title}")
                    else:
                        print("Greg: No jobs found in the knowledge base.")
                    continue

                FoundJobs = SearchJobs(Kb, UserInput)
                if FoundJobs:
                    print("Here are some green jobs that match your interests:")
                    for Job in FoundJobs:
                        print(f"\nJob Title: {Job['7title']}")
                        print(f"Description: {Job['description']}")
                        print(f"Level: {Job['level']}")
                        print(f"Median Annual Salary: £{Job['salary']}")
                    print("I found some green jobs!")
                    
                    job_query = input("\nAsk me more about any job. For example, type 'Tell me more about [Job Name]'\nYou: ").strip().lower()
                    if "tell me more about" in job_query:
                        job_name = job_query.replace("tell me more about", "").strip()
                        matched_jobs = [job for job in FoundJobs if job_name in job['title'].lower()]
                        if matched_jobs:
                            job = matched_jobs[0]
                            print(f"\nDetails for {job['title']}:")
                            print(f"Description: {job['description']}")
                            print(f"Level: {job['level']}")
                            print(f"Median Annual Salary: £{job['salary']}")
                        else:
                            print(f"Greg: Sorry, I couldn't find a job by the name '{job_name}'. Please make sure you typed it correctly.")
                else:
                    print("Greg: I couldn't find any green jobs related to that. Let's refine your search.")

        else:
            openai_response = GetOpenAIResponse(UserInput)
            print(f"Greg: {openai_response}")


if __name__ == "__main__":
    ChatBot()
