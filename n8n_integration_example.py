#!/usr/bin/env python3
"""
n8n Integration Example
Shows how to use Visual Agent with n8n for self-contained HTML output
"""

import subprocess
import json
import os
from visual_agent import VisualAgent


def generate_visual_for_n8n(input_text, visual_type="auto", output_file="n8n_visual.html"):
    """
    Generate a self-contained HTML visual for n8n integration

    Args:
        input_text (str): Text to convert to visual
        visual_type (str): Type of visual (flowchart, diagram, chart, auto)
        output_file (str): Output HTML file path

    Returns:
        dict: Result with file path and metadata
    """
    try:
        # Use the Visual Agent to generate HTML
        agent = VisualAgent()

        # Generate the visual
        html_content = agent.generate_html(input_text, visual_type)

        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Get file info
        file_size = os.path.getsize(output_file)

        return {
            "success": True,
            "output_file": output_file,
            "file_size": file_size,
            "visual_type": visual_type,
            "message": "Visual generated successfully"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate visual"
        }


def n8n_webhook_handler(request_data):
    """
    Handle n8n webhook request

    Expected request format:
    {
        "text": "Your input text here",
        "type": "flowchart|diagram|chart|auto",
        "output_file": "optional_custom_filename.html"
    }
    """
    try:
        # Extract data from request
        input_text = request_data.get('text', '')
        visual_type = request_data.get('type', 'auto')
        output_file = request_data.get('output_file', 'n8n_visual.html')

        if not input_text:
            return {
                "success": False,
                "error": "No input text provided",
                "message": "Please provide text to convert"
            }

        # Generate visual
        result = generate_visual_for_n8n(input_text, visual_type, output_file)

        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Webhook processing failed"
        }


def main():
    """Example usage for n8n integration"""
    print("🚀 n8n Integration Example")
    print("=" * 50)

    # Example 1: Generate flowchart
    print("\n📊 Example 1: Flowchart Generation")
    flowchart_text = """Start
User visits website
Check if user is logged in?
Yes: Show dashboard
No: Show login page
User enters credentials
Validate credentials?
Yes: Redirect to dashboard
No: Show error message
End"""

    result = generate_visual_for_n8n(
        flowchart_text, "flowchart", "n8n_flowchart.html")
    print(f"Result: {result}")

    # Example 2: Generate diagram
    print("\n📊 Example 2: Diagram Generation")
    diagram_text = """Frontend Application connects to API Gateway
API Gateway routes to Authentication Service
API Gateway routes to Product Service
Authentication Service queries User Database
Product Service queries Product Database
API Gateway sends response to Frontend"""

    result = generate_visual_for_n8n(
        diagram_text, "diagram", "n8n_diagram.html")
    print(f"Result: {result}")

    # Example 3: Generate chart
    print("\n📊 Example 3: Chart Generation")
    chart_text = """Q1: 1000
Q2: 1500
Q3: 2000
Q4: 1800"""

    result = generate_visual_for_n8n(chart_text, "chart", "n8n_chart.html")
    print(f"Result: {result}")

    print("\n✅ All examples completed!")
    print("📁 Generated files:")
    print("  - n8n_flowchart.html")
    print("  - n8n_diagram.html")
    print("  - n8n_chart.html")

    print("\n🔗 n8n Integration:")
    print("1. Use these HTML files directly in n8n workflows")
    print("2. Or call this script from n8n using Execute Command node")
    print("3. Or use the visual_agent_service.py for REST API integration")


if __name__ == "__main__":
    main()
