# Visual Agent - Text to Interactive Visuals

A Python-based visual agent that converts plain text into interactive HTML visuals (flowcharts, diagrams, and charts) with n8n integration.

## Features

- **Visual Types**: Automatically detects and generates:
  - Flowcharts for step sequences and dependencies
  - Diagrams for components and connections
  - Charts for numeric series and tabular metrics
- **Secret Redaction**: Automatically masks sensitive information
- **n8n Integration**: Ready-to-use n8n workflow
- **Self-contained HTML**: Generates complete HTML files with embedded visuals
- **Deterministic Output**: Same input produces same visual

## Quick Start

### For n8n Integration (Self-contained HTML output)

1. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Generate self-contained HTML files:**

   ```bash
   # Auto-detect visual type
   python simple_cli.py -i "your text" -o output.html

   # Force specific visual type
   python simple_cli.py -i "your text" -t flowchart -o flowchart.html
   ```

3. **Use the generated HTML file in n8n workflows**

### For Testing/Demo (Web Interface)

1. **Run the local web server:**

   ```bash
   python run_local.py
   ```

2. **Open your browser:**
   - Go to `http://localhost:8080`
   - Enter your text and generate visuals

## Usage

### Direct Python Usage

```python
from visual_agent import VisualAgent

agent = VisualAgent()

# Generate flowchart
text = """
Start
Check user authentication?
Yes: Load user dashboard
No: Show login form
End
"""

html = agent.generate_html(text, "flowchart")
with open("output.html", "w") as f:
    f.write(html)
```

### n8n Integration

1. Set up the n8n workflow
2. Send POST request to the webhook with:

```json
{
  "text": "Your text here",
  "visual_type": "auto" // or "flowchart", "diagram", "chart"
}
```

3. Receive HTML response with embedded visual

## Input Text Formats

### Flowcharts

```
Start
Check condition?
Yes: Action 1
No: Action 2
End
```

### Diagrams

```
Frontend connects to API
API queries Database
Database returns data to API
API sends response to Frontend
```

### Charts

```
Q1: 1000
Q2: 1500
Q3: 1200
Q4: 1800
```

## API Endpoints

- `POST /webhook/visual-agent` - Generate visual from text

## Security Features

- Automatic redaction of:
  - Email addresses
  - Credit card numbers
  - Passwords and secrets
  - API keys and tokens

## File Structure

```
├── visual_agent.py          # Core visual agent logic
├── visual_agent_service.py  # n8n service wrapper
├── n8n_workflow.json       # n8n workflow configuration
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Complete stack setup
└── README.md             # This file
```

## Customization

The visual agent can be extended by modifying:

- `detect_visual_type()` - Add new detection patterns
- `parse_*()` methods - Add new parsing logic
- `generate_*_svg()` methods - Customize visual appearance

## License

MIT License - feel free to use and modify as needed.
