#!/usr/bin/env python3
"""
Quick ROI Analysis Test
"""

from assistant_v2_core import EchoesAssistantV2

def test_roi_analysis():
    # Initialize assistant
    assistant = EchoesAssistantV2(enable_tools=True, enable_status=False)

    # ROI parameters
    params = {
        'business_type': 'financial',
        'analysis_data': {
            'monthly_investment': 12000,
            'monthly_savings': 71822,
            'team_size': 5
        },
        'stakeholder_info': {
            'institution_name': 'Test Bank Corp',
            'email_to': ['cfo@testbank.com', 'cto@testbank.com']
        },
        'output_formats': ['yaml', 'csv', 'spreadsheet', 'report'],
        'customization_level': 'comprehensive'
    }

    print("🎯 Testing ROI Analysis Action...")
    print(f"Business: {params['business_type']}")
    print(f"Institution: {params['stakeholder_info']['institution_name']}")
    print(f"Investment: ${params['analysis_data']['monthly_investment']:,}")
    print(f"Savings: ${params['analysis_data']['monthly_savings']:,}")

    # Execute ROI analysis
    result = assistant.execute_action('roi', 'generate_roi_package', **params)

    if result['success']:
        print("\n✅ ROI Analysis Generated Successfully!")
        result_data = result['result']
        print(f"Analysis ID: {result_data['analysis_id']}")
        print(f"Generated {result_data['file_count']} file types")

        # Check file organization
        file_org = result_data.get('file_organization', {})
        if file_org.get('success'):
            print(f"Files organized in: {file_org['institution_directory']}")

        # Show metrics
        roi_metrics = result_data.get('roi_metrics', {})
        print(f"ROI: {roi_metrics.get('roi_percentage', 0):.1f}%")
        print(f"Payback Period: {roi_metrics.get('payback_days', 0):.1f} days")
        print(f"Annual Benefit: ${roi_metrics.get('annual_net_benefit', 0):,.0f}")

        print("\n📊 Savings Breakdown:")
        savings = roi_metrics.get('savings_breakdown', {})
        for category, amount in savings.items():
            annual = amount * 12
            print(f"- {category.replace('_', ' ').title()}: ${amount:,.0f}/month (${annual:,.0f}/year)")
    else:
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    test_roi_analysis()
