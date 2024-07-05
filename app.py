import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
import re

st.set_page_config(
    page_title="YT-Transcripter",
    page_icon="favicon.ico",
    layout="centered",
    initial_sidebar_state="auto",
)

load_dotenv()  # Load all the environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

prompt = """Title of the Video: [Insert Video Title Here]

Video Length: [Insert Video Length Here]

Channel Name: [Insert Channel Name Here]

Summary Guidelines:

1. **Main Points**: Identify and summarize the primary topics and key arguments discussed in the video. Ensure all significant details are included.

2. **Highlights**: Capture noteworthy moments, surprising facts, or important quotes that stand out in the video.

3. **Structure**: Break down the video into sections such as introduction, main content, and conclusion, providing a clear outline.

4. **Speaker Information**: Mention the speaker(s) involved, including their names and relevant credentials or background information.

5. **Visuals and Graphics**: Describe any critical visuals, graphics, or on-screen text that enhance the understanding of the content.

6. **Examples and Anecdotes**: Include any examples, case studies, or personal anecdotes shared to illustrate key points.

7. **Conclusion and Takeaways**: Summarize the closing remarks and list any actionable takeaways or advice provided.

**Example Summary:**

**Title of the Video:** "The Science of Sleep: How to Improve Your Sleep Quality"

**Video Length:** 15:32

**Channel Name:** Health Insights

**Summary:**

**Main Points:**
- Importance of sleep for health and well-being.
- Stages of sleep: REM and non-REM.
- Factors affecting sleep quality: diet, exercise, environment.
- Tips for better sleep: consistent schedule, restful environment.

**Highlights:**
- Quote: "Sleep is as crucial as nutrition and exercise" - Dr. Smith.
- Fact: "Adults need 7-9 hours of sleep per night."

**Structure:**
- Introduction: Overview of sleep's importance.
- Main Content: Sleep stages, factors affecting sleep.
- Conclusion: Tips for improving sleep.

**Speaker Information:**
- Dr. Jane Smith, a sleep specialist with 20 years of experience.

**Visuals and Graphics:**
- Diagrams of the sleep cycle.
- Charts on the effects of poor sleep.

**Examples and Anecdotes:**
- Dr. Smith's anecdote about a patient who improved sleep quality by changing bedtime routine.

**Conclusion and Takeaways:**
- Prioritize sleep for better health.
- Key takeaway: Consistent sleep schedule and restful environment.

**Instructions:**
1. Watch the video thoroughly.
2. Note the main points, highlights, structure, speakers, visuals, examples, and conclusion.
3. Write a concise summary using the provided format.
4. Ensure the summary is clear, informative, and captures the video's essence."""

# Function to extract the transcript data from YouTube videos
def extract_transcript_details(youtube_video_url):
    try:
        video_id = get_video_id(youtube_video_url)
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

        transcript = " ".join([entry["text"] for entry in transcript_text])
        return transcript

    except NoTranscriptFound:
        return "No subtitles found for this video."
    except TranscriptsDisabled:
        return "Subtitles are disabled for this video."
    except Exception as e:
        raise e

# Function to generate content based on the transcript and prompt
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Function to extract video ID from the URL
def get_video_id(url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = get_video_id(youtube_link)
    if video_id:
        embed_url = f"https://www.youtube.com/embed/{video_id}?autoplay=1"
        st.markdown(
            f"""
            <style>
            .video-container {{
                position: relative;
                padding-bottom: 56.25%;
                height: 0;
                overflow: hidden;
                max-width: 100%;
                background: #000;
                margin: 0 auto;
            }}
            .video-container iframe {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
            }}
            </style>
            <div class="video-container">
                <iframe src="{embed_url}" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.error("Invalid YouTube URL")

if st.button("Get Detailed Notes"):
    if video_id:
        transcript_text = extract_transcript_details(youtube_link)
        if "No subtitles found" in transcript_text or "Subtitles are disabled" in transcript_text:
            st.error(transcript_text)
        elif transcript_text:
            summary = generate_gemini_content(transcript_text, prompt)
            st.markdown("## Detailed Notes:")
            st.write(summary)
        else:
            st.error("Failed to retrieve transcript.")
    else:
        st.error("Please enter a valid YouTube URL.")
