# Calculus 1 AI Assistant

An AI-powered study assistant designed for a **specific Calculus I course**, using the **course syllabus and materials** as its main academic reference.

## Overview

This project is an early working prototype of a **course-aligned AI learning assistant**.

Unlike general-purpose AI chat tools, this assistant is designed to:

- stay aligned with the **actual course content**
- follow the **course sequence and instructional logic**
- avoid jumping ahead to methods not yet covered
- adapt explanations to the student’s needs
- provide basic instructor-facing insights through a **Professor Mode**

## Current Features

### Guest Mode
- Temporary access without login
- Useful for demos and quick testing
- No permanent conversation history

### Student Mode
- Login with assigned student credentials
- Persistent course chat history
- One main chat per student
- Course-aligned explanations based on syllabus and materials
- Adaptive responses:
  - simpler explanations
  - step-by-step guidance
  - more rigorous explanations when needed

### Professor Mode
- Create student accounts
- View student list
- Access full student chat history
- Generate AI-based student summaries
- Generate weekly course summaries
- Review early course-level insights such as:
  - most consulted topics
  - recurrent doubts
  - possible reinforcement needs

## Educational Approach

This assistant is designed as a **course assistant**, not a general math chatbot.

Its behavior is guided by the following principles:

- use the **syllabus** to understand course goals, scope, and sequence
- use the **course materials** as the main factual foundation
- explain clearly without simply repeating the PDFs
- stay within the **current stage of the course**
- avoid advanced methods unless explicitly requested
- support understanding, not just answer delivery

## Tech Stack

- **Streamlit**
- **Google Gemini API**
- **Firebase**
- **GitHub**

## Current Limitations

This is still an early prototype.

Current limitations include:

- repeated large-context requests to the model
- chat storage not yet optimized
- analytics still experimental
- no automated multi-course creation yet
- not designed yet for institutional-scale deployment

## Project Goal

The main goal of this project is to explore whether a **course-specific AI assistant** can support both:

- **students**, through more relevant and pedagogically aligned explanations
- **instructors**, through basic visibility into student questions and patterns

## Status

- Functional prototype
- Guest, Student, and Professor modes implemented
- Basic analytics working
- Currently being prepared for instructor feedback and early pilot presentation

## Author

Developed by **Roger Rivero**

## Note

This is an educational prototype for testing, feedback, and iterative improvement.  
It is not yet a production-ready institutional platform.