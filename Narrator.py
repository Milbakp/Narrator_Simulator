import streamlit as st
from openai import OpenAI

with open('style.css') as f:
    css = f.read()
client = OpenAI(api_key=st.secrets["OPENAIAPIKEY"])
promptNum = 0
st.title("Narrator Simulator")
def narrator(prompt):
    global promptNum
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages= [
            {'role':'system', 'content':"""You are a highly successful author and Narrator. 
             Given a starting scenario. create a short introduction to the story, about 150-200 words long,
              that takes inspiration from the scenario. 
             Create 2 characters in this world. given them a name,desciption of their looks and general
             personality.
             Your output should follow the following format:
             1.Story
             2. character 1
                - name
                - description
                - personality
             3. character 2
                - name
                - description
                - personality"""},
            {'role':'user', 'content':prompt},
        ],
        n=1,
        max_tokens=1000
    )
    promptNum += 1
    return response.choices[0].message.content

def createCharacter(prompt, memory):
    name = memory[:memory.find('Name')]
    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages=[
            {'role':'system', 'content':"""You are a fictional character. Given a desciption of the character and their memories,
             Deliver dialog and actions as if your really are this character.
             Your output should be between 1-50 words
             Your output should end with a clear space followed by one of the 4 emotion angry, neutral, sad, happy.
             Include the emotions in curly brackets"""},
            {'role':'system', 'content':f"You is: {name}. Your memory: {memory}. The action : {prompt}"}
        ],
        temperature=1.4,
        max_tokens=1000
    )
    return response.choices[0].message.content

if promptNum == 0:
    st.caption("""Hello! I am a professional narrator! Let's have some fun role-playing!
                Give me a scenario and I'll help you get started!
                Your on your own after that!""")

    prompt = st.text_input("Give me a scenario")
    if 'startButton' not in st.session_state:
        st.session_state.startButton = 'Start'

    startButton = st.button(st.session_state.startButton)

    #startButton = st.button("Start Playing")

    if startButton:
        st.session_state.startButton = 'Stop Playing/Restart'
        output = narrator(prompt)
        firstCharIndex = output.find('2.')
        secondCharIndex = output.find('3.')
        story = output[:firstCharIndex]
        memory1 = output[firstCharIndex:secondCharIndex]
        memory2 = output[secondCharIndex:]
        st.write(story)
        st.write(memory1)
        st.write(memory2)
        char1 = createCharacter(story, memory1)
        char2 = createCharacter(story, memory2)
        st.write(char1)
        st.write(char2)
        promptNum += 1
        prompt = st.text_input("Continue the Story")


    


"""st.markdown(f'<style>{css}</style> Testing', unsafe_allow_html=True)
st.write("Testing")
st.write("Testting")"""