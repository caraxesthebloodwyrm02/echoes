# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Solar Salesman Tools for Staten Island, NY
# Goal: Equip a solar salesman with tools for mapping leads, timing pitches, drafting natural pitches, and convincing with blended persuasion.
# Tools: HomeworkTool (prep), RealtimeTool (live use).
# Leverages codebase: minicon for OpenAI API, search_web for data.

import sys

sys.path.append("e:/Projects/Development")

from ai_modules.minicon.config import Config


class HomeworkTool:
    def __init__(self):
        self.config = Config.from_env()
        self.client = self.config.openai_client

    def map_leads(self, area="Staten Island, NY"):
        # Mock leads for demo; in real, use search_web
        leads = [
            "Homeowners in suburban areas with high energy bills",
            "Small businesses in industrial zones",
            "Apartment complexes interested in community solar",
        ]
        return f"Shortlist for {area}: {leads}"

    def draft_pitch(self, focus="clean energy impact"):
        prompt = f"Draft a concise, natural pitch for solar conversion focusing on {focus}. Make it iterative and conversational."
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    def blend_persuasion(self, pitch):
        prompt = f"Enhance this pitch with marketing techniques, human instincts, cleanliness promise, and daily life impact: {pitch}"
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content


class RealtimeTool:
    def __init__(self):
        self.config = Config.from_env()
        self.client = self.config.openai_client

    def identify_timing(self, prospect="homeowner"):
        # Analyze best times
        prompt = f"Suggest optimal timing for pitching solar to a {prospect} in Staten Island, considering attentiveness and energy concerns."
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    def practice_pitch(self, pitch, feedback="more natural"):
        prompt = f"Refine this pitch for smoothness: {pitch}. Feedback: {feedback}"
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    def realtime_convince(self, objection="cost"):
        prompt = f"Handle objection '{objection}' in solar pitch, blending persuasion techniques."
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content


# Usage
if __name__ == "__main__":
    homework = HomeworkTool()
    print("Homework - Leads:", homework.map_leads())
    pitch = homework.draft_pitch()
    print("Draft Pitch:", pitch)
    enhanced = homework.blend_persuasion(pitch)
    print("Enhanced Pitch:", enhanced)

    realtime = RealtimeTool()
    print("Timing:", realtime.identify_timing())
    refined = realtime.practice_pitch(pitch)
    print("Refined Pitch:", refined)
    handle = realtime.realtime_convince("too expensive")
    print("Objection Handling:", handle)
