#!/usr/bin/env python3
"""
Simple CLI for Visual Agent
Command-line interface for generating visuals without web server
"""

import argparse
import sys
import os
from visual_agent import VisualAgent


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description='Visual Agent CLI - Convert text to interactive visuals',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect visual type
  python simple_cli.py -i "Start -> Process -> End" -o flowchart.html
  
  # Force flowchart
  python simple_cli.py -i flowchart.txt -t flowchart -o output.html
  
  # Generate chart from data
  python simple_cli.py -i "Q1: 1000\\nQ2: 2000" -t chart -o chart.html
  
  # Read from file and output to console
  python simple_cli.py -i input.txt -c
        """
    )

    parser.add_argument('-i', '--input', required=True,
                        help='Input text or path to text file')
    parser.add_argument('-o', '--output',
                        help='Output HTML file path')
    parser.add_argument('-t', '--type', default='auto',
                        choices=['auto', 'flowchart', 'diagram', 'chart'],
                        help='Visual type (default: auto)')
    parser.add_argument('-c', '--console', action='store_true',
                        help='Output to console instead of file')
    parser.add_argument('--no-redact', action='store_true',
                        help='Disable secret redaction')
    parser.add_argument('--preview', action='store_true',
                        help='Open output in browser after generation')

    args = parser.parse_args()

    # Read input
    if os.path.isfile(args.input):
        with open(args.input, 'r', encoding='utf-8') as f:
            text = f.read()
        print(f"📄 Read input from file: {args.input}")
    else:
        text = args.input
        print("📝 Using input text directly")

    if not text.strip():
        print("❌ Error: No text provided")
        return 1

    # Initialize visual agent
    try:
        agent = VisualAgent()
        print(f"🤖 Visual Agent initialized")
    except Exception as e:
        print(f"❌ Error initializing Visual Agent: {e}")
        return 1

    # Disable redaction if requested
    if args.no_redact:
        agent.redact_secrets = lambda x: x
        print("🔓 Secret redaction disabled")

    # Detect visual type
    detected_type = agent.detect_visual_type(text, args.type)
    print(f"🎯 Visual type: {detected_type.value}")

    # Generate visual
    try:
        print("⚙️  Generating visual...")
        html = agent.generate_html(text, args.type)

        if not html:
            print("❌ Error: No HTML generated")
            return 1

        print("✅ Visual generated successfully")

    except Exception as e:
        print(f"❌ Error generating visual: {e}")
        return 1

    # Output result
    if args.console:
        print("\n" + "="*50)
        print("HTML OUTPUT:")
        print("="*50)
        print(html)
    else:
        # Determine output file
        if args.output:
            output_file = args.output
        else:
            # Auto-generate filename
            timestamp = __import__(
                'datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"visual_{detected_type.value}_{timestamp}.html"

        # Write to file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"💾 Saved to: {output_file}")

            # Open in browser if requested
            if args.preview:
                import webbrowser
                webbrowser.open(f"file://{os.path.abspath(output_file)}")
                print(f"🌐 Opened in browser: {output_file}")

        except Exception as e:
            print(f"❌ Error saving file: {e}")
            return 1

    print("🎉 Done!")
    return 0


if __name__ == "__main__":
    exit(main())
