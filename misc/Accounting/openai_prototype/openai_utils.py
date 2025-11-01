"""OpenAI integration utilities for AAE framework."""
import os
import json
import asyncio
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import base64

# OpenAI imports
from openai import OpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

@dataclass
class AuditPolicy:
    """Represents an audit policy that can be enforced via function calling."""
    name: str
    description: str
    function: Callable
    parameters: Dict[str, Any]

class OpenAIAuditOrchestrator:
    """OpenAI-powered audit orchestrator that integrates with AAE framework."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.audit_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.analysis_llm = ChatOpenAI(model="gpt-4o", temperature=0)
        
        # Registry of audit policies
        self.policies: Dict[str, AuditPolicy] = {}
        self._register_default_policies()
        
        # Audit prompts - OPTIMIZED for accuracy and efficiency
        self.audit_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a forensic accountant AI auditor. Analyze transactions for ALL accounting irregularities.

CRITICAL PATTERNS TO DETECT:
1. **Duplicates**: Exact/near matches in amount+date+vendor+description
2. **Rounding Errors**: Penny differences, suspicious rounding patterns  
3. **Classification Errors**: Wrong accounts, incorrect categories
4. **Amount Manipulation**: Statistical outliers, round numbers, unusual patterns
5. **Temporal Anomalies**: Future dates, weekend transactions, unusual timing
6. **Vendor Issues**: First-time high-value vendors, transaction splitting
7. **Documentation Gaps**: Missing approvals, inconsistent references

For each finding, provide:
- transaction_id, risk_score (0-100), category, confidence (high/medium/low), reason, recommended_action

Return ONLY valid JSON array. Be thorough but efficient."""),
            ("human", "{transactions}")
        ])
        
        self.explanation_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert auditor explaining AI findings to human reviewers.
            Provide clear, professional explanations for why each transaction was flagged.
            Include specific details and potential next steps."""),
            ("human", "Explain these audit findings: {findings}")
        ])
        
        self.audit_chain = self.audit_prompt | self.audit_llm | JsonOutputParser()
        self.explanation_chain = self.explanation_prompt | self.analysis_llm
    
    def _register_default_policies(self):
        """Register default audit policies with advanced statistical methods."""
        
        def check_duplicate_transactions(transactions: List[Dict]) -> List[Dict]:
            """Enhanced duplicate detection with fuzzy matching."""
            duplicates = []
            seen = {}
            
            for tx in transactions:
                # Create multiple keys for fuzzy matching
                key_exact = (tx['amount'], tx['date'], tx['vendor'], tx['description'])
                key_amount_date = (tx['amount'], tx['date'])
                key_vendor_desc = (tx['vendor'], tx['description'])
                
                if key_exact in seen:
                    duplicates.append({
                        'transaction_id': tx['transaction_id'],
                        'duplicate_id': seen[key_exact]['transaction_id'],
                        'confidence': 0.95,
                        'match_type': 'exact'
                    })
                elif key_amount_date in seen:
                    duplicates.append({
                        'transaction_id': tx['transaction_id'],
                        'duplicate_id': seen[key_amount_date]['transaction_id'],
                        'confidence': 0.75,
                        'match_type': 'amount_date'
                    })
                else:
                    seen[key_exact] = tx
                    seen[key_amount_date] = tx
            
            return duplicates
        
        def check_rounding_errors(transactions: List[Dict]) -> List[Dict]:
            """Detect rounding and mathematical errors."""
            errors = []
            
            for tx in transactions:
                amount = abs(tx['amount'])
                
                # Check for common rounding patterns
                if amount % 0.01 != 0:  # Not whole cents
                    continue
                    
                # Check for suspicious penny differences
                if amount % 1 == 0.01 or amount % 1 == 0.99:
                    errors.append({
                        'transaction_id': tx['transaction_id'],
                        'amount': tx['amount'],
                        'issue': 'rounding_error',
                        'confidence': 0.7,
                        'pattern': 'penny_difference'
                    })
                
                # Check for too many trailing zeros (suspicious rounding)
                amount_str = str(amount)
                if amount_str.count('0') > 3 and '.' in amount_str:
                    errors.append({
                        'transaction_id': tx['transaction_id'],
                        'amount': tx['amount'],
                        'issue': 'suspicious_rounding',
                        'confidence': 0.6,
                        'pattern': 'excessive_zeros'
                    })
            
            return errors
        
        def check_amount_anomalies(transactions: List[Dict]) -> List[Dict]:
            """Advanced statistical anomaly detection."""
            amounts = [abs(tx['amount']) for tx in transactions if tx['amount'] != 0]
            if not amounts:
                return []
            
            # Calculate statistical measures
            mean_amount = sum(amounts) / len(amounts)
            std_amount = (sum((x - mean_amount) ** 2 for x in amounts) / len(amounts)) ** 0.5
            
            anomalies = []
            for tx in transactions:
                amount = abs(tx['amount'])
                if amount == 0:
                    continue
                    
                z_score = (amount - mean_amount) / std_amount if std_amount > 0 else 0
                
                # Flag extreme outliers (3+ sigma)
                if z_score > 3:
                    anomalies.append({
                        'transaction_id': tx['transaction_id'],
                        'amount': tx['amount'],
                        'z_score': round(z_score, 2),
                        'confidence': min(0.9, z_score / 5),
                        'pattern': 'statistical_outlier'
                    })
                
                # Flag suspiciously round numbers
                elif amount % 1000 == 0 and amount > 10000:
                    anomalies.append({
                        'transaction_id': tx['transaction_id'],
                        'amount': tx['amount'],
                        'z_score': z_score,
                        'confidence': 0.8,
                        'pattern': 'round_number_suspicious'
                    })
            
            return anomalies
        
        def check_benfords_law(transactions: List[Dict]) -> List[Dict]:
            """Check for Benford's Law violations (digit frequency analysis)."""
            violations = []
            
            # Extract leading digits
            leading_digits = []
            for tx in transactions:
                amount = abs(tx['amount'])
                if amount >= 1:  # Only for amounts >= $1
                    digit = int(str(amount)[0])
                    leading_digits.append(digit)
            
            if len(leading_digits) < 10:  # Need minimum sample
                return violations
            
            # Calculate expected vs actual frequencies (Benford's Law)
            expected_freq = {d: (len(leading_digits) * 0.3010 * (1 / d)) for d in range(1, 10)}
            actual_freq = {d: leading_digits.count(d) for d in range(1, 10)}
            
            # Check for suspicious deviations
            for digit in range(1, 10):
                expected = expected_freq[digit]
                actual = actual_freq[digit]
                deviation = abs(actual - expected) / expected if expected > 0 else 0
                
                if deviation > 0.5:  # 50% deviation threshold
                    # Find transactions with this leading digit
                    suspicious_txs = [
                        tx for tx in transactions 
                        if abs(tx['amount']) >= 1 and int(str(abs(tx['amount']))[0]) == digit
                    ][:3]  # Limit to 3 examples
                    
                    for tx in suspicious_txs:
                        violations.append({
                            'transaction_id': tx['transaction_id'],
                            'amount': tx['amount'],
                            'leading_digit': digit,
                            'expected_freq': round(expected, 1),
                            'actual_freq': actual,
                            'deviation_percent': round(deviation * 100, 1),
                            'confidence': min(0.8, deviation),
                            'pattern': 'benford_violation'
                        })
            
            return violations
        
        def check_temporal_patterns(transactions: List[Dict]) -> List[Dict]:
            """Detect unusual timing patterns."""
            from datetime import datetime
            anomalies = []
            
            for tx in transactions:
                try:
                    date = datetime.fromisoformat(tx['date'].replace('Z', '+00:00'))
                    
                    # Future dates
                    if date > datetime.now():
                        anomalies.append({
                            'transaction_id': tx['transaction_id'],
                            'date': tx['date'],
                            'issue': 'future_date',
                            'confidence': 1.0,
                            'pattern': 'temporal_anomaly'
                        })
                    
                    # Weekend transactions (potentially suspicious)
                    elif date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                        anomalies.append({
                            'transaction_id': tx['transaction_id'],
                            'date': tx['date'],
                            'issue': 'weekend_transaction',
                            'confidence': 0.6,
                            'pattern': 'unusual_timing'
                        })
                        
                except (ValueError, AttributeError):
                    anomalies.append({
                        'transaction_id': tx['transaction_id'],
                        'date': tx['date'],
                        'issue': 'invalid_date_format',
                        'confidence': 0.9,
                        'pattern': 'data_quality_issue'
                    })
            
            return anomalies
        
        def check_vendor_anomalies(transactions: List[Dict]) -> List[Dict]:
            """Enhanced vendor analysis."""
            from collections import defaultdict
            vendor_stats = defaultdict(list)
            
            for tx in transactions:
                if tx.get('vendor'):
                    vendor_stats[tx['vendor']].append(tx)
            
            anomalies = []
            for vendor, txs in vendor_stats.items():
                amounts = [abs(tx['amount']) for tx in txs]
                avg_amount = sum(amounts) / len(amounts)
                
                # First-time vendor with high amount
                if len(txs) == 1 and avg_amount > 5000:
                    anomalies.append({
                        'transaction_id': txs[0]['transaction_id'],
                        'vendor': vendor,
                        'amount': txs[0]['amount'],
                        'issue': 'first_time_high_value',
                        'confidence': 0.7,
                        'pattern': 'vendor_anomaly'
                    })
                
                # Single vendor with many small transactions (possible splitting)
                elif len(txs) > 5 and all(abs(tx['amount']) < 100 for tx in txs):
                    for tx in txs[:2]:  # Flag first 2 as examples
                        anomalies.append({
                            'transaction_id': tx['transaction_id'],
                            'vendor': vendor,
                            'amount': tx['amount'],
                            'issue': 'transaction_splitting',
                            'confidence': 0.6,
                            'pattern': 'vendor_anomaly'
                        })
            
            return anomalies
        
        # Register enhanced policies
        self.policies['duplicate_check'] = AuditPolicy(
            name="duplicate_check",
            description="Enhanced duplicate detection with fuzzy matching",
            function=check_duplicate_transactions,
            parameters={}
        )
        
        self.policies['rounding_errors'] = AuditPolicy(
            name="rounding_errors",
            description="Detect rounding and mathematical errors",
            function=check_rounding_errors,
            parameters={}
        )
        
        self.policies['amount_anomalies'] = AuditPolicy(
            name="amount_anomalies",
            description="Advanced statistical anomaly detection",
            function=check_amount_anomalies,
            parameters={}
        )
        
        self.policies['benfords_law'] = AuditPolicy(
            name="benfords_law",
            description="Check for Benford's Law violations",
            function=check_benfords_law,
            parameters={}
        )
        
        self.policies['temporal_patterns'] = AuditPolicy(
            name="temporal_patterns",
            description="Detect unusual timing patterns",
            function=check_temporal_patterns,
            parameters={}
        )
        
        self.policies['vendor_anomalies'] = AuditPolicy(
            name="vendor_anomalies",
            description="Enhanced vendor analysis",
            function=check_vendor_anomalies,
            parameters={}
        )
    
    async def audit_with_openai(
        self, 
        transactions: List[Dict[str, Any]],
        enable_policies: bool = True,
        explain_findings: bool = True
    ) -> Dict[str, Any]:
        """Comprehensive audit using OpenAI and rule-based policies."""
        import time
        start_time = time.time()
        
        results = {
            'openai_flags': [],
            'policy_flags': [],
            'explanations': [],
            'summary': {},
            'processing_time': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Phase 1: OpenAI analysis
            transactions_json = json.dumps(transactions, default=str)
            openai_flags = await self.audit_chain.ainvoke({"transactions": transactions_json})
            results['openai_flags'] = openai_flags
            
            # Phase 2: Rule-based policy checks
            if enable_policies:
                for policy_name, policy in self.policies.items():
                    policy_results = policy.function(transactions)
                    results['policy_flags'].extend([
                        {
                            'transaction_id': result.get('transaction_id'),
                            'policy_name': policy_name,
                            'details': result,
                            'risk_score': result.get('confidence', 0.5) * 100
                        }
                        for result in policy_results
                    ])
            
            # Phase 3: Generate explanations
            if explain_findings and openai_flags:
                all_flags = openai_flags + results['policy_flags']
                explanation = await self.explanation_chain.ainvoke({"findings": json.dumps(all_flags)})
                results['explanations'] = [str(explanation)]
            
            # Phase 4: Generate summary
            results['summary'] = {
                'total_transactions': len(transactions),
                'openai_flags': len(openai_flags),
                'policy_flags': len(results['policy_flags']),
                'total_flags': len(openai_flags) + len(results['policy_flags']),
                'flag_rate': (len(openai_flags) + len(results['policy_flags'])) / len(transactions) * 100,
                'high_risk_count': sum(1 for flag in openai_flags if flag.get('risk_score', 0) > 80)
            }
            
            results['processing_time'] = time.time() - start_time
            
            return results
            
        except Exception as e:
            results['error'] = str(e)
            return results
    
    def extract_document_fields(self, image_bytes: bytes, document_type: str = "invoice") -> Dict[str, Any]:
        """Extract structured data from documents using GPT-4 Vision."""
        try:
            base64_image = base64.b64encode(image_bytes).decode()
            
            # Define extraction schema based on document type
            if document_type == "invoice":
                prompt = """Extract vendor name, invoice date, total amount, invoice number, due date, tax amount, and line items from this invoice.
                Return JSON with keys: vendor, date, amount, invoice_number, due_date, tax_amount, items[]."""
            
            elif document_type == "receipt":
                prompt = """Extract vendor name, purchase date, total amount, payment method, and items from this receipt.
                Return JSON with keys: vendor, date, amount, payment_method, items[]."""
            
            else:
                prompt = """Extract all visible text and structured information from this document.
                Return JSON with relevant fields based on the document type."""
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
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
            return {"error": f"Document extraction failed: {str(e)}"}
    
    def register_policy(self, policy: AuditPolicy):
        """Register a custom audit policy."""
        self.policies[policy.name] = policy
    
    def get_policies(self) -> Dict[str, AuditPolicy]:
        """Get all registered policies."""
        return self.policies.copy()

# Utility function for batch processing
async def batch_audit_transactions(
    orchestrator: OpenAIAuditOrchestrator,
    transactions: List[Dict[str, Any]],
    batch_size: int = 100
) -> List[Dict[str, Any]]:
    """Process transactions in batches to handle large datasets."""
    results = []
    
    for i in range(0, len(transactions), batch_size):
        batch = transactions[i:i + batch_size]
        batch_result = await orchestrator.audit_with_openai(batch)
        results.append(batch_result)
        
        # Small delay to avoid rate limiting
        await asyncio.sleep(0.1)
    
    return results
