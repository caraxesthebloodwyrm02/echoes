import { get_openai_client } from '../../../api/clients/openai_client';

export interface Thought {
  id: string;
  content: string;
  type: 'shower' | 'random';
  timestamp: Date;
  safety_score: number;
  emotional_impact: number;
}

export interface SafetyCheck {
  is_safe: boolean;
  score: number;
  flags: string[];
  recommendations: string[];
}

export class AIGameFeatures {
  private openaiClient: any;
  private thoughts: Thought[] = [];
  private safetyThreshold = 0.8;

  constructor() {
    this.initializeAI();
  }

  private async initializeAI() {
    try {
      this.openaiClient = get_openai_client();
    } catch (error) {
      console.warn('AI client not available, running in offline mode:', error);
    }
  }

  async generateShowerThought(context?: string): Promise<Thought | null> {
    if (!this.openaiClient) {
      return this.generateOfflineThought('shower', context);
    }

    try {
      const prompt = `Generate a "shower thought" - those sudden, profound realizations people have in the shower. Make it philosophical, insightful, and surprising. Keep it under 100 words.

${context ? `Context from game: ${context}` : ''}

The thought should be:`;

      const systemMessage = `You are a creative AI that generates profound "shower thoughts" - those moments of clarity that strike while doing mundane activities. Focus on:
- Philosophical insights
- Unexpected connections
- Human condition observations
- Paradoxes and ironies
- Keep it positive and thought-provoking`;

      const response = await this.openaiClient.generate_text(
        prompt,
        150,
        0.8,
        systemMessage
      );

      if (response) {
        const safetyCheck = await this.checkSafety(response);
        if (safetyCheck.is_safe) {
          const thought: Thought = {
            id: `shower_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            content: response.trim(),
            type: 'shower',
            timestamp: new Date(),
            safety_score: safetyCheck.score,
            emotional_impact: this.calculateEmotionalImpact(response)
          };
          this.thoughts.push(thought);
          return thought;
        }
      }
    } catch (error) {
      console.error('Failed to generate shower thought:', error);
    }

    return this.generateOfflineThought('shower', context);
  }

  async generateRandomThought(context?: string): Promise<Thought | null> {
    if (!this.openaiClient) {
      return this.generateOfflineThought('random', context);
    }

    try {
      const prompt = `Generate a random, creative thought or idea. It could be:
- A wild invention concept
- An absurd hypothetical scenario
- A creative problem-solving approach
- An unusual observation about life
- Something completely unexpected

Keep it under 120 words and make it engaging.

${context ? `Inspired by game context: ${context}` : ''}

The random thought:`;

      const systemMessage = `You are an AI that generates random, creative thoughts. Be imaginative, unexpected, and entertaining. Avoid anything harmful or inappropriate. Focus on fun, creative, or insightful ideas.`;

      const response = await this.openaiClient.generate_text(
        prompt,
        180,
        0.9,
        systemMessage
      );

      if (response) {
        const safetyCheck = await this.checkSafety(response);
        if (safetyCheck.is_safe) {
          const thought: Thought = {
            id: `random_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            content: response.trim(),
            type: 'random',
            timestamp: new Date(),
            safety_score: safetyCheck.score,
            emotional_impact: this.calculateEmotionalImpact(response)
          };
          this.thoughts.push(thought);
          return thought;
        }
      }
    } catch (error) {
      console.error('Failed to generate random thought:', error);
    }

    return this.generateOfflineThought('random', context);
  }

  private async checkSafety(content: string): Promise<SafetyCheck> {
    if (!this.openaiClient) {
      return { is_safe: true, score: 0.9, flags: [], recommendations: [] };
    }

    try {
      const prompt = `Analyze this content for safety and appropriateness. Rate it on a scale of 0-1 (1 being completely safe). Flag any concerning elements and provide recommendations if needed.

Content to analyze: "${content}"

Safety analysis:`;

      const systemMessage = `You are a content safety analyzer. Evaluate content for:
- Harmful or violent themes
- Inappropriate language
- Sensitive topics
- Potential to cause distress
- Age-appropriateness

Provide a numerical safety score (0-1) and any flags or recommendations.`;

      const response = await this.openaiClient.generate_text(
        prompt,
        200,
        0.3,
        systemMessage
      );

      if (response) {
        // Simple parsing - in production, use structured output
        const scoreMatch = response.match(/(\d+\.?\d*)/);
        const score = scoreMatch ? Math.min(1, parseFloat(scoreMatch[1])) : 0.5;

        const hasFlags = response.toLowerCase().includes('flag') ||
                        response.toLowerCase().includes('concern') ||
                        score < this.safetyThreshold;

        return {
          is_safe: score >= this.safetyThreshold,
          score,
          flags: hasFlags ? ['content_review_needed'] : [],
          recommendations: hasFlags ? ['Review content before display'] : []
        };
      }
    } catch (error) {
      console.error('Safety check failed:', error);
    }

    return { is_safe: true, score: 0.8, flags: [], recommendations: [] };
  }

  private calculateEmotionalImpact(content: string): number {
    // Simple heuristic for emotional impact
    const positiveWords = ['happy', 'joy', 'love', 'peace', 'wonder', 'amazing', 'beautiful'];
    const negativeWords = ['sad', 'angry', 'fear', 'hate', 'terrible', 'awful', 'pain'];

    const lowerContent = content.toLowerCase();
    const positiveCount = positiveWords.filter(word => lowerContent.includes(word)).length;
    const negativeCount = negativeWords.filter(word => lowerContent.includes(word)).length;

    // Return impact from -1 (very negative) to 1 (very positive)
    if (positiveCount > negativeCount) return Math.min(1, positiveCount * 0.2);
    if (negativeCount > positiveCount) return Math.max(-1, negativeCount * -0.2);
    return 0;
  }

  private generateOfflineThought(type: 'shower' | 'random', context?: string): Thought {
    const showerThoughts = [
      "If you try to fail and succeed, what have you done?",
      "We're all just collections of atoms pretending to be solid.",
      "Your brain is constantly hallucinating what reality should look like.",
      "Time is just the universe's way of preventing everything from happening at once.",
      "Every decision you make is just a step in an infinite number of possible timelines.",
      "Consciousness is just your brain trying to make sense of electrical signals.",
      "The universe is probably full of life, but we're too primitive to understand it.",
      "Death is just the universe taking back its atoms on a temporary loan.",
      "Your dreams are your brain's way of practicing for real life scenarios.",
      "Everything you experience is just your brain's interpretation of sensory data."
    ];

    const randomThoughts = [
      "What if clouds were actually giant floating cotton candy factories?",
      "Imagine if trees could talk, but only in riddles and metaphors.",
      "A library where books rewrite themselves based on what readers think.",
      "Cities where buildings grow and shrink based on how people feel about them.",
      "A world where colors have personalities and argue with each other.",
      "Time travel that only lets you visit moments when you were eating pizza.",
      "Animals that can trade skills with each other like Pokémon.",
      "A mirror that shows you not what you look like, but what you dream about.",
      "Weather that changes based on the collective mood of the population.",
      "A language where every word is a different flavor of ice cream."
    ];

    const thoughts = type === 'shower' ? showerThoughts : randomThoughts;
    const content = thoughts[Math.floor(Math.random() * thoughts.length)];

    return {
      id: `${type}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      content,
      type,
      timestamp: new Date(),
      safety_score: 1.0,
      emotional_impact: 0
    };
  }

  getThoughtsHistory(): Thought[] {
    return [...this.thoughts].sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
  }

  clearThoughtsHistory(): void {
    this.thoughts = [];
  }

  getThoughtsByType(type: 'shower' | 'random'): Thought[] {
    return this.thoughts.filter(thought => thought.type === type);
  }

  async generateThoughtBasedOnGameState(gameState: any): Promise<Thought | null> {
    const context = `Game score: ${gameState.score}, Lives: ${gameState.lives}, Level: ${Math.floor(gameState.score / 10000) + 1}`;
    return Math.random() > 0.5 ?
      await this.generateShowerThought(context) :
      await this.generateRandomThought(context);
  }
}

// Global instance
export const aiGameFeatures = new AIGameFeatures();
