"""Synthetic dataset generator for Innovate Inc. company data."""
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any


# Simple name generators without faker dependency
def generate_company_name():
    prefixes = ["Tech", "Global", "Advanced", "Smart", "NextGen", "Prime", "Elite"]
    suffixes = ["Solutions", "Systems", "Technologies", "Labs", "Group", "Corp", "Inc"]
    return f"{random.choice(prefixes)} {random.choice(suffixes)}"


def generate_person_name():
    first_names = [
        "John",
        "Jane",
        "Mike",
        "Sarah",
        "David",
        "Lisa",
        "Robert",
        "Emily",
        "James",
        "Maria",
    ]
    last_names = [
        "Smith",
        "Johnson",
        "Williams",
        "Brown",
        "Jones",
        "Garcia",
        "Miller",
        "Davis",
        "Rodriguez",
        "Martinez",
    ]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


@dataclass
class Transaction:
    """Represents a single financial transaction."""

    transaction_id: str
    date: datetime
    amount: float
    description: str
    account_from: str
    account_to: str
    transaction_type: str  # 'income', 'expense', 'transfer'
    category: str
    vendor: str = ""
    reference: str = ""


@dataclass
class Document:
    """Represents a financial document."""

    document_id: str
    document_type: str  # 'invoice', 'receipt', 'contract', 'payroll', 'ledger'
    date: datetime
    amount: float
    parties: list[str]
    content: str = ""
    file_path: str = ""


@dataclass
class Dataset:
    """Complete synthetic dataset for Innovate Inc."""

    company_name: str = "Innovate Inc."
    transactions: list[Transaction] = field(default_factory=list)
    documents: list[Document] = field(default_factory=list)
    planted_errors: list[dict[str, Any]] = field(default_factory=list)
    start_date: datetime | None = None
    end_date: datetime | None = None


class InnovateIncGenerator:
    """Generator for synthetic Innovate Inc. financial data."""

    def __init__(self, seed: int = 42):
        random.seed(seed)

        # Company structure
        self.departments = [
            "Engineering",
            "Sales",
            "Marketing",
            "HR",
            "Finance",
            "Operations",
            "Legal",
            "IT",
            "Research",
            "Customer Service",
        ]

        self.vendors = [
            "Office Depot",
            "Microsoft",
            "AWS",
            "Google Cloud",
            "Adobe",
            "Deloitte",
            "PwC",
            "Accenture",
            "IBM",
            "Oracle",
            "Local Catering Co",
            "Travel Agency",
            "Printer Supplies Inc",
        ]

        # Transaction categories and types
        self.expense_categories = [
            "Office Supplies",
            "Software Licenses",
            "Cloud Services",
            "Professional Services",
            "Travel",
            "Marketing",
            "Equipment",
            "Rent",
            "Utilities",
            "Insurance",
            "Payroll",
            "Taxes",
        ]

        self.income_categories = [
            "Product Sales",
            "Service Revenue",
            "Consulting",
            "Licensing",
            "Subscriptions",
            "Grants",
            "Investments",
        ]

        self.accounts = {
            "checking": ["1001-Checking", "1002-Payroll Checking"],
            "savings": ["2001-Savings"],
            "receivables": ["1101-Accounts Receivable"],
            "payables": ["2101-Accounts Payable"],
            "revenue": ["4001-Product Revenue", "4002-Service Revenue"],
            "expenses": ["5001-Operating Expenses", "5002-COGS"],
        }

    def generate_company_data(
        self,
        years: int = 2,
        include_errors: bool = True,
        complexity_level: str = "medium",
        include_fraud_scheme: bool = False,
    ) -> Dataset:
        """Generate complete synthetic dataset for Innovate Inc.

        Args:
            years: Number of years of data to generate
            include_errors: Whether to plant accounting errors
            complexity_level: 'simple', 'medium', or 'complex'
            include_fraud_scheme: Whether to include fraud scenarios

        Returns:
            Complete Dataset object
        """
        print(
            f"🏭 Generating Innovate Inc. dataset ({years} years, {complexity_level} complexity)..."
        )

        # Calculate date range
        end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=365 * years)

        dataset = Dataset(
            company_name="Innovate Inc.", start_date=start_date, end_date=end_date
        )

        # Generate transactions based on complexity
        num_transactions = self._get_transaction_volume(complexity_level, years)

        # Generate core transactions
        self._generate_core_transactions(dataset, num_transactions)

        # Generate documents
        self._generate_documents(dataset)

        # Plant errors if requested
        if include_errors:
            self._plant_accounting_errors(dataset, complexity_level)

        # Add fraud scheme if requested
        if include_fraud_scheme:
            self._plant_fraud_scheme(dataset)

        print(f"📊 Generated {len(dataset.transactions)} transactions")
        print(f"📄 Generated {len(dataset.documents)} documents")
        if include_errors:
            print(f"⚠️ Planted {len(dataset.planted_errors)} accounting irregularities")

        return dataset

    def _get_transaction_volume(self, complexity: str, years: int) -> int:
        """Calculate transaction volume based on complexity."""
        base_volume = 5000  # transactions per year

        if complexity == "simple":
            multiplier = 0.5
        elif complexity == "medium":
            multiplier = 1.0
        elif complexity == "complex":
            multiplier = 2.0
        else:
            multiplier = 1.0

        return int(base_volume * years * multiplier)

    def _generate_core_transactions(self, dataset: Dataset, num_transactions: int):
        """Generate core business transactions."""
        current_date = dataset.start_date

        for i in range(num_transactions):
            # Generate transaction date (roughly evenly distributed)
            days_since_start = (dataset.end_date - dataset.start_date).days
            random_days = random.randint(0, days_since_start)
            transaction_date = dataset.start_date + timedelta(days=random_days)

            # Decide transaction type
            transaction_type = random.choices(
                ["income", "expense", "transfer"], weights=[0.4, 0.5, 0.1]
            )[0]

            if transaction_type == "income":
                transaction = self._generate_income_transaction(i, transaction_date)
            elif transaction_type == "expense":
                transaction = self._generate_expense_transaction(i, transaction_date)
            else:  # transfer
                transaction = self._generate_transfer_transaction(i, transaction_date)

            dataset.transactions.append(transaction)

    def _generate_income_transaction(self, index: int, date: datetime) -> Transaction:
        """Generate an income transaction."""
        amount = random.uniform(500, 50000)  # $500 to $50,000
        category = random.choice(self.income_categories)
        vendor = generate_company_name()

        return Transaction(
            transaction_id=f"INC-{index:06d}",
            date=date,
            amount=amount,
            description=f"{category} from {vendor}",
            account_from=random.choice(self.accounts["receivables"]),
            account_to=random.choice(self.accounts["revenue"]),
            transaction_type="income",
            category=category,
            vendor=vendor,
            reference=f"INV-{index:04d}",
        )

    def _generate_expense_transaction(self, index: int, date: datetime) -> Transaction:
        """Generate an expense transaction."""
        category = random.choice(self.expense_categories)

        # Amount based on category
        if category in ["Rent", "Insurance", "Equipment"]:
            amount = random.uniform(1000, 25000)
        elif category in ["Software Licenses", "Cloud Services"]:
            amount = random.uniform(100, 5000)
        elif category == "Payroll":
            amount = random.uniform(2000, 15000)
        else:
            amount = random.uniform(50, 2000)

        vendor = random.choice(self.vendors)

        return Transaction(
            transaction_id=f"EXP-{index:06d}",
            date=date,
            amount=-amount,  # Negative for expenses
            description=f"{category} - {vendor}",
            account_from=random.choice(self.accounts["expenses"]),
            account_to=random.choice(self.accounts["checking"]),
            transaction_type="expense",
            category=category,
            vendor=vendor,
            reference=f"BILL-{index:04d}",
        )

    def _generate_transfer_transaction(self, index: int, date: datetime) -> Transaction:
        """Generate an internal transfer transaction."""
        amount = random.uniform(1000, 50000)
        from_account = random.choice(self.accounts["checking"])
        to_account = random.choice(self.accounts["checking"] + self.accounts["savings"])

        return Transaction(
            transaction_id=f"TRF-{index:06d}",
            date=date,
            amount=amount,
            description="Transfer between accounts",
            account_from=from_account,
            account_to=to_account,
            transaction_type="transfer",
            category="Internal Transfer",
            reference=f"TRF-{index:04d}",
        )

    def _generate_documents(self, dataset: Dataset):
        """Generate supporting documents."""
        # Generate invoices for income transactions
        for transaction in dataset.transactions:
            if transaction.transaction_type == "income" and random.random() < 0.7:
                doc = Document(
                    document_id=f"DOC-{transaction.transaction_id}",
                    document_type="invoice",
                    date=transaction.date,
                    amount=transaction.amount,
                    parties=[transaction.vendor, dataset.company_name],
                    content=f"Invoice for {transaction.description}",
                    file_path=f"invoices/{transaction.transaction_id}.pdf",
                )
                dataset.documents.append(doc)

            elif transaction.transaction_type == "expense" and random.random() < 0.5:
                doc = Document(
                    document_id=f"DOC-{transaction.transaction_id}",
                    document_type="receipt",
                    date=transaction.date,
                    amount=abs(transaction.amount),
                    parties=[dataset.company_name, transaction.vendor],
                    content=f"Receipt for {transaction.description}",
                    file_path=f"receipts/{transaction.transaction_id}.pdf",
                )
                dataset.documents.append(doc)

    def _plant_accounting_errors(self, dataset: Dataset, complexity: str):
        """Plant accounting errors in the dataset."""
        num_errors = len(dataset.transactions) // 100  # 1% error rate

        if complexity == "simple":
            error_types = ["duplicate", "rounding"]
        elif complexity == "medium":
            error_types = ["duplicate", "rounding", "timing", "classification"]
        else:  # complex
            error_types = [
                "duplicate",
                "rounding",
                "timing",
                "classification",
                "amount",
            ]

        for i in range(num_errors):
            error_type = random.choice(error_types)
            transaction_idx = random.randint(0, len(dataset.transactions) - 1)

            if error_type == "duplicate":
                # Duplicate transaction
                original = dataset.transactions[transaction_idx]
                duplicate = Transaction(
                    transaction_id=f"DUP-{original.transaction_id}",
                    date=original.date + timedelta(days=random.randint(1, 30)),
                    amount=original.amount,
                    description=f"[DUPLICATE] {original.description}",
                    account_from=original.account_from,
                    account_to=original.account_to,
                    transaction_type=original.transaction_type,
                    category=original.category,
                    vendor=original.vendor,
                )
                dataset.transactions.append(duplicate)

                dataset.planted_errors.append(
                    {
                        "type": "duplicate_transaction",
                        "original_id": original.transaction_id,
                        "duplicate_id": duplicate.transaction_id,
                        "severity": "medium",
                        "description": "Duplicate transaction posted twice",
                    }
                )

            elif error_type == "rounding":
                # Rounding error
                original = dataset.transactions[transaction_idx]
                # Small amount difference (like $0.01)
                error_amount = random.choice([-0.01, 0.01])

                dataset.planted_errors.append(
                    {
                        "type": "rounding_error",
                        "transaction_id": original.transaction_id,
                        "expected_amount": original.amount,
                        "actual_amount": original.amount + error_amount,
                        "difference": error_amount,
                        "severity": "low",
                        "description": f"Rounding error of ${error_amount}",
                    }
                )

            elif error_type == "timing":
                # Transaction recorded in wrong period
                original = dataset.transactions[transaction_idx]
                # Move to adjacent month
                date_shift = timedelta(days=random.randint(25, 35))
                wrong_date = original.date + date_shift

                dataset.planted_errors.append(
                    {
                        "type": "timing_error",
                        "transaction_id": original.transaction_id,
                        "recorded_date": original.date,
                        "correct_date": wrong_date,
                        "severity": "medium",
                        "description": "Transaction recorded in wrong accounting period",
                    }
                )

            elif error_type == "classification":
                # Wrong account classification
                original = dataset.transactions[transaction_idx]
                wrong_category = random.choice(
                    [
                        cat
                        for cat in self.expense_categories + self.income_categories
                        if cat != original.category
                    ]
                )

                dataset.planted_errors.append(
                    {
                        "type": "classification_error",
                        "transaction_id": original.transaction_id,
                        "correct_category": original.category,
                        "wrong_category": wrong_category,
                        "severity": "high",
                        "description": "Transaction classified in wrong category",
                    }
                )

            elif error_type == "amount":
                # Amount recording error
                original = dataset.transactions[transaction_idx]
                # Transpose digits or multiply/divide by 10
                if random.random() < 0.5:
                    # Transpose (e.g., 123.45 -> 132.45)
                    amount_str = f"{abs(original.amount):.2f}"
                    if len(amount_str) > 4:
                        pos1, pos2 = random.sample(range(len(amount_str) - 3), 2)
                        chars = list(amount_str)
                        chars[pos1], chars[pos2] = chars[pos2], chars[pos1]
                        wrong_amount = float("".join(chars))
                    else:
                        wrong_amount = original.amount * 10
                else:
                    # Multiply/divide by 10
                    wrong_amount = original.amount * (
                        10 if random.random() < 0.5 else 0.1
                    )

                dataset.planted_errors.append(
                    {
                        "type": "amount_error",
                        "transaction_id": original.transaction_id,
                        "correct_amount": original.amount,
                        "wrong_amount": wrong_amount,
                        "severity": "high",
                        "description": "Transaction amount recorded incorrectly",
                    }
                )

    def _plant_fraud_scheme(self, dataset: Dataset):
        """Plant a sophisticated fraud scheme."""
        # Create a vendor fraud scheme
        fake_vendor = "Premium Office Solutions LLC"

        # Add the fake vendor to vendors list
        self.vendors.append(fake_vendor)

        # Create fraudulent transactions over several months
        fraud_start = dataset.start_date + timedelta(days=60)
        fraud_amounts = [4500, 5200, 4800, 6100, 3900]  # Slightly varying amounts

        for i, amount in enumerate(fraud_amounts):
            fraud_date = fraud_start + timedelta(days=i * 30)  # Monthly

            # Create fraudulent expense transaction
            fraud_transaction = Transaction(
                transaction_id=f"FRD-{i:03d}",
                date=fraud_date,
                amount=-amount,
                description=f"Office supplies and equipment - {fake_vendor}",
                account_from=random.choice(self.accounts["expenses"]),
                account_to=random.choice(self.accounts["checking"]),
                transaction_type="expense",
                category="Office Supplies",
                vendor=fake_vendor,
                reference=f"PO-{1000+i}",
            )

            dataset.transactions.append(fraud_transaction)

            # Create fake supporting document
            fraud_doc = Document(
                document_id=f"DOC-FRD-{i:03d}",
                document_type="invoice",
                date=fraud_date,
                amount=amount,
                parties=[fake_vendor, dataset.company_name],
                content=f"Fraudulent invoice from {fake_vendor}",
                file_path=f"invoices/FRD-{i:03d}.pdf",
            )

            dataset.documents.append(fraud_doc)

        # Record the fraud scheme
        dataset.planted_errors.append(
            {
                "type": "fraud_scheme",
                "description": f"Vendor fraud scheme with fake vendor {fake_vendor}",
                "involved_transactions": [
                    f"FRD-{i:03d}" for i in range(len(fraud_amounts))
                ],
                "total_amount": sum(fraud_amounts),
                "severity": "critical",
                "pattern": "Regular payments to non-existent vendor with varying amounts to avoid detection",
            }
        )
