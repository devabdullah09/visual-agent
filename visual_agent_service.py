#!/usr/bin/env python3
"""
Visual Agent Service for n8n Integration
Handles HTTP requests and generates visual HTML output
"""

import json
import sys
import os
from visual_agent import VisualAgent


def main():
    """Main service function for n8n integration"""
    try:
        # Read input from stdin (n8n passes data this way)
        input_data = json.loads(sys.stdin.read())

        # Extract text and visual type from n8n input
        text = input_data.get('text', '')
        visual_type = input_data.get('visual_type', 'auto')

        if not text:
            result = {
                "error": "No text provided",
                "html_output": ""
            }
        else:
            # Initialize visual agent
            agent = VisualAgent()

            # Generate HTML visual
            html_output = agent.generate_html(text, visual_type)

            result = {
                "html_output": html_output,
                "visual_type": visual_type,
                "text_length": len(text)
            }

        # Output result as JSON for n8n
        print(json.dumps(result))

    except Exception as e:
        error_result = {
            "error": str(e),
            "html_output": ""
        }
        print(json.dumps(error_result))
        sys.exit(1)


if __name__ == "__main__":
    main()
