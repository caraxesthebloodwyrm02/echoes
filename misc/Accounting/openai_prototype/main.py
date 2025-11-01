"""OpenAI-powered AAE Phase 1 Prototype - FastAPI Integration."""
import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import pandas as pd
import io

# OpenAI imports
from openai import OpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Existing AAE imports
from Accounting.dataset.innovate_inc_generator import InnovateIncGenerator
from Accounting.core.experiment_orchestrator import ExperimentOrchestrator
from Accounting.core.models import ExperimentConfig

# Initialize OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = FastAPI(title="AAE OpenAI Prototype", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class TransactionFlag(BaseModel):
    transaction_id: str
    risk_score: float  # 0-100
    reason: str
    category: str  # 'error', 'fraud', 'policy_violation', 'anomaly'

class AuditResponse(BaseModel):
    flags: List[TransactionFlag]
    total_transactions: int
    flagged_count: int
    processing_time_seconds: float

# OpenAI prompts
audit_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert AI accounting auditor analyzing financial transactions. 
    Your task is to identify potential issues and return a JSON array of flagged transactions.
    
    For each flagged transaction, provide:
    - transaction_id: The unique identifier
    - risk_score: Number from 0-100 indicating severity
    - reason: Detailed explanation of why it was flagged
    - category: One of ['error', 'fraud', 'policy_violation', 'anomaly']
    
    Look for:
    1. Duplicate transactions
    2. Unusual amounts or patterns
    3. Missing or incorrect vendor information
    4. Timing anomalies
    5. Policy violations
    
    Return ONLY the JSON array, no additional text."""),
    ("human", "{transactions}")
])

parser = JsonOutputParser()

class OpenAIAuditEngine:
    """OpenAI-powered audit Glimpse that leverages existing AAE framework."""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.audit_chain = audit_prompt | self.llm | parser
    
    async def audit_transactions(self, transactions: List[Dict[str, Any]]) -> AuditResponse:
        """Analyze transactions using OpenAI."""
        import time
        start_time = time.time()
        
        # Convert transactions to JSON for OpenAI
        transactions_json = json.dumps(transactions, default=str, indent=2)
        
        try:
            # Get flags from OpenAI
            flags_raw = await self.audit_chain.ainvoke({"transactions": transactions_json})
            
            # Convert to our model
            flags = []
            for flag in flags_raw:
                try:
                    flags.append(TransactionFlag(**flag))
                except Exception as e:
                    print(f"Invalid flag format: {flag}, error: {e}")
            
            processing_time = time.time() - start_time
            
            return AuditResponse(
                flags=flags,
                total_transactions=len(transactions),
                flagged_count=len(flags),
                processing_time_seconds=processing_time
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"OpenAI analysis failed: {str(e)}")
    
    def extract_invoice_data(self, image_bytes: bytes) -> Dict[str, Any]:
        """Extract key fields from invoice using GPT-4 Vision."""
        try:
            # Convert image to base64
            base64_image = base64.b64encode(image_bytes).decode()
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": "Extract vendor name, invoice date, total amount, invoice number, and line items from this invoice. Return as JSON with keys: vendor, date, amount, invoice_number, items."
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                        }
                    ]
                }],
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Vision extraction failed: {str(e)}")

# Initialize Glimpse
audit_engine = OpenAIAuditEngine()

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "AAE OpenAI Prototype is running", "version": "1.0.0"}

@app.post("/generate/dataset")
async def generate_dataset(
    years: int = 1,
    include_errors: bool = True,
    complexity_level: str = 'medium',
    include_fraud: bool = True
):
    """Generate synthetic dataset using existing AAE framework."""
    try:
        generator = InnovateIncGenerator(seed=42)
        dataset = generator.generate_company_data(
            years=years,
            include_errors=include_errors,
            complexity_level=complexity_level,
            include_fraud_scheme=include_fraud
        )
        
        # Convert to JSON format for API
        transactions = []
        for tx in dataset.transactions:
            transactions.append({
                'transaction_id': tx.transaction_id,
                'date': tx.date.isoformat(),
                'amount': tx.amount,
                'description': tx.description,
                'account_from': tx.account_from,
                'account_to': tx.account_to,
                'transaction_type': tx.transaction_type,
                'category': tx.category,
                'vendor': tx.vendor,
                'reference': tx.reference
            })
        
        return {
            "company_name": dataset.company_name,
            "transactions": transactions,
            "total_transactions": len(transactions),
            "planted_errors": dataset.planted_errors,
            "error_count": len(dataset.planted_errors)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dataset generation failed: {str(e)}")

@app.post("/audit", response_model=AuditResponse)
async def audit_transactions(file: UploadFile = File(...)):
    """Audit uploaded transaction file using OpenAI."""
    try:
        # Read file content
        content = await file.read()
        
        # Parse based on file type
        if file.filename.endswith('.csv'):
            # Parse CSV
            df = pd.read_csv(io.StringIO(content.decode()))
            transactions = df.to_dict('records')
        elif file.filename.endswith('.json'):
            # Parse JSON
            transactions = json.loads(content.decode())
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Use CSV or JSON.")
        
        # Audit with OpenAI
        result = await audit_engine.audit_transactions(transactions)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit processing failed: {str(e)}")

@app.post("/extract/invoice")
async def extract_invoice(file: UploadFile = File(...)):
    """Extract data from invoice image using GPT-4 Vision."""
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image.")
        
        image_bytes = await file.read()
        extracted_data = audit_engine.extract_invoice_data(image_bytes)
        
        return {"extracted_data": extracted_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Invoice extraction failed: {str(e)}")

@app.post("/experiment/run")
async def run_experiment(
    name: str = "OpenAI_AAE_Experiment",
    dataset_size: str = "medium",
    groups: List[str] = ["human", "ai", "hybrid", "oracle"]
):
    """Run complete AAE experiment with OpenAI integration."""
    try:
        # Create experiment using existing framework
        orchestrator = ExperimentOrchestrator()
        experiment = orchestrator.create_experiment(
            name=name,
            dataset_size=dataset_size,
            groups=groups
        )
        
        # Run experiment
        results = experiment.run()
        
        # Return results
        return {
            "experiment_name": results.experiment_name,
            "duration_minutes": results.duration_minutes,
            "scores": {
                "human": results.human_score,
                "ai": results.ai_score,
                "hybrid": results.hybrid_score,
                "oracle": results.oracle_score
            },
            "key_findings": results.key_findings,
            "status": "completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Experiment failed: {str(e)}")

@app.get("/models/available")
async def list_available_models():
    """List available OpenAI models for auditing."""
    try:
        models = client.models.list()
        relevant_models = [
            model.id for model in models.data 
            if any(name in model.id for name in ['gpt-4', 'gpt-3.5'])
        ]
        
        return {
            "available_models": relevant_models,
            "recommended_models": {
                "audit": "gpt-4o-mini",
                "vision": "gpt-4o",
                "analysis": "gpt-4o"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model listing failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
