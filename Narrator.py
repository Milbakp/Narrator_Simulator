import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAIAPIKEY"])
# Number to keep track of prompts
if "promptNum" not in st.session_state:
    st.session_state.promptNum  = 0
# Prompt to be carried over to the next session
if "prompt" not in st.session_state:
    st.session_state.prompt  = ""
# Story so far
if "story" not in st.session_state:
    st.session_state.story  = ""
# List of chracters, index 0 is a template
if "Characters" not in st.session_state:
    st.session_state.Characters  = [
        {'Name': 'dummyName', 'appearance':'dummyLooks', 'personality':'dummypersonality',
         'past':'dummypast', 'parthers':'dummyparthers'}
    ]
# Character images
if "images" not in st.session_state:
    st.session_state.images  = []

# Creates the characters and the initial story from the prompt
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
                - *Name:*
                - *Description:*
                - *Personality:*
             3. character 2
                - *Name:*
                - *Description:*
                - *Personality:*
             ALWAYS Start the list with 1."""},
            {'role':'user', 'content':prompt},
        ],
        n=1,
        max_tokens=1000
    )
    return response.choices[0].message.content
# Creates the chracters dialog
def createCharacter(story, info, index, action = ""):
    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages=[
            {'role':'system', 'content':"""You are a fictional character. Given a desciption of a character 
             personality, appearence, past dialog, parthers dialog and the Story so far),
             Deliver dialog and actions as if your really are this character.
             Using the knowlege of the characters past dialog and the action provided
             to create the best and most believable dialog.
             Only make dialog for your character.
             The output should focus on creating dialog that is RELEVANT TO THE action. 
             Your output should be between 1-50 words
             Your output should ALWAYS end with a clear space followed by ONLY one of the 4 emotions angry, neutral, sad, happy.
             Include the emotions in curly brackets"""},
            {'role':'user', 'content':f"""You are: {info[index]["Name"]}. Your appearence: {info[index]["appearance"]}.
             Your personality: {info[index]["personality"]}. The story so far: {story}. 
             Your previous dialog {info[index]["past"]}. 
             Your parthers dialog {info[index]["parthers"]}. The action : {action}"""}
        ],
        temperature=1.4,
        max_tokens=500
    )
    return response.choices[0].message.content

def scene_prompt(prompt):
  response = client.chat.completions.create(
      model='gpt-4o-mini',
      messages=[
           {'role':'system','content':"""
            You are tasked with generating a prompt for an AI image Generator.
            A story will be given and you have to analyse and digest the contents, and extra the main elements or essence of the story.
            Write a short prompt to produce an interesting and relevant environment art for the story.
            The style MUST be in black and white acsii art.
          """},
          {'role':'user','content':prompt}
      ],
      temperature=1,
      max_tokens=1000
  )
  return response.choices[0].message.content

def characterArtPrompt(prompt, emotion):
    response = client.chat.completions.create(
      model='gpt-4o-mini',
        messages=[
            {'role':'system','content':"""
            You are tasked with generating a prompt for an AI image Generator.
            A description of a character will be given and you have to analyse and digest the contents, and extra the main elements or essence of the character
            Write a short prompt to produce an interesting and relevant character art that represents the emotion given.
            The style MUST be in black and white acsii art.
            """},
            {'role':'user','content':f"The description: {prompt}. The emotion of the character:{emotion}"}
        ],
        temperature=1,
        max_tokens=500
    )
    return response.choices[0].message.content

def generate_art(prompt):
    response = client.images.generate(
        model='dall-e-3',
        prompt=prompt,
        size='1024x1024',
        quality='standard',
        n = 1,
        style = 'vivid'
    )
    return response.data[0].url

def generate_cart(prompt, emotion):
    response = client.images.generate(
        model='dall-e-3',
        prompt=f"""
        You are tasked with generating a prompt for an AI image Generator.
        A description of a character will be given and you have to analyse and digest the contents, and extra the main elements or essence of the character
        Write a short prompt to produce an interesting and relevant character art that represents the emotion given.
        The style MUST be in black and white acsii art.
        The description: {prompt}. The emotion of the character:{emotion}""",
        size='1024x1024',
        quality='standard',
        n = 1,
        style = 'vivid'
    )
    return response.data[0].url

#Star of the web page -------------------------------------
st.title("Narrator Simulator")
if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Kepps a log of the story
st.session_state.story = f"{st.session_state.story} Part {st.session_state.promptNum}: {st.session_state.prompt}."

if st.session_state.promptNum  == 0:
    st.caption("""Hello! I am a professional narrator! Let's have some fun role-playing!
                Give me a scenario and I'll help you get started!
                Your on your own after that!""")

    prompt = st.text_input("Give me a scenario")
    if prompt:
        st.session_state.prompt = prompt
        st.session_state.promptNum  += 1
        st.rerun()

elif st.session_state.promptNum  == 1:
        output = narrator(st.session_state.prompt)
        firstCharIndex = output.find('2.')
        secondCharIndex = output.find('3.')
        # Story
        st.session_state.story = output[:firstCharIndex]
        # Get the character 1 info
        info1 = output[firstCharIndex:secondCharIndex]
        name = info1[info1.find("*Name:*") + 8 :info1.find("*Description:*") -2]
        description = info1[info1.find("*Description:*")+14:info1.find("*Personality:*")-2]
        personality = info1[info1.find("*Personality:*")+14:]
        st.session_state.Characters.append({
            'Name': name, 'appearance': description, 'personality': personality,
         'past':'', 'parthers':''
        })
        # Character 1 image generation
        #neutral = characterArtPrompt(description, "neutral")
        #happy = characterArtPrompt(description, "happy")
        #sad = characterArtPrompt(description, "sad")
        #angry = characterArtPrompt(description, "sad")
        neutral = generate_cart(description, "neutral")
        happy = generate_cart(description, "happy")
        sad = generate_cart(description,"sad")
        angry = generate_cart(description,"angry")
        st.image(neutral)
        st.image(happy)
        st.image(sad)
        st.image(angry)
        st.session_state.images.append({'neutral':neutral, 'happy': happy, 'sad':sad,'angry':angry})

        #Get the character 2 info
        info2 = output[secondCharIndex:]
        name = info1[info2.find("*Name:*") + 8 :info2.find("*Description:*") -2]
        description = info2[info2.find("*Description:*")+14:info2.find("*Personality:*")-2]
        personality = info2[info2.find("*Personality:*")+14:]
        st.session_state.Characters.append({
            'Name': name, 'appearance': description, 'personality': personality,
         'past':'', 'parthers':''
        })
        # Character 2 image generation
        neutral = generate_cart(description, "neutral")
        happy = generate_cart(description, "happy")
        sad = generate_cart(description,"sad")
        angry = generate_cart(description,"angry")
        st.image(neutral)
        st.image(happy)
        st.image(sad)
        st.image(angry)
        st.session_state.images.append({'neutral':neutral, 'happy': happy, 'sad':sad,'angry':angry})
        #Environment prompt
        environmentPrompt = scene_prompt(st.session_state.story)
        environment = generate_art(environmentPrompt)
        st.session_state.images.append({'environment':environment})

        st.write(st.session_state.story)
        st.write(info1)
        st.write(info2)
        st.session_state.messages.append({'role':'Narrator', 'content':st.session_state.story})
        st.session_state.promptNum  += 1

        if st.button("Start Scenario"):
             st.rerun()

elif st.session_state.promptNum  == 10:
    st.write("Story Over. Sorry thats as far as you can go.")
else:
    st.session_state.prompt = st.chat_input("Continue")
    st.image(st.session_state.images[0]["environment"])
    if st.session_state.prompt:
        st.session_state.messages.append(st.session_state.prompt)
        st.write(st.session_state.prompt)
        char1 = createCharacter(st.session_state.story, st.session_state.Characters, 1, st.session_state.prompt)
        with st.chat_message(st.session_state.Characters[1]['Name']):
            st.write(char1)
        st.session_state.Characters[1]["past"] = char1
        st.session_state.Characters[2]["parthers"] = char1
        st.session_state.messages.append({'role':st.session_state.Characters[1]['Name'], 'content':char1})

        char2 = createCharacter(st.session_state.story, st.session_state.Characters, 2, st.session_state.prompt)
        with st.chat_message(st.session_state.Characters[2]['Name']):
            st.write(char2)
        st.session_state.Characters[2]["past"] = char2
        st.session_state.Characters[1]["parthers"] = char2
        st.session_state.messages.append({'role':st.session_state.Characters[2]['Name'], 'content':char2})
        st.session_state.promptNum  += 1


#st.write(st.session_state.story)
st.write(st.session_state.promptNum)
st.write(st.session_state.prompt)
