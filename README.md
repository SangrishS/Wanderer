# Wanderer
# Mumbai Travel Guide Bot

This project is a chatbot that provides travel guidance for exploring Mumbai, particularly the Churchgate area. It uses the Mistral AI API to generate responses.

## Features
- Offers unique and authentic travel suggestions.
- Provides recommendations for exploring the Churchgate area and nearby neighborhoods.
- Handles retry logic for API calls to ensure reliability.

---

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- An API key for Mistral AI

---

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/mumbai-travel-guide-bot.git
   cd mumbai-travel-guide-bot
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Linux/Mac
   venv\Scripts\activate     # For Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   - Create a `.env` file in the root directory:
     ```env
     API_KEY=your_mistral_api_key
     MODEL=ministral-8b-latest
     ```

5. Run the script:
   ```bash
   python main.py
   ```

---

## Deployment

### Using Docker

1. Build the Docker image:
   ```bash
   docker build -t mumbai-travel-guide-bot .
   ```

2. Run the Docker container:
   ```bash
   docker run -d -p 8000:8000 --env-file .env mumbai-travel-guide-bot
   ```

---

### Notes
- Ensure that your `.env` file contains valid API credentials before running the application.
- Retry logic is implemented with the `tenacity` package to handle API call failures.

---

## .env File Example
```env
API_KEY=your_mistral_api_key
MODEL=ministral-8b-latest
```

---

## .gitignore

- The `.env` file and other sensitive files are ignored from version control to protect your credentials. Refer to the `.gitignore` file in this repository.

---

## License

This project is licensed under the MIT License.

