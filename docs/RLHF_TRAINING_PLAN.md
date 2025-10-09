# Reinforcement Learning & Fine-Tuning - Implementation Plan

## Overview

Implement Reinforcement Learning from Human Feedback (RLHF) to continuously improve the assistant based on user interactions and feedback.

## RLHF Pipeline

```
┌─────────────┐
│User Interacts│
│with Assistant│
└──────┬───────┘
       ↓
┌──────────────────┐     ┌──────────────────┐
│ Collect Feedback │ ──→ │  Build Dataset   │
│ (thumbs, ratings)│     │ (prompts+responses)│
└──────────────────┘     └─────────┬────────┘
                                   ↓
                         ┌──────────────────┐
                         │  Train Reward    │
                         │     Model        │
                         └─────────┬────────┘
                                   ↓
                         ┌──────────────────┐
                         │  PPO Training    │
                         │  (Policy Update) │
                         └─────────┬────────┘
                                   ↓
                         ┌──────────────────┐
                         │   Evaluation     │
                         │   & Deployment   │
                         └──────────────────┘
```

## 1. Feedback Collection

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
import json

@dataclass
class FeedbackEntry:
    """Single feedback entry."""
    query: str
    response: str
    feedback_type: str  # thumbs_up, thumbs_down, rating, correction
    rating: Optional[int] = None  # 1-5
    correction: Optional[str] = None
    timestamp: datetime = None
    metadata: Dict = None

class FeedbackCollector:
    """
    Collect and store user feedback.
    """

    def __init__(self, storage_path: str = "data/feedback.jsonl"):
        self.storage_path = storage_path
        self.feedback_buffer: List[FeedbackEntry] = []

    def collect(
        self,
        query: str,
        response: str,
        feedback_type: str,
        rating: Optional[int] = None,
        correction: Optional[str] = None,
        **metadata,
    ):
        """Collect feedback from user."""
        entry = FeedbackEntry(
            query=query,
            response=response,
            feedback_type=feedback_type,
            rating=rating,
            correction=correction,
            timestamp=datetime.now(),
            metadata=metadata,
        )

        self.feedback_buffer.append(entry)
        self._persist(entry)

    def _persist(self, entry: FeedbackEntry):
        """Persist feedback to storage."""
        with open(self.storage_path, 'a') as f:
            f.write(json.dumps(entry.__dict__, default=str) + '\n')

    def get_training_data(
        self,
        min_rating: int = 4,
        max_samples: int = 10000,
    ) -> List[Dict]:
        """Get training data from feedback."""
        with open(self.storage_path) as f:
            entries = [json.loads(line) for line in f]

        # Filter by rating
        positive = [
            e for e in entries
            if e.get('rating', 0) >= min_rating
            or e['feedback_type'] == 'thumbs_up'
        ]

        negative = [
            e for e in entries
            if e.get('rating', 0) < min_rating
            or e['feedback_type'] == 'thumbs_down'
        ]

        return {
            'positive': positive[:max_samples],
            'negative': negative[:max_samples],
        }
```

## 2. Reward Model

```python
import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer, Trainer, TrainingArguments
from datasets import Dataset

class RewardModel(nn.Module):
    """
    Model to predict quality of responses.
    """

    def __init__(self, base_model: str = "microsoft/deberta-v3-base"):
        super().__init__()

        self.encoder = AutoModel.from_pretrained(base_model)
        self.tokenizer = AutoTokenizer.from_pretrained(base_model)

        # Reward head
        hidden_size = self.encoder.config.hidden_size
        self.reward_head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size // 2, 1),
        )

    def forward(
        self,
        input_ids,
        attention_mask,
    ):
        """Forward pass."""
        outputs = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask,
        )

        # Pool
        pooled = outputs.last_hidden_state[:, 0, :]  # [CLS] token

        # Reward
        reward = self.reward_head(pooled)

        return reward

    def predict_reward(
        self,
        query: str,
        response: str,
    ) -> float:
        """Predict reward for query-response pair."""
        # Format input
        text = f"Query: {query}\nResponse: {response}"

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
        )

        with torch.no_grad():
            reward = self.forward(
                inputs['input_ids'],
                inputs['attention_mask'],
            )

        return float(reward.item())

class RewardModelTrainer:
    """
    Train reward model on feedback data.
    """

    def __init__(self):
        self.model = RewardModel()
        self.feedback_collector = FeedbackCollector()

    def prepare_dataset(self) -> Dataset:
        """Prepare training dataset."""
        feedback_data = self.feedback_collector.get_training_data()

        examples = []

        # Positive examples (label=1)
        for entry in feedback_data['positive']:
            examples.append({
                'text': f"Query: {entry['query']}\nResponse: {entry['response']}",
                'label': 1.0,
            })

        # Negative examples (label=0)
        for entry in feedback_data['negative']:
            examples.append({
                'text': f"Query: {entry['query']}\nResponse: {entry['response']}",
                'label': 0.0,
            })

        return Dataset.from_list(examples)

    def train(
        self,
        output_dir: str = "models/reward_model",
        num_epochs: int = 3,
    ):
        """Train reward model."""
        dataset = self.prepare_dataset()

        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=8,
            learning_rate=2e-5,
            logging_steps=100,
            save_steps=500,
            evaluation_strategy="steps",
            eval_steps=500,
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=dataset,
        )

        trainer.train()

        # Save model
        self.model.save_pretrained(output_dir)
```

## 3. PPO Training

```python
from trl import PPOTrainer, PPOConfig, AutoModelForCausalLMWithValueHead
from transformers import AutoTokenizer

class PPOAssistantTrainer:
    """
    PPO trainer for assistant policy.
    """

    def __init__(
        self,
        model_name: str = "microsoft/phi-2",
        reward_model: RewardModel = None,
    ):
        # Load policy model
        self.model = AutoModelForCausalLMWithValueHead.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        # Reward model
        self.reward_model = reward_model or RewardModel()

        # PPO config
        self.ppo_config = PPOConfig(
            learning_rate=1e-5,
            batch_size=8,
            mini_batch_size=4,
            ppo_epochs=4,
            target_kl=0.1,
            init_kl_coef=0.2,
        )

        # Create trainer
        self.trainer = PPOTrainer(
            config=self.ppo_config,
            model=self.model,
            tokenizer=self.tokenizer,
        )

    async def train_step(self, queries: List[str]):
        """Single PPO training step."""

        # Generate responses
        query_tensors = [
            self.tokenizer.encode(q, return_tensors="pt")[0]
            for q in queries
        ]

        response_tensors = []
        for query_tensor in query_tensors:
            response = self.model.generate(
                query_tensor.unsqueeze(0),
                max_new_tokens=256,
                do_sample=True,
                top_p=0.95,
                temperature=0.8,
            )
            response_tensors.append(response[0])

        # Get rewards
        rewards = []
        for query, response_tensor in zip(queries, response_tensors):
            response_text = self.tokenizer.decode(
                response_tensor,
                skip_special_tokens=True,
            )
            reward = self.reward_model.predict_reward(query, response_text)
            rewards.append(torch.tensor(reward))

        # PPO step
        stats = self.trainer.step(query_tensors, response_tensors, rewards)

        return stats

    async def train(
        self,
        num_epochs: int = 100,
        queries_per_epoch: int = 32,
    ):
        """Full PPO training loop."""

        for epoch in range(num_epochs):
            # Sample queries from feedback
            queries = self._sample_queries(queries_per_epoch)

            # Train step
            stats = await self.train_step(queries)

            # Log
            print(f"Epoch {epoch}: {stats}")

            # Save checkpoint
            if epoch % 10 == 0:
                self.model.save_pretrained(f"checkpoints/ppo_epoch_{epoch}")

    def _sample_queries(self, n: int) -> List[str]:
        """Sample queries from feedback data."""
        feedback_data = FeedbackCollector().get_training_data()
        all_queries = [e['query'] for e in feedback_data['positive'][:n]]
        return all_queries
```

## 4. Continuous Learning

```python
import asyncio
from collections import deque

class ContinuousLearner:
    """
    Continuously learn from interactions.
    """

    def __init__(
        self,
        buffer_size: int = 1000,
        train_threshold: int = 100,
    ):
        self.feedback_buffer = deque(maxlen=buffer_size)
        self.train_threshold = train_threshold

        self.reward_trainer = RewardModelTrainer()
        self.ppo_trainer = PPOAssistantTrainer()

        self.learning_active = False

    async def add_interaction(
        self,
        query: str,
        response: str,
        feedback: Dict,
    ):
        """Add interaction to buffer."""
        self.feedback_buffer.append({
            'query': query,
            'response': response,
            'feedback': feedback,
        })

        # Check if ready to train
        if len(self.feedback_buffer) >= self.train_threshold:
            await self.trigger_training()

    async def trigger_training(self):
        """Trigger training cycle."""
        if self.learning_active:
            return

        self.learning_active = True

        try:
            # 1. Update reward model
            print("Training reward model...")
            self.reward_trainer.train(num_epochs=1)

            # 2. Update policy with PPO
            print("Running PPO training...")
            await self.ppo_trainer.train(
                num_epochs=10,
                queries_per_epoch=16,
            )

            # 3. Evaluate
            print("Evaluating...")
            metrics = await self.evaluate()

            print(f"Training complete. Metrics: {metrics}")

        finally:
            self.learning_active = False

    async def evaluate(self) -> Dict:
        """Evaluate current model."""
        # Hold-out test set
        test_queries = self._get_test_queries()

        total_reward = 0
        for query in test_queries:
            response = await self._generate_response(query)
            reward = self.reward_trainer.model.predict_reward(query, response)
            total_reward += reward

        avg_reward = total_reward / len(test_queries)

        return {
            'average_reward': avg_reward,
            'test_samples': len(test_queries),
        }
```

## 5. A/B Testing

```python
import random

class ABTestingFramework:
    """
    A/B test different model versions.
    """

    def __init__(self):
        self.variants = {
            'control': {'model': 'qwq-32b', 'config': {}},
            'variant_a': {'model': 'qwq-32b-finetuned', 'config': {}},
        }
        self.metrics = {name: [] for name in self.variants}

    def assign_variant(self, user_id: str) -> str:
        """Assign user to variant."""
        # Consistent hashing for same user
        hash_val = hash(user_id)
        if hash_val % 2 == 0:
            return 'control'
        else:
            return 'variant_a'

    async def run_query(
        self,
        user_id: str,
        query: str,
    ) -> str:
        """Run query with assigned variant."""
        variant = self.assign_variant(user_id)
        model_config = self.variants[variant]

        # Run with assigned model
        from app.core import create_agentic_assistant
        assistant = create_agentic_assistant(
            model_id=model_config['model']
        )

        response = assistant.chat(query)

        return response

    def record_metric(
        self,
        variant: str,
        metric_name: str,
        value: float,
    ):
        """Record metric for variant."""
        self.metrics[variant].append({
            'metric': metric_name,
            'value': value,
        })

    def analyze_results(self) -> Dict:
        """Analyze A/B test results."""
        results = {}

        for variant, metrics in self.metrics.items():
            if metrics:
                avg_value = sum(m['value'] for m in metrics) / len(metrics)
                results[variant] = avg_value

        return results
```

## Implementation Timeline

### Week 1-2: Feedback System
- [ ] Feedback collector
- [ ] Storage backend
- [ ] UI for feedback collection
- [ ] Data preprocessing

### Week 3-4: Reward Model
- [ ] Reward model architecture
- [ ] Training pipeline
- [ ] Evaluation metrics
- [ ] Model deployment

### Week 5-6: PPO Training
- [ ] PPO trainer setup
- [ ] Policy model integration
- [ ] Training loop
- [ ] Checkpointing

### Week 7-8: Continuous Learning
- [ ] Continuous learner
- [ ] A/B testing framework
- [ ] Monitoring dashboard
- [ ] Deployment automation

## Success Metrics

- **Data Collection**: 10,000+ feedback samples
- **Reward Model Accuracy**: >85%
- **Policy Improvement**: +15% avg reward
- **User Satisfaction**: +20% positive feedback
- **Response Quality**: Measurable improvement

## Configuration

```yaml
rlhf:
  enabled: true

  feedback:
    collection_rate: 0.3  # Sample 30% of interactions
    storage: data/feedback.jsonl

  reward_model:
    base_model: microsoft/deberta-v3-base
    training:
      epochs: 3
      batch_size: 8
      learning_rate: 2e-5

  ppo:
    base_model: microsoft/phi-2
    training:
      epochs: 100
      batch_size: 8
      learning_rate: 1e-5
      kl_coef: 0.2

  continuous_learning:
    enabled: true
    buffer_size: 1000
    train_threshold: 100

  ab_testing:
    enabled: true
    variants: [control, variant_a]
```

## Next Steps

1. Set up feedback collection system
2. Train initial reward model
3. Implement PPO training
4. Deploy continuous learning
5. Launch A/B tests
