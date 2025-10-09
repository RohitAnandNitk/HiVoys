# from src.STT.stt_service import transcribe_audio
# from src.LLM.groq_llm import GroqLLM

# # Initialize LLM once to avoid reloading every request
# groq_llm = GroqLLM()
# groq_model = groq_llm.get_model()
# conversation_history = []

# def process_audio(audio_file):
#     """
#     Handles audio from frontend:
#     1 Transcribe audio → text
#     2 Get LLM response
#     """

#     # Step 1: Transcribe the uploaded audio
#     transcription_text = transcribe_audio(audio_file)

#     # Step 2: Append user input to conversation history
#     conversation_history.append({"role": "user", "content": transcription_text})

#     # Step 3: Get LLM response
#     response_text = groq_model.invoke(conversation_history)
#     conversation_history.append({"role": "assistant", "content": response_text})

#     return {
#         "message": "Audio processed successfully!",
#         "transcription": transcription_text,
#         "llm_response": response_text
#     }
