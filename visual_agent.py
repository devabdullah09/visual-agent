#!/usr/bin/env python3
"""
Visual Agent - Text to Interactive Visuals
Converts plain text into interactive HTML visuals (flowcharts, diagrams, charts)
Designed for n8n integration with self-contained HTML output
"""

import re
import json
import math
import random
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


class VisualType(Enum):
    FLOWCHART = "flowchart"
    DIAGRAM = "diagram"
    CHART = "chart"


@dataclass
class Node:
    id: str
    label: str
    type: str = "process"
    x: float = 0
    y: float = 0
    width: float = 180
    height: float = 70


@dataclass
class Edge:
    from_node: str
    to_node: str
    label: Optional[str] = None


@dataclass
class ChartData:
    label: str
    value: float


class VisualAgent:
    """Main visual agent class that converts text to interactive HTML visuals"""

    def __init__(self):
        self.secret_patterns = [
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),
            (r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[CARD]'),
            (r'\b(?:password|pwd|secret|key|token|api[-_]?key)\s*[:=]\s*\S+',
             'password: [REDACTED]'),
            (r'\b(?:sk|pk)-[A-Za-z0-9]{20,}\b', '[SECRET]')
        ]

    def redact_secrets(self, text: str) -> str:
        """Redact sensitive information from text"""
        redacted_text = text
        for pattern, replacement in self.secret_patterns:
            redacted_text = re.sub(pattern, replacement,
                                   redacted_text, flags=re.IGNORECASE)
        return redacted_text

    def detect_visual_type(self, text: str, preferred_type: str = "auto") -> VisualType:
        """Detect the best visual type for the given text"""
        if preferred_type != "auto":
            return VisualType(preferred_type)

        text_lower = text.lower()

        # Check for chart indicators
        has_key_value = bool(re.search(r'[:=]\s*\d+', text))
        has_quarter_or_month = bool(re.search(
            r'\b(q1|q2|q3|q4|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b', text, re.IGNORECASE))
        if (has_key_value and has_quarter_or_month) or len(re.findall(r'[:=]\s*\d+', text)) >= 3:
            return VisualType.CHART

        # Check for flowchart indicators
        has_flow_keywords = bool(
            re.search(r'\b(start|begin|end|finish|step|process)\b', text_lower))
        has_decision = '?' in text
        has_yes_no = bool(re.search(r'\b(yes|no)\s*:', text, re.IGNORECASE))
        has_if_then = bool(
            re.search(r'\bif\b[\s\S]*\bthen\b', text, re.IGNORECASE))

        if has_flow_keywords or has_decision or has_yes_no or has_if_then:
            return VisualType.FLOWCHART

        # Default to diagram
        return VisualType.DIAGRAM

    def parse_flowchart(self, text: str) -> Dict[str, Any]:
        """Parse text into flowchart nodes and edges"""
        nodes = []
        edges = []
        node_map = {}
        node_id_counter = 0

        def add_node(label: str, node_type: str = "process") -> str:
            nonlocal node_id_counter
            if label not in node_map:
                node_id = f"node_{node_id_counter}"
                node_id_counter += 1
                node = Node(id=node_id, label=label, type=node_type)
                nodes.append(node)
                node_map[label] = node_id
                return node_id
            return node_map[label]

        lines = [line.strip() for line in text.split('\n') if line.strip()]
        sequential_candidates = []
        last_decision = None
        decision_to_branches = {}
        last_non_decision = None
        decision_prev_map = {}
        pending_yes_no = {}  # Track pending Yes/No branches

        for i, line in enumerate(lines):
            # Check for arrow connections
            arrow_parts = re.split(r'\s*→\s*|\s*->\s*', line)
            has_arrow = len(arrow_parts) > 1
            has_branch = bool(
                re.search(r'\b(yes|no)\s*:', line, re.IGNORECASE))

            # Handle if-then-else statements
            if_then_match = re.match(
                r'^if\s+(.+?)\s+then\s+(.+?)(?:\s+else\s+(.+))?$', line, re.IGNORECASE)
            if if_then_match:
                condition = if_then_match.group(1).strip()
                then_action = if_then_match.group(2).strip()
                else_action = if_then_match.group(
                    3).strip() if if_then_match.group(3) else ''

                decision_label = condition if condition.endswith(
                    '?') else f"{condition}?"
                decision_id = add_node(decision_label, "decision")
                last_decision = decision_label

                if decision_label not in decision_to_branches:
                    decision_to_branches[decision_label] = set()

                if then_action:
                    is_terminal = bool(
                        re.search(r'\b(start|begin|end|finish)\b', then_action, re.IGNORECASE))
                    then_id = add_node(
                        then_action, "terminal" if is_terminal else "process")
                    edges.append(Edge(decision_id, then_id, "Yes"))
                    decision_to_branches[decision_label].add("Yes")

                if else_action:
                    is_terminal = bool(
                        re.search(r'\b(start|begin|end|finish)\b', else_action, re.IGNORECASE))
                    else_id = add_node(
                        else_action, "terminal" if is_terminal else "process")
                    edges.append(Edge(decision_id, else_id, "No"))
                    decision_to_branches[decision_label].add("No")
                continue

            # Handle standalone Yes/No branches
            if has_branch and not has_arrow:
                yes_match = re.search(
                    r'^yes\s*:\s*(.+?)(?=\s+no\s*:|$)', line, re.IGNORECASE)
                no_match = re.search(r'no\s*:\s*(.+?)$', line, re.IGNORECASE)

                if yes_match:
                    yes_path = yes_match.group(1).strip()
                    decision_source = last_decision
                    if decision_source and yes_path:
                        is_terminal = bool(
                            re.search(r'\b(start|begin|end|finish)\b', yes_path, re.IGNORECASE))
                        yes_id = add_node(
                            yes_path, "terminal" if is_terminal else "process")
                        decision_id = node_map.get(decision_source)
                        if decision_id:
                            edges.append(Edge(decision_id, yes_id, "Yes"))
                        if decision_source not in decision_to_branches:
                            decision_to_branches[decision_source] = set()
                        decision_to_branches[decision_source].add("Yes")

                if no_match:
                    no_path = no_match.group(1).strip()
                    decision_source = last_decision
                    if decision_source and no_path:
                        is_terminal = bool(
                            re.search(r'\b(start|begin|end|finish)\b', no_path, re.IGNORECASE))
                        no_id = add_node(
                            no_path, "terminal" if is_terminal else "process")
                        decision_id = node_map.get(decision_source)
                        if decision_id:
                            edges.append(Edge(decision_id, no_id, "No"))
                        if decision_source not in decision_to_branches:
                            decision_to_branches[decision_source] = set()
                        decision_to_branches[decision_source].add("No")
                continue

            if not has_arrow and not has_branch:
                # Sequential step
                step_match = re.match(
                    r'^step\s*\d+\s*:\s*(.+)$', line, re.IGNORECASE)
                label = step_match.group(1).strip() if step_match else line
                is_terminal = bool(
                    re.search(r'\b(start|begin|end|finish)\b', label, re.IGNORECASE))

                # Check if this is a decision node
                is_decision = '?' in label or bool(
                    re.search(r'\b(decision|check|validate|verify)\b', label, re.IGNORECASE))
                node_type = "decision" if is_decision else (
                    "terminal" if is_terminal else "process")

                add_node(label, node_type)

                if is_decision:
                    last_decision = label
                    if label not in decision_to_branches:
                        decision_to_branches[label] = set()
                    if last_non_decision:
                        decision_prev_map[label] = last_non_decision
                if not is_decision:
                    last_non_decision = label

                sequential_candidates.append(label)
                continue

            # Process arrow connections
            for i, part in enumerate(arrow_parts):
                part = part.strip()
                if not part:
                    continue

                # Handle if-then-else constructs
                if_match = re.match(
                    r'^if\s+(.+?)\s+then\s+(.+?)(?:\s+else\s+(.+))?$', part, re.IGNORECASE)
                if if_match:
                    condition = if_match.group(1).strip()
                    then_action = if_match.group(2).strip()
                    else_action = if_match.group(
                        3).strip() if if_match.group(3) else ''

                    decision_label = condition if condition.endswith(
                        '?') else f"{condition}?"
                    decision_id = add_node(decision_label, "decision")
                    last_decision = decision_label

                    if decision_label not in decision_to_branches:
                        decision_to_branches[decision_label] = set()
                    if last_non_decision:
                        decision_prev_map[decision_label] = last_non_decision

                    if then_action:
                        is_terminal = bool(
                            re.search(r'\b(start|begin|end|finish)\b', then_action, re.IGNORECASE))
                        then_id = add_node(
                            then_action, "terminal" if is_terminal else "process")
                        edges.append(Edge(decision_id, then_id, "Yes"))
                        decision_to_branches[decision_label].add("Yes")

                    if else_action:
                        is_terminal = bool(
                            re.search(r'\b(start|begin|end|finish)\b', else_action, re.IGNORECASE))
                        else_id = add_node(
                            else_action, "terminal" if is_terminal else "process")
                        edges.append(Edge(decision_id, else_id, "No"))
                        decision_to_branches[decision_label].add("No")

                    continue

                # Handle yes/no branches
                yes_match = re.search(
                    r'^yes\s*:\s*(.+?)(?=\s+no\s*:|$)', part, re.IGNORECASE)
                no_match = re.search(r'no\s*:\s*(.+?)$', part, re.IGNORECASE)

                if yes_match or no_match:
                    if yes_match:
                        yes_path = yes_match.group(1).strip()
                        decision_source = last_decision
                        if decision_source and yes_path:
                            is_terminal = bool(
                                re.search(r'\b(start|begin|end|finish)\b', yes_path, re.IGNORECASE))
                            yes_id = add_node(
                                yes_path, "terminal" if is_terminal else "process")
                            edges.append(Edge(decision_source, yes_id, "Yes"))
                            if decision_source not in decision_to_branches:
                                decision_to_branches[decision_source] = set()
                            decision_to_branches[decision_source].add("Yes")

                    if no_match:
                        no_path = no_match.group(1).strip()
                        decision_source = last_decision
                        if decision_source and no_path:
                            is_terminal = bool(
                                re.search(r'\b(start|begin|end|finish)\b', no_path, re.IGNORECASE))
                            no_id = add_node(
                                no_path, "terminal" if is_terminal else "process")
                            edges.append(Edge(decision_source, no_id, "No"))
                            if decision_source not in decision_to_branches:
                                decision_to_branches[decision_source] = set()
                            decision_to_branches[decision_source].add("No")
                else:
                    # Regular node
                    is_decision = '?' in part or bool(
                        re.search(r'\b(decision|check|validate|verify)\b', part, re.IGNORECASE))
                    is_terminal = bool(
                        re.search(r'\b(start|begin|end|finish)\b', part, re.IGNORECASE))

                    node_type = "decision" if is_decision else (
                        "terminal" if is_terminal else "process")
                    node_id = add_node(part, node_type)

                    if is_decision:
                        last_decision = part
                        if part not in decision_to_branches:
                            decision_to_branches[part] = set()
                        if last_non_decision:
                            decision_prev_map[part] = last_non_decision
                    if not is_decision:
                        last_non_decision = part

                    # Connect to next part
                    if i < len(arrow_parts) - 1:
                        next_part = arrow_parts[i + 1].strip()
                        if not re.match(r'^(yes|no)\s*:', next_part, re.IGNORECASE):
                            next_id = add_node(next_part, "process")
                            edges.append(Edge(node_id, next_id))

        # Add proper flow connections based on the logical flow
        # This handles the correct flow: Yes branches go to End, No branches continue the flow

        # First, identify decision nodes and their branches
        decision_nodes = [node for node in nodes if node.type == "decision"]

        for decision in decision_nodes:
            decision_id = decision.id
            decision_edges = [e for e in edges if e.from_node ==
                              decision_id and e.label in ["Yes", "No"]]

            if decision_edges:
                yes_edge = next(
                    (e for e in decision_edges if e.label == "Yes"), None)
                no_edge = next(
                    (e for e in decision_edges if e.label == "No"), None)

                if yes_edge and no_edge:
                    # Yes branch should go to End (user is already logged in)
                    # No branch should continue the flow
                    yes_to_id = yes_edge.to_node
                    no_to_id = no_edge.to_node

                    # Connect Yes branch to End
                    end_node = next(
                        (n for n in nodes if n.type == "terminal" and "end" in n.label.lower()), None)
                    if end_node and not any(e.from_node == yes_to_id and e.to_node == end_node.id for e in edges):
                        edges.append(Edge(yes_to_id, end_node.id))

                    # Connect No branch to the next step in the flow
                    # Find the next step after this decision in the sequential flow
                    decision_index = next((i for i, label in enumerate(
                        sequential_candidates) if label == decision.label), -1)
                    if decision_index >= 0 and decision_index < len(sequential_candidates) - 1:
                        next_step = sequential_candidates[decision_index + 1]
                        if next_step in node_map:
                            next_id = node_map[next_step]
                            if not any(e.from_node == no_to_id and e.to_node == next_id for e in edges):
                                edges.append(Edge(no_to_id, next_id))

        # Add remaining sequential connections for non-decision nodes
        for i in range(len(sequential_candidates) - 1):
            from_label = sequential_candidates[i]
            to_label = sequential_candidates[i + 1]

            if from_label in node_map and to_label in node_map:
                from_node = next(
                    (n for n in nodes if n.label == from_label), None)
                from_id = node_map[from_label]
                to_id = node_map[to_label]

                # Skip if edge already exists or if it's a decision node
                if (any(e.from_node == from_id and e.to_node == to_id for e in edges) or
                        (from_node and from_node.type == "decision")):
                    continue

                # Add sequential connection
                edges.append(Edge(from_id, to_id))

        return {
            "nodes": [{"id": n.id, "label": n.label, "type": n.type} for n in nodes],
            "edges": [{"from": e.from_node, "to": e.to_node, "label": e.label} for e in edges]
        }

    def parse_diagram(self, text: str) -> Dict[str, Any]:
        """Parse text into diagram nodes and edges"""
        nodes = []
        edges = []
        node_set = set()
        edge_set = set()

        def canon(s: str) -> str:
            return re.sub(r'\s+', ' ', s.strip())

        def clean_entity(s: str) -> str:
            return re.sub(r'^(the|a|an)\s+', '', canon(s), flags=re.IGNORECASE)

        def add_node(label: str) -> Optional[str]:
            key = canon(label)
            if not key:
                return None
            if key not in node_set:
                node_id = f"node_{len(nodes)}"
                nodes.append({"id": node_id, "label": key})
                node_set.add(key)
                return key
            return key

        def add_edge(from_label: str, to_label: str):
            key = f"{from_label} -> {to_label}"
            if key not in edge_set:
                edges.append({"from": from_label, "to": to_label})
                edge_set.add(key)

        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # Process arrow connections
        for line in lines:
            if re.search(r'[→-]>', line) or '→' in line or '->' in line:
                parts = re.split(r'\s*→\s*|\s*->\s*', line)
                for i in range(len(parts) - 1):
                    from_label = add_node(parts[i])
                    to_label = add_node(parts[i + 1])
                    if from_label and to_label:
                        add_edge(from_label, to_label)

        # Process natural language connections
        phrases = re.split(r'[\n\.;]+|,\s*(?=[A-Z0-9])', text)
        phrases = [p.strip() for p in phrases if p.strip()]

        verb_patterns = [
            r'^(.+?)\s+connects\s+to\s+(.+)$',
            r'^(.+?)\s+sends(?:\s+request)?\s+to\s+(.+)$',
            r'^(.+?)\s+routes\s+to\s+(.+)$',
            r'^(.+?)\s+links\s+to\s+(.+)$',
            r'^(.+?)\s+queries\s+(.+)$',
            r'^(.+?)\s+returns(?:\s+(?:data|response))?\s+to\s+(.+)$',
            r'^(.+?)\s+sends\s+data\s+to\s+(.+)$'
        ]

        for phrase in phrases:
            for pattern in verb_patterns:
                match = re.match(pattern, phrase, re.IGNORECASE)
                if match:
                    from_raw = clean_entity(match.group(1))
                    to_raw = clean_entity(match.group(2))
                    from_label = add_node(from_raw)
                    to_label = add_node(to_raw)
                    if from_label and to_label:
                        add_edge(from_label, to_label)
                    break

        return {"nodes": nodes, "edges": edges}

    def parse_chart(self, text: str) -> List[Dict[str, Any]]:
        """Parse text into chart data"""
        data = []
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        for line in lines:
            match = re.match(r'([^:=]+)\s*[:=]\s*(\d+(?:\.\d+)?)', line)
            if match:
                data.append({
                    "label": match.group(1).strip(),
                    "value": float(match.group(2))
                })

        return data

    def generate_flowchart_svg(self, data: Dict[str, Any]) -> str:
        """Generate SVG for flowchart"""
        nodes = data["nodes"]
        edges = data["edges"]

        if not nodes:
            return ""

        # Calculate layout
        layout = self._calculate_flowchart_layout(nodes, edges)

        # Calculate dimensions with better spacing
        max_col = max(pos["col"] for pos in layout.values())
        max_row = max(pos["row"] for pos in layout.values())
        width = max(1200, (max_col + 1) * 220 + 200)  # Ensure minimum width
        height = max(800, (max_row + 1) * 140 + 200)  # Ensure minimum height

        svg = f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">'

        # Add arrow marker
        svg += '''
        <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
                <polygon points="0 0, 10 3, 0 6" fill="#667eea"/>
            </marker>
        </defs>
        '''

        # Draw edges first (so they appear behind nodes)
        for edge in edges:
            from_pos = layout.get(edge["from"])
            to_pos = layout.get(edge["to"])

            if from_pos and to_pos:
                svg += self._draw_flowchart_edge(from_pos,
                                                 to_pos, edge, width, height)

        # Draw nodes
        for node in nodes:
            pos = layout.get(node["id"])
            if pos:
                svg += self._draw_flowchart_node(node, pos, width, height)

        svg += '</svg>'
        return svg

    def generate_diagram_svg(self, data: Dict[str, Any]) -> str:
        """Generate SVG for diagram"""
        nodes = data["nodes"]
        edges = data["edges"]

        if not nodes:
            return ""

        width = 1000
        height = 800
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2.5
        node_width = 160
        node_height = 80

        svg = f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">'

        # Add arrow marker
        svg += '''
        <defs>
            <marker id="arrowhead-diagram" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
                <polygon points="0 0, 10 3, 0 6" fill="#667eea"/>
            </marker>
        </defs>
        '''

        # Calculate positions
        positions = {}
        for i, node in enumerate(nodes):
            angle = (2 * math.pi * i) / len(nodes) - math.pi / 2
            x = center_x + radius * math.cos(angle) - node_width / 2
            y = center_y + radius * math.sin(angle) - node_height / 2
            positions[node["id"]] = {"x": x, "y": y, "label": node["label"]}

        # Draw edges
        for edge in edges:
            # Find the node IDs for the edge labels
            from_node = next(
                (node for node in nodes if node["label"] == edge["from"]), None)
            to_node = next(
                (node for node in nodes if node["label"] == edge["to"]), None)

            if from_node and to_node:
                from_pos = positions.get(from_node["id"])
                to_pos = positions.get(to_node["id"])

                if from_pos and to_pos:
                    start = self._border_point(from_pos, node_width, node_height,
                                               to_pos["x"] + node_width / 2, to_pos["y"] + node_height / 2)
                    end = self._border_point(to_pos, node_width, node_height,
                                             from_pos["x"] + node_width / 2, from_pos["y"] + node_height / 2)

                    svg += f'''
                    <line x1="{start['x']}" y1="{start['y']}" x2="{end['x']}" y2="{end['y']}" 
                          stroke="#667eea" stroke-width="2.5" marker-end="url(#arrowhead-diagram)"/>
                    '''

        # Draw nodes
        for node in nodes:
            pos = positions[node["id"]]
            svg += f'''
            <g class="node">
                <rect x="{pos['x']}" y="{pos['y']}" width="{node_width}" height="{node_height}" 
                      rx="12" fill="#667eea" stroke="#5568d3" stroke-width="2.5"/>
                <text x="{pos['x'] + node_width / 2}" y="{pos['y'] + node_height / 2}" 
                      text-anchor="middle" dominant-baseline="middle" fill="white" 
                      font-size="14" font-weight="600">{pos['label']}</text>
            </g>
            '''

        svg += '</svg>'
        return svg

    def generate_chart_svg(self, data: List[Dict[str, Any]]) -> str:
        """Generate SVG for chart"""
        if not data:
            return ""

        width = 1000
        height = 700
        padding = 100
        chart_width = width - 2 * padding
        chart_height = height - 2 * padding

        max_value = max(item["value"] for item in data)
        bar_width = chart_width / len(data) * 0.7
        bar_spacing = chart_width / len(data) * 0.3

        svg = f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">'

        # Draw axes
        svg += f'''
        <line x1="{padding}" y1="{height - padding}" x2="{width - padding}" y2="{height - padding}" 
              stroke="#2c3e50" stroke-width="3"/>
        <line x1="{padding}" y1="{padding}" x2="{padding}" y2="{height - padding}" 
              stroke="#2c3e50" stroke-width="3"/>
        '''

        # Draw bars
        for i, item in enumerate(data):
            bar_height = (item["value"] / max_value) * chart_height
            x = padding + i * (bar_width + bar_spacing) + bar_spacing / 2
            y = height - padding - bar_height

            svg += f'''
            <rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" 
                  fill="#667eea" stroke="#5568d3" stroke-width="2" rx="6" class="bar"/>
            <text x="{x + bar_width / 2}" y="{height - padding + 30}" 
                  text-anchor="middle" font-size="14" font-weight="600" fill="#2c3e50">{item['label']}</text>
            <text x="{x + bar_width / 2}" y="{y - 10}" 
                  text-anchor="middle" font-size="14" font-weight="bold" fill="#2c3e50">{item['value']:,.0f}</text>
            '''

        svg += '</svg>'
        return svg

    def generate_html(self, text: str, visual_type: str = "auto") -> str:
        """Generate complete HTML with embedded visual"""
        redacted_text = self.redact_secrets(text)
        detected_type = self.detect_visual_type(redacted_text, visual_type)

        # Parse data based on type
        if detected_type == VisualType.FLOWCHART:
            data = self.parse_flowchart(redacted_text)
            svg_content = self.generate_flowchart_svg(data)
        elif detected_type == VisualType.DIAGRAM:
            data = self.parse_diagram(redacted_text)
            svg_content = self.generate_diagram_svg(data)
        elif detected_type == VisualType.CHART:
            data = self.parse_chart(redacted_text)
            svg_content = self.generate_chart_svg(data)
        else:
            return ""

        # Generate complete HTML
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visual Agent - {detected_type.value.title()}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 300;
        }}
        
        .header p {{
            opacity: 0.9;
            font-size: 1.1rem;
        }}
        
        .visual-container {{
            padding: 20px;
            background: white;
            display: flex;
            align-items: flex-start;
            justify-content: center;
            min-height: 600px;
            overflow: auto;
        }}
        
        .visual-svg {{
            display: block;
            max-width: 100%;
            height: auto;
        }}
        
        .node {{
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        
        .node:hover rect,
        .node:hover ellipse,
        .node:hover polygon {{
            filter: brightness(1.1);
            stroke-width: 3;
        }}
        
        .connection {{
            transition: all 0.2s ease;
        }}
        
        .connection:hover {{
            stroke-width: 3;
        }}
        
        .bar:hover {{
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Visual Agent</h1>
            <p>Generated {detected_type.value.title()}</p>
        </div>
        
        <div class="visual-container">
            {svg_content}
        </div>
    </div>
</body>
</html>
        """

        return html_template

    def _calculate_flowchart_layout(self, nodes: List[Dict], edges: List[Dict]) -> Dict[str, Dict]:
        """Calculate layout positions for flowchart nodes"""
        layout = {}
        node_map = {node["id"]: node for node in nodes}

        # Find start node
        target_nodes = {edge["to"] for edge in edges}
        start_node = next(
            (node for node in nodes if node["id"] not in target_nodes), nodes[0])

        # Build adjacency list
        adj_list = {}
        for edge in edges:
            if edge["from"] not in adj_list:
                adj_list[edge["from"]] = []
            adj_list[edge["from"]].append(
                {"to": edge["to"], "label": edge.get("label")})

        # Use a more comprehensive layout algorithm
        visited = set()
        queue = [{"id": start_node["id"], "col": 0, "row": 0}]
        max_row = 0

        while queue:
            current = queue.pop(0)
            if current["id"] in visited:
                continue
            visited.add(current["id"])

            node = node_map[current["id"]]
            layout[current["id"]] = {
                "col": current["col"],
                "row": current["row"],
                "node": node
            }
            max_row = max(max_row, current["row"])

            children = adj_list.get(current["id"], [])

            if node["type"] == "decision" and children:
                yes_child = next((c for c in children if c.get(
                    "label") and c.get("label").lower() == "yes"), None)
                no_child = next((c for c in children if c.get(
                    "label") and c.get("label").lower() == "no"), None)

                if yes_child and no_child:
                    # Position Yes/No branches side by side
                    queue.append(
                        {"id": yes_child["to"], "col": current["col"] + 1, "row": current["row"] + 1})
                    queue.append(
                        {"id": no_child["to"], "col": current["col"] - 1, "row": current["row"] + 1})
                else:
                    # Handle other decision branches
                    for i, child in enumerate(children):
                        child_col = current["col"] + (1 if i == 0 else -1)
                        queue.append(
                            {"id": child["to"], "col": child_col, "row": current["row"] + 1})
            else:
                # Regular nodes - continue the flow
                for i, child in enumerate(children):
                    # For regular flow, continue in the same column
                    child_col = current["col"]
                    child_row = current["row"] + 1
                    queue.append(
                        {"id": child["to"], "col": child_col, "row": child_row})

        # Handle any remaining nodes that weren't reached by BFS
        for node in nodes:
            if node["id"] not in layout:
                # Find a good position for orphaned nodes
                layout[node["id"]] = {
                    "col": 0,
                    "row": max_row + 1,
                    "node": node
                }
                max_row += 1

        # Normalize columns to start from 0
        min_col = min(pos["col"] for pos in layout.values())
        if min_col < 0:
            for pos in layout.values():
                pos["col"] -= min_col

        return layout

    def _draw_flowchart_node(self, node: Dict, pos: Dict, width: int, height: int) -> str:
        """Draw a flowchart node"""
        x = 100 + pos["col"] * 220
        y = 100 + pos["row"] * 140
        node_width = 180
        node_height = 70

        if node["type"] == "decision":
            # Diamond shape
            points = f"{x + node_width/2},{y} {x + node_width},{y + node_height/2} {x + node_width/2},{y + node_height} {x},{y + node_height/2}"
            return f'''
            <g class="node">
                <polygon points="{points}" fill="#e74c3c" stroke="#c0392b" stroke-width="2.5"/>
                <text x="{x + node_width/2}" y="{y + node_height/2}" text-anchor="middle" dominant-baseline="middle" 
                      fill="white" font-size="14" font-weight="600">{node['label']}</text>
            </g>
            '''
        elif node["type"] == "terminal":
            # Rounded rectangle
            return f'''
            <g class="node">
                <rect x="{x}" y="{y}" width="{node_width}" height="{node_height}" rx="35" 
                      fill="#27ae60" stroke="#229954" stroke-width="2.5"/>
                <text x="{x + node_width/2}" y="{y + node_height/2}" text-anchor="middle" dominant-baseline="middle" 
                      fill="white" font-size="15" font-weight="600">{node['label']}</text>
            </g>
            '''
        else:
            # Regular rectangle
            return f'''
            <g class="node">
                <rect x="{x}" y="{y}" width="{node_width}" height="{node_height}" rx="10" 
                      fill="#667eea" stroke="#5568d3" stroke-width="2.5"/>
                <text x="{x + node_width/2}" y="{y + node_height/2}" text-anchor="middle" dominant-baseline="middle" 
                      fill="white" font-size="14" font-weight="600">{node['label']}</text>
            </g>
            '''

    def _draw_flowchart_edge(self, from_pos: Dict, to_pos: Dict, edge: Dict, width: int, height: int) -> str:
        """Draw a flowchart edge with proper decision node handling"""
        from_x = from_pos["col"] * 220 + 100
        from_y = from_pos["row"] * 140 + 100
        to_x = to_pos["col"] * 220 + 100
        to_y = to_pos["row"] * 140 + 100

        # Get node dimensions
        from_node = from_pos.get("node", {})
        to_node = to_pos.get("node", {})

        # Calculate connection points based on node types
        if from_node.get("type") == "decision":
            # Decision node - connect from sides for Yes/No
            if edge.get("label") == "Yes":
                from_x += 90  # Right side
                from_y += 35  # Middle
            elif edge.get("label") == "No":
                from_x += 0   # Left side
                from_y += 35  # Middle
            else:
                from_x += 90  # Default to right side
                from_y += 35
        else:
            # Regular node - connect from bottom
            from_x += 90  # Center
            from_y += 70  # Bottom

        if to_node.get("type") == "decision":
            # Decision node - connect to top
            to_x += 90  # Center
            to_y += 0   # Top
        else:
            # Regular node - connect to top
            to_x += 90  # Center
            to_y += 0   # Top

        # Create path with curves for better appearance
        mid_y = (from_y + to_y) / 2
        path = f"M {from_x} {from_y} L {from_x} {mid_y} L {to_x} {mid_y} L {to_x} {to_y}"

        svg = f'''
        <path d="{path}" stroke="#667eea" stroke-width="2.5" fill="none" marker-end="url(#arrowhead)" class="connection"/>
        '''

        if edge.get("label"):
            label_x = (from_x + to_x) / 2 + 15
            label_y = mid_y
            svg += f'''
            <rect x="{label_x - 20}" y="{label_y - 12}" width="40" height="24" 
                  fill="white" stroke="#667eea" stroke-width="1.5" rx="4"/>
            <text x="{label_x}" y="{label_y + 4}" text-anchor="middle" font-size="12" 
                  font-weight="bold" fill="#667eea">{edge['label']}</text>
            '''

        return svg

    def _border_point(self, rect: Dict, w: float, h: float, target_x: float, target_y: float) -> Dict[str, float]:
        """Calculate border point for edge connection"""
        cx = rect["x"] + w / 2
        cy = rect["y"] + h / 2
        dx = target_x - cx
        dy = target_y - cy

        if dx == 0 and dy == 0:
            return {"x": cx, "y": cy}

        abs_dx = abs(dx)
        abs_dy = abs(dy)

        if abs_dx / (w / 2) > abs_dy / (h / 2):
            scale = (w / 2) / abs_dx
        else:
            scale = (h / 2) / abs_dy

        return {"x": cx + dx * scale, "y": cy + dy * scale}


def main():
    """Main function for testing"""
    agent = VisualAgent()

    # Test flowchart
    flowchart_text = """
    Start
    Check user authentication?
    Yes: Load user dashboard
    No: Show login form
    End
    """

    html = agent.generate_html(flowchart_text, "flowchart")
    with open("test_flowchart.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Generated test_flowchart.html")


if __name__ == "__main__":
    main()
