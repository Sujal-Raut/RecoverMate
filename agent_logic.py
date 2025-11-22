import os
import random
from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI

GOOGLE_API_KEY = "AIzaSyAPifd7wOn1iCzXxBMiXsMOgk3vdwXIv0E"


class RecoveryOrchestrator:
    def __init__(self):
        self.api_key = GOOGLE_API_KEY
        self.llm = None
        self.is_configured = True
        
        # Try to connect to the REAL AI
        try:
            if "AIza" not in self.api_key: 
                self.is_configured = False
                raise Exception("Key Missing")
            
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                verbose=True,
                temperature=0.7,
                google_api_key=self.api_key
            )
        except:
            print("⚠️ AI Connection Failed. Switching to Simulation Mode.")
            self.llm = None

        # Define Agents
        self.guardian = Agent(
            role='The Guardian',
            goal='Provide immediate crisis intervention.',
            backstory="Expert crisis specialist. Firm and directive.",
            llm=self.llm,
            allow_delegation=False
        )

        self.reflector = Agent(
            role='The Reflector',
            goal='Validate feelings.',
            backstory="Empathetic therapeutic companion.",
            llm=self.llm,
            allow_delegation=False
        )

        self.strategist = Agent(
            role='The Strategist',
            goal='Provide habit strategies.',
            backstory="Habit coach. Logical and structured.",
            llm=self.llm,
            allow_delegation=False
        )

        self.agents = {
            "sos": self.guardian,
            "journal": self.reflector,
            "general": self.strategist
        }

    def get_response(self, user_input, context_type="general"):
        active_agent = self.agents.get(context_type, self.agents["general"])

        # 1. TRY REAL AI EXECUTION
        try:
            if not self.llm: raise Exception("Simulation Triggered")
            
            task = Task(
                description=f"User Input: '{user_input}'. Respond helpfully.",
                expected_output="A clear text response.",
                agent=active_agent
            )
            
            #Crew Execution

            crew = Crew(agents=[active_agent], tasks=[task], verbose=True)
            result = crew.kickoff()
            return {"agent_name": active_agent.role, "content": str(result)}

        # 2. EMERGENCY SIMULATION (If API Fails)
        except Exception as e:
            print(f"⚠️ Using Fallback Response due to: {e}")
            
            fallback = ""
            
            # --- RANDOMIZED RESPONSES FOR DEMO ---
            if context_type == "sos":
                options = [
                    "I hear that you are struggling. Take a deep breath right now. Inhale for 4 seconds, hold for 7, exhale for 8. Do this three times.",
                    "This urge will pass. Distract yourself immediately—drink a glass of cold water or splash your face.",
                    "You are stronger than this craving. Look around the room and name 5 blue objects. Ground yourself in the present."
                ]
                fallback = random.choice(options)
            
            elif context_type == "journal":
                # I added 5 variations here so it doesn't repeat
                options = [
                    "Thank you for sharing that. It sounds like a challenging moment. I appreciate your honesty. How did you feel immediately after writing this down?",
                    "I hear you. It takes a lot of courage to admit that. What is one small thing you can do for yourself right now to feel a bit better?",
                    "That sounds heavy to carry alone. Remember, recovery isn't a straight line. Be gentle with yourself today.",
                    "Writing this down is a huge step. You are processing your emotions instead of suppressing them. That is progress.",
                    "I understand. Sometimes just getting the thoughts out of your head helps. What would you tell a friend who felt this way?"
                ]
                fallback = random.choice(options)
            
            else:
                # Strategy variations
                options = [
                    "That is a great question. To build this habit, start small (the 2-minute rule). Consistency is more important than intensity.",
                    "Breaking habits is hard. Try to identify the 'cue' that triggers this behavior. Change the environment to remove that cue.",
                    "Focus on replacing the bad habit with a neutral one, rather than just stopping. What could you do instead?"
                ]
                fallback = random.choice(options)

            return {
                "agent_name": f"{active_agent.role}", 
                "content": fallback
            }

# Instantiate
manager = RecoveryOrchestrator()